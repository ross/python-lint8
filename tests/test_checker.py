#
#
#

from __future__ import absolute_import

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
        self.assertEquals(7, checker.process([join(FILES_DIR, 'bad',
                                                   'simple.py')]))

        self.assertEquals(7, checker.process([join(FILES_DIR, 'bad',
                                                   'other.py')]))

        # TODO: this should be 4 b/c of tuples w/Exception
        self.assertEquals(2, checker.process([join(FILES_DIR, 'bad',
                                                   'exceptions.py')]))

        self.assertEquals(16, checker.process([join(FILES_DIR, 'bad')]))

    def test_web(self):
        checker = Checker(web=True)

        self.assertEquals(8, checker.process([join(FILES_DIR, 'bad',
                                                   'simple.py')]))

        self.assertEquals(8, checker.process([join(FILES_DIR, 'bad',
                                                   'other.py')]))

        self.assertEquals(2, checker.process([join(FILES_DIR, 'bad',
                                                   'exceptions.py')]))

        self.assertEquals(18, checker.process([join(FILES_DIR, 'bad')]))


    def test_ignore(self):
        checker = Checker(ignore=['W291'])
        self.assertEquals(6, checker.process([join(FILES_DIR, 'bad',
                                                   'simple.py')]))

        checker = Checker(ignore=['W291', 'L001'])
        self.assertEquals(5, checker.process([join(FILES_DIR, 'bad',
                                                   'simple.py')]))

        checker = Checker(ignore=['W291', 'L001', 'F001'])
        self.assertEquals(4, checker.process([join(FILES_DIR, 'bad',
                                                   'simple.py')]))

        # ignore unknown pyflakes msg
        checker = Checker(ignore=['W291', 'L001', 'F001', 'F999'])
        self.assertEquals(4, checker.process([join(FILES_DIR, 'bad',
                                                   'simple.py')]))


