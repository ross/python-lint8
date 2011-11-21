#!/usr/bin/env python

# TODO:
# - real paths
# - support processing strings
# - listing of codes
# - raw regexes
# - no pprint
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
# http://docs.python.org/howto/doanddont.html
# http://www.fantascienza.net/leonardo/ar/python_best_practices.html
# http://www.ferg.org/projects/python_gotchas.html

from __future__ import absolute_import

from argparse import ArgumentParser
from os import walk
from os.path import isdir, join
from sys import exit, stderr
import pyflakes.checker
import ast
import pep8

check_counter = 0


class Check:
    cache = {}

    def __init__(self, ignore=[]):
        pass

    def _parse_file(self, path):
        # TODO: source/tree cache?
        with open(path) as f:
            lines = f.readlines()
            source = ''.join(lines)
            return lines, ast.parse(source, path)


class Pep8Check(Check):

    def __init__(self, ignore=[]):
        Check.__init__(self, ignore=ignore)
        arglist = ['--repeat', '--show-source']
        if ignore:
            # we only care about codes E and W
            arglist.append('--ignore')
            arglist.append(','.join(filter(lambda code: code[0] == 'E' or \
                                           code[0] == 'W', ignore)))
        arglist.append('dummy')
        pep8.process_options(arglist=arglist)

        def message(text):
            print >> stderr, text

        pep8.message = message

    def do(self, path):
        lines, tree = self._parse_file(path)
        checker = pep8.Checker(path, lines=lines)
        return checker.check_all()


class PyFlakesCheck(Check):
    msg_to_code = {}
    code_to_msg = {}

    # we have our own check for pyflakes.messages.ImportStarUsed,
    for code, msg in enumerate((pyflakes.messages.UnusedImport,
                                pyflakes.messages.RedefinedWhileUnused,
                                pyflakes.messages.ImportShadowedByLoopVar,
                                pyflakes.messages.UndefinedName,
                                pyflakes.messages.UndefinedExport,
                                pyflakes.messages.UndefinedLocal,
                                pyflakes.messages.DuplicateArgument,
                                pyflakes.messages.RedefinedFunction,
                                pyflakes.messages.LateFutureImport,
                                pyflakes.messages.UnusedVariable)):
        code = 'F{:=03}'.format(code + 1)
        msg_to_code[msg] = code
        code_to_msg[code] = msg

    def __init__(self, ignore=[]):
        for code in ignore:
            if code[0] == 'F':
                try:
                    msg = self.code_to_msg[code]
                    # removing from the lookup will ignore messages of this
                    # type
                    del self.msg_to_code[msg]
                except KeyError:
                    pass

    def do(self, path):
        lines, tree = self._parse_file(path)
        checker = pyflakes.checker.Checker(tree, path)
        for message in checker.messages:
            type_ = type(message)
            if type_ in self.msg_to_code:
                code = self.msg_to_code[type_]
                lineno = int(str(message).split(':')[1])
                line = lines[lineno - 1]
                msg = message.message % message.message_args
                print >> stderr, '{file}:{lineno}: {code} {message}\n{line}' \
                        .format(file=path, lineno=message.lineno, code=code,
                                message=msg, line=line)

        return len(checker.messages)


class CodedCheck(Check):

    def __init__(self, ignore=[]):
        Check.__init__(self, ignore=ignore)
        self.skip = ignore.count(self.code) > 0

    def do(self, path):
        if self.skip:
            return 0
        return self._do(path)


class AbsoluteImportCheck(CodedCheck):
    global check_counter
    check_counter += 1
    code = 'L{:=03}'.format(check_counter)

    def _do(self, path):
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

        print >> stderr, '{file}:1: {code} file missing "from __future__ ' \
                'import absolute_import"\n'.format(file=path, code=self.code)
        # if we're here we didn't find what we're looking for
        return 1


class NoImportStarCheck(CodedCheck):
    global check_counter
    check_counter += 1
    code = 'L{:=03}'.format(check_counter)

    def _do(self, path):
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
                print >> stderr, '{file}:{lineno}:{col_offset}: {code} use ' \
                        'of import *\n{line}{shift}^' \
                        .format(file=path, lineno=node.lineno,
                                col_offset=col_offset, code=self.code,
                                line=line, shift=' ' * col_offset)
                count += 1

        return count


class NoExceptEmpty(CodedCheck):
    global check_counter
    check_counter += 1
    code = 'L{:=03}'.format(check_counter)

    def _do(self, path):
        lines, tree = self._parse_file(path)
        count = 0
        # for each node
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler) and not node.type:
                line = lines[node.lineno - 1]
                # ExceptHandler nodes don't have a col_offset :(
                col_offset = line.find(':')
                print >> stderr, '{file}:{lineno}:{col_offset}: {code} use ' \
                        'of empty/broad except\n{line}{shift}^' \
                        .format(file=path, lineno=node.lineno,
                                col_offset=col_offset, code=self.code,
                                line=line, shift=' ' * col_offset)
                count += 1

        return count


class NoExceptException(CodedCheck):
    global check_counter
    check_counter += 1
    code = 'L{:=03}'.format(check_counter)

    def _do(self, path):
        lines, tree = self._parse_file(path)
        count = 0
        # for each node
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler) and \
               node.type.id == 'Exception':
                line = lines[node.lineno - 1]
                # ExceptHandler nodes don't have a col_offset :(
                col_offset = line.find(':')
                print >> stderr, '{file}:{lineno}:{col_offset}: {code} use ' \
                        'of empty/broad except\n{line}{shift}^' \
                        .format(file=path, lineno=node.lineno,
                                col_offset=col_offset, code=self.code,
                                line=line, shift=' ' * col_offset)
                count += 1

        return count


class NoPrintCheck(CodedCheck):
    global check_counter
    check_counter += 1
    code = 'L{:=03}'.format(check_counter)

    def _do(self, path):
        lines, tree = self._parse_file(path)
        count = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Print):
                line = lines[node.lineno - 1]
                # Print nodes don't have a col_offset :(
                col_offset = line.find('print')
                print >> stderr, '{file}:{lineno}:{col_offset}: {code} use ' \
                        'of print\n{line}{shift}^' \
                        .format(file=path, lineno=node.lineno,
                                col_offset=col_offset, code=self.code,
                                line=line, shift=' ' * col_offset)
                count += 1

        return count


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

    ignore = args.ignore.split(',') if args.ignore else []

    checks = set([Pep8Check(ignore=ignore),
                  # TODO: provide a way to number and ignore pyflakes messages
                  PyFlakesCheck(ignore=ignore),
                  AbsoluteImportCheck(ignore=ignore),
                  NoImportStarCheck(ignore=ignore),
                  NoExceptEmpty(ignore=ignore),
                  NoExceptException(ignore=ignore)])

    if args.web:
        checks.add(NoPrintCheck(ignore=ignore))

    def process_file(filename):
        count = 0
        for check in checks:
            count += check.do(filename)

        return count

    count = 0
    for path in args.paths:
        if isdir(path):
            for dirpath, dirnames, filenames in walk(path):
                for filename in filenames:
                    if filename.endswith('.py'):
                        count += process_file(join(dirpath, filename))
        else:
            count += process_file(path)

    exit(int(count))


if __name__ == '__main__':
    _main()
