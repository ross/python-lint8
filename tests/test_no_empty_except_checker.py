#
#
#

from __future__ import absolute_import

from lint8.checks import NoEmptyExceptChecker
from tests import CheckerTestCase

class TestChecker(CheckerTestCase):

    def test_basic(self):
        checker = NoEmptyExceptChecker()
        checker.cache_enabled = False

        self.assertEquals([], checker.check('', ['']), 'empty is ok')

        self.assertEquals([], checker.check('', ['v = 42']),
                          'assignment is ok')

        self.assertEquals([], checker.check('', ['try:\n', '    v = 42\n', 
                                                 'except Exception:\n', 
                                                 '    pass\n']), 
                          'exception is ok')

        self.assertEquals([], checker.check('', ['try:\n', '    v = 42\n', 
                                                 'except IOError:\n', 
                                                 '    pass\n']), 
                          'IOError is ok')

        # basic FAIL
        result = checker.check('', ['try:\n', '    pass\n', 'except:\n', 
                                    '    pass\n'])
        self.assertEquals(1, len(result), 'var assignment')
        self.assert_message(result[0], 3, 0, 'use of empty except')

        # indented FAIL
        result = checker.check('', ['if True:\n', '    try:\n', 
                                    '        pass\n', '    except:\n', 
                                    '        pass\n'])
        self.assertEquals(1, len(result), 'var assignment')
        self.assert_message(result[0], 4, 4, 'use of empty except')
