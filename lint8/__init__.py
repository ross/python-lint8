#
#
#

from __future__ import absolute_import

from os import walk
from os.path import isdir, join
import ast
import pep8
import pyflakes.checker
import re

check_counter = 0


class Check:
    cache = {}

    def __init__(self, ignore=[]):
        pass

    def _parse_file(self, path):
        if path in self.cache:
            return self.cache[path][0], self.cache[path][1]
        # TODO: source/tree cache?
        with open(path) as f:
            lines = f.readlines()
            source = ''.join(lines)
            tree = ast.parse(source, path)
            self.cache[path] = [lines, tree]
            return lines, tree


class CustomPep8Checker(pep8.Checker):

    def __init__(self, *args, **kwargs):
        pep8.Checker.__init__(self, *args, **kwargs)
        self.errors = []

    def report_error(self, *args, **kwargs):

        self.msg = ''

        def message(text):
            self.msg += text + '\n'

        pep8.message = message

        pep8.Checker.report_error(self, *args, **kwargs)

        if self.msg:
            self.errors.append(self.msg)


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

    def do(self, path):
        lines, tree = self._parse_file(path)
        checker = CustomPep8Checker(path, lines=lines)
        checker.check_all()

        # TODO: convert to objects rather than strings
        return checker.errors


class PyFlakesCheck(Check):
    msg_to_code = {}
    code_to_msg = {}

    for code, msg in enumerate((pyflakes.messages.UnusedImport,
                                pyflakes.messages.RedefinedWhileUnused,
                                pyflakes.messages.ImportShadowedByLoopVar,
                                pyflakes.messages.ImportStarUsed,
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
        # this is always ignored b/c we have a slightly better test for it
        self.ignored = {pyflakes.messages.ImportStarUsed: True}
        for code in ignore:
            if code[0] == 'F':
                try:
                    msg = self.code_to_msg[code]
                except KeyError:
                    pass
                else:
                    self.ignored[msg] = True

    def do(self, path):
        lines, tree = self._parse_file(path)
        checker = pyflakes.checker.Checker(tree, path)
        errors = []
        for message in checker.messages:
            type_ = type(message)
            if type_ not in self.ignored:
                code = self.msg_to_code[type_]
                lineno = int(str(message).split(':')[1])
                line = lines[lineno - 1]
                msg = message.message % message.message_args
                errors.append('{file}:{lineno}: {code} {message}\n{line}'
                              .format(file=path, lineno=message.lineno,
                                      code=code, message=msg, line=line))

        return errors


class CodedCheck(Check):

    def __init__(self, ignore=[]):
        Check.__init__(self, ignore=ignore)
        self.skip = ignore.count(self.code) > 0

    def do(self, path):
        if self.skip:
            return []
        return self._do(path)


class AbsoluteImportCheck(CodedCheck):
    global check_counter
    check_counter += 1
    code = 'L{:=03}'.format(check_counter)

    def _do(self, path):
        lines, tree = self._parse_file(path)
        if len(tree.body) == 0:
            return []
        first = tree.body[0]
        # from __future__
        if isinstance(first, ast.ImportFrom) and \
           first.module == '__future__':
            # look though the things being imported for absolute_import
            for name in first.names:
                if name.name == 'absolute_import' or name.name == '*':
                    # found it so no error
                    return []

        # if we're here we didn't find what we're looking for
        return ['{file}:1: {code} file missing "from __future__ ' \
                'import absolute_import"\n'.format(file=path, code=self.code)]


class NoImportStarCheck(CodedCheck):
    global check_counter
    check_counter += 1
    code = 'L{:=03}'.format(check_counter)

    def _do(self, path):
        lines, tree = self._parse_file(path)
        errors = []
        # for each node
        for node in ast.walk(tree):
            # from <anything> import *
            if isinstance(node, ast.ImportFrom) and \
               node.names[0].name == '*':
                line = lines[node.lineno - 1]
                # ImportFrom nodes don't have a col_offset :(
                col_offset = line.find('*')
                errors.append('{file}:{lineno}:{col_offset}: {code} use '
                              'of import *\n{line}{shift}^'
                              .format(file=path, lineno=node.lineno,
                                      col_offset=col_offset, code=self.code,
                                      line=line, shift=' ' * col_offset))

        return errors


class NoExceptEmpty(CodedCheck):
    global check_counter
    check_counter += 1
    code = 'L{:=03}'.format(check_counter)

    def _do(self, path):
        lines, tree = self._parse_file(path)
        errors = []
        # for each node
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler) and not node.type:
                line = lines[node.lineno - 1]
                # ExceptHandler nodes don't have a col_offset :(
                col_offset = line.find(':')
                errors.append('{file}:{lineno}:{col_offset}: {code} use '
                              'of empty/broad except\n{line}{shift}^'
                              .format(file=path, lineno=node.lineno,
                                      col_offset=col_offset, code=self.code,
                                      line=line, shift=' ' * col_offset))

        return errors


class NoExceptException(CodedCheck):
    global check_counter
    check_counter += 1
    code = 'L{:=03}'.format(check_counter)

    def _do(self, path):
        lines, tree = self._parse_file(path)
        errors = []

        def catches_exception(node):
            if isinstance(node, ast.ExceptHandler) and \
               node.type.id == 'Exception':
                return True
            elif isinstance(node, ast.Tuple):
                for elt in node.elts:
                    if elt.id == 'Exception':
                        return True
            return False

        # for each node
        for node in ast.walk(tree):
            try:
                if catches_exception(node):
                    line = lines[node.lineno - 1]
                    col_offset = line.find('Exception')
                    errors.append('{file}:{lineno}:{col_offset}: {code} use '
                                  'of empty/broad except\n{line}{shift}^'
                                  .format(file=path, lineno=node.lineno,
                                          col_offset=col_offset,
                                          code=self.code, line=line,
                                          shift=' ' * col_offset))
            except AttributeError:
                pass

        return errors


class NoPrintCheck(CodedCheck):
    global check_counter
    check_counter += 1
    code = 'L{:=03}'.format(check_counter)

    def _do(self, path):
        lines, tree = self._parse_file(path)
        errors = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Print):
                line = lines[node.lineno - 1]
                # Print nodes don't have a col_offset :(
                col_offset = line.find('print')
                errors.append('{file}:{lineno}:{col_offset}: {code} use '
                              'of print\n{line}{shift}^'
                              .format(file=path, lineno=node.lineno,
                                      col_offset=col_offset, code=self.code,
                                      line=line, shift=' ' * col_offset))

        return errors


