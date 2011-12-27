#
#
#

from __future__ import absolute_import

from lint8.checks import NoImportStarChecker
from tests import CheckerTestCase


class TestNoImportStarChecker(CheckerTestCase):

    def test_basic(self):
        checker = NoImportStarChecker()
        checker.cache_enabled = False

        # empty
        self.assertEquals([], checker.check('', ['']), 'empty is ok')

        # assignment
        self.assertEquals([], checker.check('', ['v = 42']), 'assign is ok')

        # import
        self.assertEquals([], checker.check('', ['import sys']),
                          'import is ok')

        # import * not ok
        result = checker.check('', ['from sys import *'])
        self.assertEquals(1, len(result), 'import start fails')
        self.assert_message(result[0], 1, 16, 'use of import *')
