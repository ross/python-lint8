#
#
#

from __future__ import absolute_import, print_function, unicode_literals

from lint8.checks import UnicodeLiteralsChecker
from tests import CheckerTestCase


class TestUnicodeLiteralsChecker(CheckerTestCase):

    def test_basic(self):
        checker = UnicodeLiteralsChecker()
        checker.cache_enabled = False

        # empty
        self.assertEquals([], checker.check('', ['']), 'empty is ok')

        # basic
        self.assertEquals([], checker.check('', ['from __future__ import '
                                                 'unicode_literals']),
                          'basic is ok')

        # first
        self.assertEquals([], checker.check('', ['from __future__ import '
                                                 'unicode_literals, division']),
                          'first is ok')

        # last
        self.assertEquals([], checker.check('', ['from __future__ import '
                                                 'division, unicode_literals']),
                          'last is ok')

        # star
        self.assertEquals([], checker.check('', ['from __future__ import *']),
                          'star is ok')

        # var assignment FAIL
        result = checker.check('', ['v = 42'])
        self.assertEquals(1, len(result), 'var assignment')
        self.assert_message(result[0], 1, 0,
                            'missing from __future__ import unicode_literals')

        # other module
        result = checker.check('', ['from other import something'])
        self.assertEquals(1, len(result), 'var assignment')
        self.assert_message(result[0], 1, 0,
                            'missing from __future__ import unicode_literals')

        # correct module, other thing
        result = checker.check('', ['from __future__ import something'])
        self.assertEquals(1, len(result), 'var assignment')
        self.assert_message(result[0], 1, 0,
                            'missing from __future__ import unicode_literals')
