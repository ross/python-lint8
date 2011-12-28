#
#
#

from __future__ import absolute_import

from lint8.checks import Registry, registry
from unittest2 import TestCase


class TestRegistry(TestCase):

    def test_global(self):
        self.assertEqual('n/a', registry.lookup(Registry))
        self.assertEqual('n/a', registry.lookup(TestCase))

        registry.register(Registry, 'Registry')

        self.assertEqual('Registry', registry.lookup(Registry))
        self.assertEqual('n/a', registry.lookup(TestCase))

        registry.register(TestCase, 'TestCase')

        self.assertEqual('Registry', registry.lookup(Registry))
        self.assertEqual('TestCase', registry.lookup(TestCase))

    def test_instance(self):
        reg = Registry()

        self.assertEqual('n/a', reg.lookup(Registry))
        self.assertEqual('n/a', reg.lookup(TestCase))

        reg.register(Registry, 'Registry')

        self.assertEqual('Registry', reg.lookup(Registry))
        self.assertEqual('n/a', reg.lookup(TestCase))

        reg.register(TestCase, 'TestCase')

        self.assertEqual('Registry', reg.lookup(Registry))
        self.assertEqual('TestCase', reg.lookup(TestCase))
