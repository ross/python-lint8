#
#
#

from __future__ import absolute_import, print_function, unicode_literals

from lint8.checks import ClassNamingChecker
from tests import CheckerTestCase


class TestClassNamingChecker(CheckerTestCase):

    def test_basic(self):
        checker = ClassNamingChecker()
        checker.cache_enabled = False

        self.assertEquals([], checker.check('', ['']), 'empty is ok')
        self.assertEquals([], checker.check('', ['v = 42']),
                          'assignment is ok')
        self.assertEquals([], checker.check('', ['def foo():\n',
                                                 '    pass\n']),
                          'func is ok')
        self.assertEquals([], checker.check('', ['def Foo():\n',
                                                 '    pass\n']),
                          'bad func is ok')

        self.assertEquals([], checker.check('', ['class Foo:\n',
                                                 '    pass\n']), 'valid class')
        self.assertEquals([], checker.check('', ['class FooBar:\n',
                                                 '    pass\n']),
                          'two-word valid class')
        self.assertEquals([], checker.check('', ['class Foo():\n',
                                                 '    pass\n']),
                          'valid with parens class')
        self.assertEquals([], checker.check('', ['class Foo(object):\n',
                                                 '    pass\n']),
                          'valid with parent class')
        self.assertEquals([], checker.check('', ['class _Foo(object):\n',
                                                 '    pass\n']),
                          'valid with initial underscore class')

        result = checker.check('', ['class foo:\n', '    pass\n'])
        self.assertEquals(1, len(result), 'initial lower')
        self.assert_message(result[0], 1, 6, 'invalid class name "foo"')

        result = checker.check('', ['class foo():\n', '    pass\n'])
        self.assertEquals(1, len(result), 'initial lower parens')
        self.assert_message(result[0], 1, 6, 'invalid class name "foo"')

        result = checker.check('', ['class foo(object):\n', '    pass\n'])
        self.assertEquals(1, len(result), 'initial lower parens')
        self.assert_message(result[0], 1, 6, 'invalid class name "foo"')

        result = checker.check('', ['class fooBar:\n', '    pass\n'])
        self.assertEquals(1, len(result), 'camelCase')
        self.assert_message(result[0], 1, 6, 'invalid class name "fooBar"')

        result = checker.check('', ['class Foo_Bar:\n', '    pass\n'])
        self.assertEquals(1, len(result), 'internal underscore')
        self.assert_message(result[0], 1, 6, 'invalid class name "Foo_Bar"')
