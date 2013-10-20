#
#
#

from __future__ import absolute_import, print_function, unicode_literals

from lint8.checks import Pep8Checker
from tests import CheckerTestCase


class TestAbsoluteImportChecker(CheckerTestCase):

    def test_basic(self):
        checker = Pep8Checker()
        checker.cache_enabled = False

        self.assertEquals([], checker.check('foo.py', []), 'empty is ok')
        self.assertEquals([], checker.check('foo.py', ['']), 'empty str is ok')

        result = checker.check('foo.py', ['v = 42 \n', '\n'])
        self.assertEquals(2, len(result), 'couple errors')
        self.assertEquals('foo.py', result[0].path, 'expected path')
        self.assertEquals('W291', result[0].code, 'expected code')
        self.assert_message(result[0], 1, 6, 'trailing whitespace')
        self.assertEquals('W391', result[1].code, 'expected code')
        self.assert_message(result[1], 2, 0, 'blank line at end of file')
