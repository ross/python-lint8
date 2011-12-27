#
#
#

from __future__ import absolute_import

from lint8.checks import FunctionNamingChecker
from tests import CheckerTestCase


class TestFunctionNamingChecker(CheckerTestCase):

    def test_basic(self):
        checker = FunctionNamingChecker()
        checker.cache_enabled = False

        self.assertEquals([], checker.check('', ['']), 'empty is ok')
        self.assertEquals([], checker.check('', ['v = 42']),
                          'assignment is ok')
        self.assertEquals([], checker.check('', ['class foo():\n',
                                                 '    pass\n']),
                          'class is ok')
        self.assertEquals([], checker.check('', ['class Foo():\n',
                                                 '    pass\n']),
                          'bad class is ok')

        self.assertEquals([], checker.check('', ['def foo():\n',
                                                 '    pass\n']), 'valid func')
        self.assertEquals([], checker.check('', ['def foo_bar():\n',
                                                 '    pass\n']),
                          'two-word valid func')
        self.assertEquals([], checker.check('', ['def foo(arg):\n',
                                                 '    pass\n']),
                          'valid with arg')
        self.assertEquals([], checker.check('', ['def _foo(object):\n',
                                                 '    pass\n']),
                          'valid with initial underscore func')
        self.assertEquals([], checker.check('', ['def foo3():\n',
                                                 '    pass\n']),
                          'valid func with number')

        result = checker.check('', ['def Foo():\n', '    pass\n'])
        self.assertEquals(1, len(result), 'initial lower parens')
        self.assert_message(result[0], 1, 4, 'invalid function name "Foo"')

        result = checker.check('', ['def Foo(arg):\n', '    pass\n'])
        self.assertEquals(1, len(result), 'initial lower parens')
        self.assert_message(result[0], 1, 4, 'invalid function name "Foo"')

        result = checker.check('', ['def fooBar():\n', '    pass\n'])
        self.assertEquals(1, len(result), 'camelCase')
        self.assert_message(result[0], 1, 4, 'invalid function name "fooBar"')

        result = checker.check('', ['def Foo_Bar():\n', '    pass\n'])
        self.assertEquals(1, len(result), 'internal underscore')
        self.assert_message(result[0], 1, 4, 'invalid function name "Foo_Bar"')