class NoPprintCheck(CodedCheck):
    global check_counter
    check_counter += 1
    code = 'L{:=03}'.format(check_counter)

    def _do(self, path):
        lines, tree = self._parse_file(path)
        errors = []
        # for each node
        for node in ast.walk(tree):
            # from <anything> import *
            if isinstance(node, ast.ImportFrom) and \
               node.module == 'pprint':
                line = lines[node.lineno - 1]
                # ImportFrom nodes don't have a col_offset :(
                col_offset = line.find('*')
                errors.append('{file}:{lineno}:{col_offset}: {code} import '
                              'of pprint *\n{line}{shift}^'
                              .format(file=path, lineno=node.lineno,
                                      col_offset=col_offset, code=self.code,
                                      line=line, shift=' ' * col_offset))

        return errors


# TODO: look in to using this everywhere
class WalkingCheck(CodedCheck):

    def _do(self, path):
        lines, tree = self._parse_file(path)
        errors = []
        # for each node
        for node in ast.walk(tree):
            error = self._check(node, path, lines)
            if error:
                errors.append(error)

        return errors

    def _message(self, path, lines, line_num, col_offset, desc):
        line = lines[line_num]
        return '{file}:{lineno}:{col_offset}: {code} {desc}\n{line}' \
                '{shift}^'.format(file=path, lineno=line_num,
                                  col_offset=col_offset,
                                  code=self.code, line=line,
                                  shift=' ' * col_offset, desc=desc)


class FunctionNamingCheck(WalkingCheck):
    global check_counter
    check_counter += 1
    code = 'L{:=03}'.format(check_counter)

    # lower and underscore
    func_re = re.compile('^[a-z_][a-z0-9_]+$')

    def _check(self, node, path, lines):
        if isinstance(node, ast.FunctionDef) and \
           not self.func_re.match(node.name):
            # +4 to skip over 'def '
            return self._message(path, lines, node.lineno - 1,
                                 node.col_offset + 4,
                                 'bad function name "{name}"'
                                 .format(name=node.name))


class ClassNamingCheck(WalkingCheck):
    global check_counter
    check_counter += 1
    code = 'L{:=03}'.format(check_counter)

    # initial cap, lower and upper after
    func_re = re.compile('^[A-Z][A-Za-z0-9]+$')

    def _check(self, node, path, lines):
        if isinstance(node, ast.ClassDef) and \
           not self.func_re.match(node.name):
            # +6 to skip over 'def '
            return self._message(path, lines, node.lineno - 1,
                                 node.col_offset + 6,
                                 'bad class name "{name}"'
                                 .format(name=node.name))


class Checker:

    def __init__(self, ignore=[], web=False):
        self.checks = set([Pep8Check(ignore=ignore),
                           PyFlakesCheck(ignore=ignore),
                           AbsoluteImportCheck(ignore=ignore),
                           NoImportStarCheck(ignore=ignore),
                           NoExceptEmpty(ignore=ignore),
                           NoExceptException(ignore=ignore),
                           FunctionNamingCheck(ignore=ignore),
                           ClassNamingCheck(ignore=ignore)])

        if web:
            self.checks.add(NoPrintCheck(ignore=ignore))
            self.checks.add(NoPprintCheck(ignore=ignore))

    def process_file(self, filename):
        errors = []
        for check in self.checks:
            errors.extend(check.do(filename))

        return errors

    def process(self, paths):
        errors = []
        for path in paths:
            if isdir(path):
                for dirpath, dirnames, filenames in walk(path):
                    for filename in filenames:
                        if filename.endswith('.py'):
                            errors.extend(self.process_file(join(dirpath,
                                                                 filename)))
            else:
                errors.extend(self.process_file(path))

        self.errors = errors

        return len(errors)
