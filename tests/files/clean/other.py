#!/usr/bin/env python

from __future__ import division, absolute_import, print_function, \
    unicode_literals


class SomeClass:

    def __init__(self):
        self.val = 42

    def method(self):
        self.val += 1


class Valid8Name:

    def some_valid8_method(self):
        pass


some_class = SomeClass()
some_class.method()
