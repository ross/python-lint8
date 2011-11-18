#!/usr/bin/env python

from __future__ import absolute_import

from optparse import OptionParser
from os.path import isdir
from sys import argv, exit, stderr
import ast
import pep8


def setup_pep8(args):
    options = list(args)
    options.extend(['--repeat', '--show-source'])
    pep8.process_options(arglist=options)


def do_pep8(path):
    pep8.input_file(path)
    return pep8.get_count()


def check_absolute_import(path):
    # TODO: source/tree cache?
    source = open(path).read()
    tree = ast.parse(source, path)
    first = tree.body[0]
    # from __future__
    if isinstance(first, ast.ImportFrom) and \
       first.module == '__future__':
        # look though the things being imported for absolute_import
        for name in first.names:
            if name.name == 'absolute_import' or name.name == '*':
                # found it so no error
                return 0

    print >> stderr, '{0}:1: L001 file missing "from __future__ import ' \
            'absolute_import"\n'.format(path)
    # if we're here we didn't find what we're looking for
    return 1


def _main():
    '''
    Parse options and run lint8 checks on Python source.
    '''

    # TODO: provide a way to get at the pep8 options through lint8
    setup_pep8(['dummy'])

    count = 0

    for path in argv[1:]:
        count += do_pep8(path)
        count += check_absolute_import(path)

    exit(1 if count else 0)


if __name__ == '__main__':
    _main()
