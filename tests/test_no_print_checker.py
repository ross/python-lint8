#
#
#

from __future__ import absolute_import

from lint8.checks import NoPrintChecker
from tests import CheckerTestCase


class TestNoPrintChecker(CheckerTestCase):

    def test_basic(self):
        checker = NoPrintChecker()
        checker.cache_enabled = False

        self.assertEquals([], checker.check('', ['']), 'empty is ok')

        self.assertEquals([], checker.check('', ['v = 42']),
                          'assignment is ok')

        self.assertEquals([], checker.check('', ['v = "print"']),
                          'in string is ok')

        result = checker.check('', ['print "hello world"'])
        self.assertEquals(1, len(result), 'as special')
        self.assert_message(result[0], 1, 0, 'use of print')

        result = checker.check('', ['print("hello world")'])
        self.assertEquals(1, len(result), 'as function')
        self.assert_message(result[0], 1, 0, 'use of print')

        result = checker.check('', ['if True:\n',
                                    '    print("hello world")\n'])
        self.assertEquals(1, len(result), 'as function')
        self.assert_message(result[0], 2, 4, 'use of print')

        result = checker.check('', ['print "hello world" \n',
                                    'print("another world")'])
        self.assertEquals(2, len(result), 'as function')
        self.assert_message(result[0], 1, 0, 'use of print')
        self.assert_message(result[1], 2, 0, 'use of print')

    def test_with_future(self):
        checker = NoPrintChecker()
        checker.cache_enabled = False

        future = 'from __future__ import print_function\n'

        self.assertEquals([], checker.check('', [future, 'v = "print"']),
                          'in string is ok')

        result = checker.check('', [future, 'print("hello world")'])
        self.assertEquals(1, len(result), 'as function')
        self.assert_message(result[0], 2, 0, 'use of print')

        result = checker.check('', [future,
                                    'if True:\n',
                                    '    print("hello world")\n'])
        self.assertEquals(1, len(result), 'as function')
        self.assert_message(result[0], 3, 4, 'use of print')
