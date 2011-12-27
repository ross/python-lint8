#
#
#

from __future__ import absolute_import

from lint8.checks import AstChecker
from unittest2 import TestCase


class TestAstChecker(TestCase):

    def test_caching(self):
        checker = AstChecker()

        self.assertTrue(checker.cache_enabled)

        # empty
        empty = checker._parse('path', [])
        # cached empty
        cached = checker._parse('path', ['v = 32'])
        self.assertEqual(empty, cached)

        # disable cache
        checker.cache_enabled = False
        not_cached = checker._parse('path', ['v = 32'])
        self.assertNotEqual(empty, not_cached)
