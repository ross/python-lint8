#
#
#

from __future__ import absolute_import, print_function, unicode_literals

from lint8.checks import PyFlakesChecker
from tests import CheckerTestCase


class TestAbsoluteImportChecker(CheckerTestCase):

    def test_basic(self):
        checker = PyFlakesChecker()
        checker.cache_enabled = False

        self.assertEquals([], checker.check('foo.py', []), 'empty is ok')
        self.assertEquals([], checker.check('foo.py', ['']), 'empty str is ok')

        self.assertEquals([], checker.check('foo.py',
                                            ['from os.path import *\n']),
                          'import * is ok')

        result = checker.check('foo.py', ['import os.path\n'])
        self.assertEquals(1, len(result), 'one error')
        self.assertEquals('foo.py', result[0].path, 'expected path')
        self.assert_message(result[0], 1, None, "'os' imported but unused")

        result = checker.check('foo.py', ['def foo():\n', '    pass\n',
                                          'if True:\n', '    def foo():\n',
                                          '        pass\n'])
        self.assertEquals(1, len(result), 'one error')
        self.assert_message(result[0], 4, None,
                            "redefinition of unused 'foo' from line 1")
