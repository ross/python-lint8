#!/usr/bin/env python

from __future__ import division
from pprint import pprint
from pprint import pprint as fooprint

from os.path import join

class SomeClass:

    def __init__(self): 
        self.val = 42
    
    def method(self):
        self.val += 1
        print self.val
        pprint(self)
        fooprint(self)


class otherClass:
    pass


class Another_Class:
    pass


some_class=SomeClass()
some_class.method ()
