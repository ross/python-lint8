#!/usr/bin/env python

from os.path import join

class SomeClass:

    def __init__(self): 
        self.val = 42
    
    def method(self):
        self.val += 1
        print self.val


some_class=SomeClass()
some_class.method ()
