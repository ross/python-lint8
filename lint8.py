#!/usr/bin/env python

# TODO:
# - raw regexes
# - no print
# - logging best practices
#  - require logger and calls in each file?
#  - all execpt clauses have a log call of some sort, probably not?
# - naming (pep8)
#  - lowercase module names
#  - CapWordsClasses
#  - ExceptionClassesEndInError
#  - function_names_lower_with_underscore (same for methods and instance vars)
#  - self and cls
#  - no reserved words (open, file, ...) as var/func names
# - use of super is bad...
# - if any of __eq__, __ne__, __lt__, __le__, __gt__, __ge__, impl all

from __future__ import absolute_import

from argparse import ArgumentParser
from sys import exit, stderr
import pyflakes.checker
import ast
import pep8


class Check:

    def _parse_file(self, path):
        # TODO: source/tree cache?
        with open(path) as f:
            lines = f.readlines()
            source = ''.join(lines)
            return lines, ast.parse(source, path)


class Pep8Check(Check):

    def __init__(self):
        pep8.process_options(arglist=['--repeat', '--show-source', 'dummy'])

    def do(self, path):
        pep8.input_file(path)
        return pep8.get_count()


class PyFlakesCheck(Check):

    def do(self, path):
        # things we don't want pyflakes to tell us about, probably b/c we have
        # better checks for them
        ignored = {pyflakes.messages.ImportStarUsed: True}

        lines, tree = self._parse_file(path)
        checker = pyflakes.checker.Checker(tree, path)
        for message in checker.messages:
            if type(message) not in ignored:
                lineno = int(str(message).split(':')[1])
                line = lines[lineno - 1]
                print >> stderr, '{message}\n{line}'.format(message=message,
                                                            line=line)
        return len(checker.messages)


class AbsoluteImportCheck(Check):

    def do(self, path):
        lines, tree = self._parse_file(path)
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


class NoImportStarCheck(Check):

    def do(self, path):
        lines, tree = self._parse_file(path)
        count = 0
        # for each node
        for node in ast.walk(tree):
            # from <anything> import *
            if isinstance(node, ast.ImportFrom) and \
               node.names[0].name == '*':
                line = lines[node.lineno - 1]
                # ImportFrom nodes don't have a col_offset :(
                col_offset = line.find('*')
                print >> stderr, '{file}:{lineno}:{col_offset}: L002 use of ' \
                        'import *\n{line}{shift}^' \
                        .format(file=path, lineno=node.lineno,
                                col_offset=col_offset, line=line,
                                shift=' ' * col_offset)
                count += 1

        return count


class NoExceptEmpty(Check):

    def do(self, path):
        lines, tree = self._parse_file(path)
        count = 0
        # for each node
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler) and not node.type:
                line = lines[node.lineno - 1]
                # ExceptHandler nodes don't have a col_offset :(
                col_offset = line.find(':')
                print >> stderr, '{file}:{lineno}:{col_offset}: L003 use of ' \
                        'empty/broad except\n{line}{shift}^' \
                        .format(file=path, lineno=node.lineno,
                                col_offset=col_offset, line=line,
                                shift=' ' * col_offset)
                count += 1

        return count


class NoExceptException(Check):

    def do(self, path):
        lines, tree = self._parse_file(path)
        count = 0
        # for each node
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler) and \
               node.type.id == 'Exception':
                line = lines[node.lineno - 1]
                # ExceptHandler nodes don't have a col_offset :(
                col_offset = line.find(':')
                print >> stderr, '{file}:{lineno}:{col_offset}: L004 use of ' \
                        'empty/broad except\n{line}{shift}^' \
                        .format(file=path, lineno=node.lineno,
                                col_offset=col_offset, line=line,
                                shift=' ' * col_offset)
                count += 1

        return count


class NoPrintCheck(Check):

    def do(self, path):
        lines, tree = self._parse_file(path)
        count = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Print):
                line = lines[node.lineno - 1]
                # Print nodes don't have a col_offset :(
                col_offset = line.find('print')
                print >> stderr, '{file}:{lineno}:{col_offset}: L005 use of ' \
                        'print\n{line}{shift}^'.format(file=path,
                                                       lineno=node.lineno,
                                                       col_offset=col_offset,
                                                       line=line,
                                                       shift=' ' * col_offset)
                count += 1

        return count


def _main():
    '''
    Parse options and run lint8 checks on Python source.
    '''

    parser = ArgumentParser(description='')
    parser.add_argument('--web', '-w', default=False, action='store_true',
                        help='enable web-centric checks, no prints, '
                        'good logging practices, ...')
    parser.add_argument('paths', nargs='+')
    args = parser.parse_args()

    checks = set([Pep8Check(),
                  # TODO: provide a way to number and ignore pyflakes messages
                  PyFlakesCheck(),
                  AbsoluteImportCheck(),
                  NoImportStarCheck(),
                  NoExceptEmpty(),
                  NoExceptException()])

    if args.web:
        checks.add(NoPrintCheck())

    count = 0
    for path in args.paths:
        for check in checks:
            count += check.do(path)

    exit(1 if count else 0)


if __name__ == '__main__':
    _main()
