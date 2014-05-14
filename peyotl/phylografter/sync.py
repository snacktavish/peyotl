#!/usr/bin/env python
import codecs
import json
import stat
import time
import sys
import os
from peyotl import get_logger
_LOG = get_logger(__name__)

def get_processing_paths_from_prefix(pref,
                                     nexson_dir='.',
                                     nexson_state_db=None):
    d = {'nexson': os.path.abspath(os.path.join(nexson_dir, 'study', pref, pref + '.json')),
         'nexson_state_db': nexson_state_db,
         'study': pref,
         }
    if d['nexson_state_db'] is None:
        d['nexson_state_db'] = os.path.abspath(os.path.join(nexson_dir, '.sync_status.json')), # stores the state of this repo. *very* hacky primitive db.
    return d

def get_default_dir_dict(top_level=None):
    r = '.' if top_level is None else top_level
    t = os.path.abspath(r)
    d = {'nexson_dir': t,
         'nexson_state_db': os.path.join(t, '.sync_status.json'), # stores the state of this repo. *very* hacky primitive db.
        }
    return d


def get_previous_list_of_dirty_nexsons(dir_dict):
    '''Returns the previous list of studies to be fetch and dict that contains that list and timestamps.
    The dict will be populated from the filepath `dir_dict['nexson_state_db']` if that entry is not 
    found then a default dict of no studies and old timestamps will be returned.
    '''
    filename = dir_dict['nexson_state_db']
    if os.path.exists(filename):
        old = json.load(codecs.open(filename, 'rU', encoding='utf-8'))
    else:
        old = {'from': '2010-01-01T00:00:00',
               'to': '2010-01-01T00:00:00',
               'studies': []
        }
    return old['studies'], old

def get_list_of_dirty_nexsons(dir_dict, phylografter):
    '''Returns a pair: the list of studies that need to be fetched from phylografter
    and a dict that can be serialized to disk in .sync_status.json to cache the details
    of the last call to phylografter's study/modified_list service.

    If PHYLOGRAFTER_DOMAIN_PREF is in the env, it will provide the domain the default
        is the main phylografter site.
    '''
    filename = dir_dict['nexson_state_db']
    slist, old = get_previous_list_of_dirty_nexsons(dir_dict)
    new_resp = phylografter.get_modified_list(old['to'])
    ss = set(new_resp['studies'] + old['studies'])
    sl = list(ss)
    sl.sort()
    new_resp['studies'] = sl
    new_resp['from'] = old['from']
    store_state_JSON(new_resp, filename)
    to_refresh = list(new_resp['studies'])
    return to_refresh, new_resp


def open_for_group_write(fp, mode):
    '''Open with mode=mode and permissions '-rw-rw-r--' group writable is 
    the default on some systems/accounts, but it is important that it be present on our deployment machine
    '''
    d = os.path.split(fp)[0]
    if not os.path.exists(d):
        os.makedirs(d)
    o = codecs.open(fp, mode, encoding='utf-8')
    o.flush()
    os.chmod(fp, stat.S_IRGRP | stat.S_IROTH | stat.S_IRUSR | stat.S_IWGRP | stat.S_IWUSR)
    return o

def store_state_JSON(s, fp):
    tmpfilename = fp + '.tmpfile'
    td = open_for_group_write(tmpfilename, 'w')
    try:
        json.dump(s, td, sort_keys=True, indent=0)
    finally:
        td.close()
    os.rename(tmpfilename, fp) #atomic on POSIX

def download_nexson_from_phylografter(phylografter,
                                      paths,
                                      download_db,
                                      lock_policy):
    nexson_path = paths['nexson']
    lockfile = nexson_path + '.lock'
    was_locked, owns_lock = lock_policy.wait_for_lock(lockfile)
    try:
        if not owns_lock:
            return None
        study = paths['study']
        er = phylografter.get_study(study)
        should_write = False
        if not os.path.exists(nexson_path):
            should_write = True
        else:
            prev_content = json.load(codecs.open(nexson_path, 'rU', encoding='utf-8'))
            if prev_content != er:
                should_write = True
        if should_write:
            store_state_JSON(er, nexson_path)
        if download_db is not None:
            try:
                download_db['studies'].remove(int(study))
            except:
                warn('%s not in %s' % (study, paths['nexson_state_db']))
                pass
            else:
                store_state_JSON(download_db, paths['nexson_state_db'])
    finally:
        lock_policy.remove_lock()
    return er

