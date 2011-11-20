#!/usr/bin/env python

from __future__ import absolute_import


class SomeClass:

    def __init__(self):
        self.val = 42

    def method(self):
        self.val += 1


some_class = SomeClass()
some_class.method()
