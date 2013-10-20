#
#
#

from __future__ import absolute_import, print_function, unicode_literals

from lint8.checks import PrintFunctionChecker
from tests import CheckerTestCase


class TestPrintFunctionChecker(CheckerTestCase):

    def test_basic(self):
        checker = PrintFunctionChecker()
        checker.cache_enabled = False

        # empty
        self.assertEquals([], checker.check('', ['']), 'empty is ok')

        # basic
        self.assertEquals([], checker.check('', ['from __future__ import '
                                                 'print_function']),
                          'basic is ok')

        # first
        self.assertEquals([], checker.check('', ['from __future__ import '
                                                 'print_function, division']),
                          'first is ok')

        # last
        self.assertEquals([], checker.check('', ['from __future__ import '
                                                 'division, print_function']),
                          'last is ok')

        # star
        self.assertEquals([], checker.check('', ['from __future__ import *']),
                          'star is ok')

        # var assignment FAIL
        result = checker.check('', ['v = 42'])
        self.assertEquals(1, len(result), 'var assignment')
        self.assert_message(result[0], 1, 0,
                            'missing from __future__ import print_function')

        # other module
        result = checker.check('', ['from other import something'])
        self.assertEquals(1, len(result), 'var assignment')
        self.assert_message(result[0], 1, 0,
                            'missing from __future__ import print_function')

        # correct module, other thing
        result = checker.check('', ['from __future__ import something'])
        self.assertEquals(1, len(result), 'var assignment')
        self.assert_message(result[0], 1, 0,
                            'missing from __future__ import print_function')