def record_sha_for_study(phylografter,
                         paths,
                         download_db,
                         merged_studies,
                         unmerged_study_to_sha,
                         last_merged_sha):
    '''So that the edit history of a file is accurate, we need to store the new parent SHA for any
    future updates. For studies that merged to master, this will be the last_merged_sha. 
    Other studies should be in the unmerged_study_to_sha dict
    '''
def sync_from_phylografter2nexson_api(
        cfg_file_paths,
        to_download=None
        lock_policy=None,
        api_wrapper=None,
        sleep_between_downloads=None):
    '''Returns the # of studies updated from phylografter to the "NexSON API"

    `cfg_file_paths` should be a dict with:
        'nexson_dir': directory that will be the parent of the nexson files
         'nexson_state_db': a JSON file to hold the state of the phylografter <-> API interaction
    `to_download` can be a list of study IDs (if the state is not to be preserved). If this call
        uses the history in `cfg_file_paths['nexson_state_db']` then this should be None.
    `lock_policy` can usually be None, it specifies how the nexson_state_db is to be locked for thread safety
    `api_wrapper` will be the default APIWrapper() if None
    `sleep_between_downloads` is the number of seconds to sleep between calls (to avoid stressing phylografter.)

    env vars:
        SLEEP_BETWEEN_DOWNLOADS_TIME, SLEEP_FOR_LOCK_TIME, and MAX_NUM_SLEEP_IN_WAITING_FOR_LOCK are checked
        if lock_policy and sleep_between_downloads
    '''
    if api_wrapper is None:
        from peyotl.api import APIWrapper
        api_wrapper = APIWrapper()
    if to_download is None:
        to_download, download_db = get_list_of_dirty_nexsons(dd, api_wrapper.phylografter)
        if not to_download:
            return 0
    else:
        download_db = None
    if sleep_between_downloads is None:
        sleep_between_downloads = float(os.environ.get('SLEEP_BETWEEN_DOWNLOADS_TIME', 0.5))
    if lock_policy is None:
        from peyotl.utility import LockPolicy
        lock_policy = LockPolicy(sleep_time=float(os.environ.get('SLEEP_FOR_LOCK_TIME', 0.05)),
                                 max_num_sleep=int(os.environ.get('MAX_NUM_SLEEP_IN_WAITING_FOR_LOCK', 100)))
    num_downloaded = len(to_download)
    studies_with_final_sha = set()
    unmerged_study_to_sha = {}
    last_merged_sha = None
    doc_store_api = api_wrapper.doc_store
    phylografter = api_wrapper.phylografter
    try:
        while len(to_download) > 0:
            n = to_download.pop(0)
            study = str(n)
            paths = get_processing_paths_from_prefix(study, **cfg_file_paths)
            nexson = download_nexson_from_phylografter(phylografter,
                                                       paths,
                                                       download_db,
                                                       lock_policy)
            if nexson is None:
                raise RuntimeError('NexSON "{}" could not be refreshed\n'.format(paths['nexson']))
            try:
                namespaced_id = 'pg_{s:d}'.format(s=study)
                parent_sha = find_parent_sha_for_phylografter_nexson(nexson, download_db)
                put_response = api_wrapper.put_study(study_id=namespaced_id, nexson=nexson, starting_commit_sha=parent_sha)
                assert put_response['error'] == '0'
            except:
                download_db['studies'].add(int(study))
                # act as if the study was not downloaded, so that when we try
                #   again we won't skip this study
                store_state_JSON(download_db, paths['nexson_state_db'])
                raise
            else:
                if put_response['merge_needed']:
                    unmerged_study_to_sha[study] = put_response['sha']
                else:
                    studies_with_final_sha.add(study)
                    last_merged_sha = put_response['sha']
            if len(to_download) > 0:
                time.sleep(sleep_between_downloads)
    finally:
        record_sha_for_study(phylografter,
                             download_db,
                             studies_with_final_sha,
                             unmerged_study_to_sha,
                             last_merged_sha)
    return num_downloaded

if __name__ == '__main__':
    if '-h' in sys.argv:
        sys.stderr.write('''sync.py is a short-term hack.

It stores info about the last communication with phylografter in .to_download.json
Based on this info, it tries to download as few studies as possible to make 
the NexSONs in treenexus/studies/#/... match the export from phylografter.

   -h gives this help message.

If other arguments aree supplied, it should be the study #'s to be downloaded.
''')
        sys.exit(0)

    dd = get_default_dir_dict()
    if len(sys.argv) > 1:
        to_download = sys.argv[1:]
    else:
        to_download = None
    sync_from_phylografter2nexson_api(cfg_file_paths=dd, to_download=to_download)
