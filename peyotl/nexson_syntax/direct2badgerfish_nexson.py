#!/usr/bin/env python
'Direct2BadgerfishNexson class'
from peyotl.nexson_syntax.helper import NexsonConverter, \
                                        _add_redundant_about, \
                                        _add_value_to_dict_bf, \
                                        _coerce_literal_val_to_primitive, \
                                        _convert_hbf_meta_val_for_xml, \
                                        _get_index_list_of_values, \
                                        _index_list_of_values, \
                                        BADGER_FISH_NEXSON_VERSION, \
                                        _LITERAL_META_PAT, \
                                        _RESOURCE_META_PAT

from peyotl.utility import get_logger
_LOG = get_logger(__name__)


class Direct2BadgerfishNexson(NexsonConverter):
    '''Conversion of the direct form of honeybadgerfish 
    HoneyBadgerFish (v 1.0) to "raw" Badgerfish + phylografter tweaks
    This is a dict-to-dict in-place conversion. No serialization is included.
    '''
    def __init__(self, conv_cfg):
        NexsonConverter.__init__(self, conv_cfg)
        self.remove_old_structs = getattr(conv_cfg, 'remove_old_structs', True)

    def _recursive_convert_list(self, obj):
        for el in obj:
            if isinstance(el, dict):
                self._recursive_convert_dict(el)


    def _recursive_convert_dict(self, obj):
        _add_redundant_about(obj) # rule 10...
        meta_list = []
        to_del = set()
        for k, v in obj.items():
            if k.startswith('^'):
                to_del.add(k)
                converted = _convert_hbf_meta_val_for_xml(k[1:], v)
                if isinstance(converted, list):
                    meta_list.extend(converted)
                else:
                    meta_list.append(converted)
            if isinstance(v, dict):
                self._recursive_convert_dict(v)
            elif isinstance(v, list):
                self._recursive_convert_list(v)
        for k in to_del:
            del obj[k]
        if meta_list:
            m = obj.get('meta')
            if m is None:
                obj['meta'] = meta_list
            elif isinstance(m, list):
                m.extend(meta_list)
            else:
                obj['meta'] = [m] + meta_list

    def _single_el_list_to_dicts(self, obj, tag, child_tag=None, grand_child_tag=None):
        el = obj.get(tag)
        if el:
            if isinstance(el, list):
                if len(el) == 1:
                    as_list = [el]
                    if child_tag is None:
                        obj[tag] = el[0]
                        return
                else:
                    as_list = el
            else:
                as_list = [el]
            if child_tag is not None:
                for sub in as_list:
                    self._single_el_list_to_dicts(sub, tag=child_tag, child_tag=grand_child_tag)

    def convert(self, obj):
        '''Takes a dict corresponding to the honeybadgerfish JSON blob of the 1.0.* type and
        converts it to BY_ID_HONEY_BADGERFISH version. The object is modified in place
        and returned.
        '''
        if self.pristine_if_invalid:
            raise NotImplementedError('pristine_if_invalid option is not supported yet')

        nex = obj.get('nex:nexml') or obj['nexml']
        assert(nex)
        self._recursive_convert_dict(nex)
        nex['@nexml2json'] = str(BADGER_FISH_NEXSON_VERSION)
        self._single_el_list_to_dicts(nex, 'otus')
        self._single_el_list_to_dicts(nex, 'otus', 'otu')
        self._single_el_list_to_dicts(nex, 'trees')
        self._single_el_list_to_dicts(nex, 'trees', 'tree')
        self._single_el_list_to_dicts(nex, 'trees', 'tree', 'node')
        self._single_el_list_to_dicts(nex, 'trees', 'tree', 'edge')

        return obj
