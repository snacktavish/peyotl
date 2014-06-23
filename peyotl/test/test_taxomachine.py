#! /usr/bin/env python
from peyotl.api import Taxomachine
from peyotl.test.support.pathmap import get_test_ot_service_domains
from peyotl.utility import get_logger
import unittest

_LOG = get_logger(__name__)

class TestTaxomachine(unittest.TestCase):
    def setUp(self):
        d = get_test_ot_service_domains()
        self.taxomachine = Taxomachine(d)
    def testContexts(self):
        cdict = self.taxomachine.contexts()
        self.assertTrue('PLANTS' in cdict)
    def testBogusName(self):
        resp = self.taxomachine.TNRS('bogustaxonomicname')
        self.assertEqual(resp['results'], [])
    def testSkunkName(self):
        name = u'Mephitis mephitis'
        resp = self.taxomachine.TNRS(name, 'Mammals')
        self.assertEqual(len(resp['results']), 1)
        el = resp['results'][0]['matches'][0]
        self.assertEqual(el['matched_name'], name)
    def testSkunkNameExact(self):
        name = u'Mephitis mephitis'
        resp = self.taxomachine.TNRS(name, 'Mammals')
        self.assertFalse(resp['results'][0]['matches'][0]['is_approximate_match'])
    @unittest.skip('taxomachine bug https://github.com/OpenTreeOfLife/taxomachine/issues/52')
    def testHomonymName(self):
        name = 'Nandina'
        resp = self.taxomachine.TNRS(name)
        self.assertEqual(len(resp['results'][0]['matches']), 2)
        resp = self.taxomachine.TNRS(name, 'Animals')
        self.assertEqual(len(resp['results'][0]['matches']), 1)
        resp = self.taxomachine.TNRS(name, 'Flowering plants')
        self.assertEqual(len(resp['results'][0]['matches']), 1)

if __name__ == "__main__":
    unittest.main(verbosity=5)
