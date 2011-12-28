#
#
#

from __future__ import absolute_import

from lint8.checks import Message
from unittest2 import TestCase


class TestMessage(TestCase):

    def test_basic(self):
        msg = Message('path', 42, 0, 'code', 'description', 'snippet')
        self.assertEquals('''path:42:0 code description\nsnippet\n^''',
                          str(msg))

        msg = Message('path', 42, 2, 'code', 'description', 'snippet')
        self.assertEquals('''path:42:2 code description\nsnippet\n  ^''',
                          str(msg))

        msg = Message('path', 42, None, 'code', 'description', 'snippet')
        self.assertEquals('''path:42: code description\nsnippet\n''',
                          str(msg))

        self.assertEquals('<Message code, path:42>', msg.__repr__(), 'repr')
