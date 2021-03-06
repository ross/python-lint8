#
#
#

from __future__ import absolute_import, print_function, unicode_literals

from argparse import ArgumentParser
from lint8 import Checker
from sys import exit, stderr


def main():
    '''
    Parse options and run lint8 checks on Python source.
    '''

    parser = ArgumentParser(description='')
    parser.add_argument('--ignore', default='',
                        help='skip messages of specified types (e.g. '
                        'L003,E201,F100)')
    parser.add_argument('--exclude', default='',
                        help='exclude files matching patterns (e.g. '
                        'some_file,bad_.+)')
    parser.add_argument('--web', '-w', default=False, action='store_true',
                        help='enable web-centric checks, no prints, '
                        'good logging practices, ...')
    parser.add_argument('paths', nargs='+')
    args = parser.parse_args()

    ignores = args.ignore.split(',') if args.ignore else []
    excludes = args.exclude.split(',') if args.exclude else []

    checker = Checker(ignores=ignores, web=args.web)
    count = checker.process(args.paths, excludes)
    for message in checker.messages:
        print(message, file=stderr)
    exit(count)
