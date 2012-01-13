#!/usr/bin/env python
# that's ^ kinda ugly :)

from __future__ import absolute_import

from lint8 import Checker
from sys import stderr

checker = Checker()

count = checker.process(['./lint8/', './tests/', 'test.py'],
                        ['\./tests/files/'])
for message in checker.messages:
    print >> stderr, message
exit(count)
