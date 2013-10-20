#
#
#

from __future__ import absolute_import, print_function, unicode_literals

from lint8 import Checker
from os.path import dirname, join
from unittest2 import TestCase

FILES_DIR = join(dirname(__file__), 'files')


class TestChecker(TestCase):

    def test_clean(self):
        checker = Checker()

        self.assertEquals(0, checker.process([join(FILES_DIR, 'clean',
                                                   'simple.py')]))

        self.assertEquals(0, checker.process([join(FILES_DIR, 'clean',
                                                   'other.py')]))

        self.assertEquals(0, checker.process([join(FILES_DIR, 'clean',
                                                   'exceptions.py')]))

        self.assertEquals(0, checker.process([join(FILES_DIR, 'clean')]))

    def test_bad(self):
        checker = Checker()

        checker.process([join(FILES_DIR, 'bad', 'simple.py')])
        self.assertEquals(10, checker.process([join(FILES_DIR, 'bad',
                                                    'simple.py')]))

        self.assertEquals(11, checker.process([join(FILES_DIR, 'bad',
                                                    'other.py')]))

        self.assertEquals(4, checker.process([join(FILES_DIR, 'bad',
                                                   'exceptions.py')]))

        self.assertEquals(25, checker.process([join(FILES_DIR, 'bad')]))

    def test_web(self):
        checker = Checker(web=True)

        self.assertEquals(11, checker.process([join(FILES_DIR, 'bad',
                                                    'simple.py')]))

        self.assertEquals(14, checker.process([join(FILES_DIR, 'bad',
                                                    'other.py')]))

        self.assertEquals(4, checker.process([join(FILES_DIR, 'bad',
                                                   'exceptions.py')]))

        self.assertEquals(29, checker.process([join(FILES_DIR, 'bad')]))

    def test_ignore(self):
        checker = Checker(ignores=['W291'])
        self.assertEquals(9, checker.process([join(FILES_DIR, 'bad',
                                                   'simple.py')]))

        checker = Checker(ignores=['W291', 'L001'])
        self.assertEquals(8, checker.process([join(FILES_DIR, 'bad',
                                                   'simple.py')]))

        checker = Checker(ignores=['W291', 'L001', 'F001'])
        self.assertEquals(7, checker.process([join(FILES_DIR, 'bad',
                                                   'simple.py')]))

        # ignore unknown pyflakes msg
        checker = Checker(ignores=['W291', 'L001', 'F001', 'F999'])
        self.assertEquals(7, checker.process([join(FILES_DIR, 'bad',
                                                   'simple.py')]))

    def test_nonexistent_file(self):
        checker = Checker()

        with self.assertRaises(IOError):
            checker.process([join('some', 'path', 'to', 'nowhere')])

    def test_checker_blowup(self):
        checker = Checker()

        class Blowup:

            def check(self, *args, **kwargs):
                raise Exception('boom')

        checker.checkers = [Blowup()]

        with self.assertRaises(Exception) as cm:
            checker.process([join(FILES_DIR, 'bad', 'simple.py')])
        self.assertEquals('boom', str(cm.exception))
