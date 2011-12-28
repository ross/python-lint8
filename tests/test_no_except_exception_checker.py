#
#
#

from __future__ import absolute_import

from lint8.checks import NoExceptExceptionChecker
from tests import CheckerTestCase


class TestNoExceptExceptionChecker(CheckerTestCase):

    def test_basic(self):
        checker = NoExceptExceptionChecker()
        checker.cache_enabled = False

        self.assertEquals([], checker.check('', ['']), 'empty is ok')

        self.assertEquals([], checker.check('', ['v = 42']),
                          'assignment is ok')

        self.assertEquals([], checker.check('', ['try:\n', '    v = 42\n',
                                                 'except:\n',
                                                 '    pass\n']),
                          'empty is ok')

        self.assertEquals([], checker.check('', ['try:\n', '    v = 42\n',
                                                 'except IOError:\n',
                                                 '    pass\n']),
                          'IOError is ok')

        self.assertEquals([], checker.check('', ['try:\n', '    v = 42\n',
                                                 'except IOError, e:\n',
                                                 '    pass\n']),
                          'named is ok')

        self.assertEquals([], checker.check('', ['try:\n', '    v = 42\n',
                                                 'except (IOError, '
                                                 'AttributeError):\n',
                                                 '    pass\n']),
                          'tuple is ok')

        self.assertEquals([], checker.check('', ['try:\n', '    v = 42\n',
                                                 'except (IOError, '
                                                 'AttributeError), e:\n',
                                                 '    pass\n']),
                          'named tuple is ok')

        self.assertEquals([], checker.check('', ['try:\n', '    v = 42\n',
                                                 'except (IOError, '
                                                 'AttributeError) as e:\n',
                                                 '    pass\n']),
                          'named as tuple is ok')

        # basic fail
        result = checker.check('', ['try:\n', '    v = 42\n',
                                    'except Exception:\n', '    pass\n'])
        self.assertEquals(1, len(result), 'basic fail')
        self.assert_message(result[0], 3, 7, 'use of except Exception')

        # tuple fail first
        result = checker.check('', ['try:\n', '    v = 42\n',
                                    'except (Exception, IOError):\n',
                                    '    pass\n'])
        self.assertEquals(1, len(result), 'tuple fail first')
        self.assert_message(result[0], 3, 8, 'use of except Exception')

        # tuple fail last
        result = checker.check('', ['try:\n', '    v = 42\n',
                                    'except (IOError, Exception):\n',
                                    '    pass\n'])
        self.assertEquals(1, len(result), 'tuple fail last')
        self.assert_message(result[0], 3, 17, 'use of except Exception')

        # named tuple fail
        result = checker.check('', ['try:\n', '    v = 42\n',
                                    'except (IOError, Exception), e:\n',
                                    '    pass\n'])
        self.assertEquals(1, len(result), 'named tuple fail')
        self.assert_message(result[0], 3, 17, 'use of except Exception')
