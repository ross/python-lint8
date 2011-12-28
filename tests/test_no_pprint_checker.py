#
#
#

from __future__ import absolute_import

from lint8.checks import NoPprintChecker
from tests import CheckerTestCase


class TestNoPrintChecker(CheckerTestCase):

    def test_basic(self):
        checker = NoPprintChecker()
        checker.cache_enabled = False

        self.assertEquals([], checker.check('', ['']), 'empty is ok')

        self.assertEquals([], checker.check('', ['v = 42']),
                          'assignment is ok')

        self.assertEquals([], checker.check('', ['v = "print"']),
                          'in string is ok')

        self.assertEquals([], checker.check('', ['import sys']), 'other is ok')

        self.assertEquals([], checker.check('', ['import os, sys']),
                          'multi-other is ok')

        result = checker.check('', ['import pprint'])
        self.assertEquals(1, len(result), 'import pprint')
        self.assert_message(result[0], 1, 7, 'import of pprint')

        result = checker.check('', ['from pprint import pprint'])
        self.assertEquals(1, len(result), 'from pprint import pprint')
        self.assert_message(result[0], 1, 5, 'import of pprint')

        result = checker.check('', ['from pprint import other'])
        self.assertEquals(1, len(result), 'from pprint import other')
        self.assert_message(result[0], 1, 5, 'import of pprint')

        result = checker.check('', ['import pprint, sys, path'])
        self.assertEquals(1, len(result), 'import multi-first')
        self.assert_message(result[0], 1, 7, 'import of pprint')

        result = checker.check('', ['import sys, os, pprint'])
        self.assertEquals(1, len(result), 'import multi-last')
        self.assert_message(result[0], 1, 16, 'import of pprint')
