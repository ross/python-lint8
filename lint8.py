#!/usr/bin/env python

from __future__ import absolute_import

from optparse import OptionParser
from os.path import isdir
from sys import argv
import pep8


def setup_pep8(args):
    options = list(args)
    options.extend(['--repeat', '--show-source'])
    pep8.process_options(arglist=options)


def do_pep8(path):
    pep8.input_file(path)


def _main():
    '''
    Parse options and run lint8 checks on Python source.
    '''

    # TODO: provide a way to get at the pep8 options through lint8
    setup_pep8(['dummy'])

    for path in argv[1:]:
        do_pep8(path)


if __name__ == '__main__':
    _main()
