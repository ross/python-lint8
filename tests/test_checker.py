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

        self.assertEquals(0, checker.process([join(FILES_DIR, 'clean')]))

    def test_bad(self):
        checker = Checker()

        self.assertEquals(8, checker.process([join(FILES_DIR, 'bad', 
                                                   'simple.py')]))

        self.assertEquals(7, checker.process([join(FILES_DIR, 'bad', 
                                                   'other.py')]))

        self.assertEquals(15, checker.process([join(FILES_DIR, 'bad')]))

    def test_web(self):
        checker = Checker(web=True)

        self.assertEquals(9, checker.process([join(FILES_DIR, 'bad', 
                                                   'simple.py')]))

        self.assertEquals(8, checker.process([join(FILES_DIR, 'bad', 
                                                   'other.py')]))

        self.assertEquals(17, checker.process([join(FILES_DIR, 'bad')]))
