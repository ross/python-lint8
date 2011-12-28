#!/usr/bin/env python

# TODO:
# - real paths
# - support processing strings
# - listing of codes
# - raw regexes
# - logging best practices
#  - require logger and calls in each file?
#  - all execpt clauses have a log call of some sort, probably not?
# - naming (pep8)
#  - lowercase module names
#  - CapWordsClasses
#  - ExceptionClassesEndInError
#  - self and cls
#  - no reserved words (open, file, ...) as var/func names
# - use of super is bad...
# - calls to parent methods, at least for __init__?
# - if any of __eq__, __ne__, __lt__, __le__, __gt__, __ge__, impl all
# - check for pdb, ipdbs
# - no exec
# - no manual file concatenation
# - xrange over range
# - use utf8 (or just coding) '# -*- coding: UTF-8 -*-'
# - division?
# - multable default values for args foo=[]
# - tertiaray if/else (ugly)
# - prefer .format over %
# - % of (public) things with docstring...
# - no "pass" only functions
# - alphabetized imports
# http://docs.python.org/howto/doanddont.html
# http://www.fantascienza.net/leonardo/ar/python_best_practices.html
# http://www.ferg.org/projects/python_gotchas.html

from __future__ import absolute_import

from argparse import ArgumentParser
from lint8 import Checker
from sys import exit, stderr


def _main():
    '''
    Parse options and run lint8 checks on Python source.
    '''

    parser = ArgumentParser(description='')
    parser.add_argument('--ignore', default='',
                        help='skip messages of specified types (e.g. '
                        'L003,E201,F100)')
    parser.add_argument('--web', '-w', default=False, action='store_true',
                        help='enable web-centric checks, no prints, '
                        'good logging practices, ...')
    parser.add_argument('paths', nargs='+')
    args = parser.parse_args()

    ignores = args.ignore.split(',') if args.ignore else []

    checker = Checker(ignores=ignores, web=args.web)
    count = checker.process(args.paths)
    for message in checker.messages:
        print >> stderr, message
    exit(count)


if __name__ == '__main__':
    _main()
