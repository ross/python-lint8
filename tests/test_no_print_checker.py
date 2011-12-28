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
