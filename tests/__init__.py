#
#
#

from __future__ import absolute_import, print_function, unicode_literals

from unittest2 import TestCase


class CheckerTestCase(TestCase):

    def assert_message(self, message, line, col, description):
        self.assertEquals(message.line, line)
        self.assertEquals(message.col, col)
        self.assertEquals(message.description, description)
