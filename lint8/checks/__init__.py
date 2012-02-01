#
#
#

from __future__ import absolute_import

import ast
import pep8
import pyflakes.checker
import re


class Registry:

    def __init__(self):
        self.checkers = {}

    def register(self, cls, code):
        self.checkers[cls] = code

    def lookup(self, cls):
        try:
            return self.checkers[cls]
        except KeyError:
            return 'n/a'


class Message:

    def __init__(self, path, line, col, code, description, snippet):
        self.path = path
        self.line = line
        self.col = col
        self.code = code
        if not snippet.endswith('\n'):
            snippet += '\n'
        self.snippet = snippet
        self.description = description

    def __str__(self):
        if self.col is None:
            return '{path}:{line}: {code} ' \
                    '{description}\n{snippet}'.format(**self.__dict__)
        else:
            return '{path}:{line}:{col} {code} ' \
                    '{description}\n{snippet}{shift}^' \
                    .format(shift=' ' * self.col, **self.__dict__)

    def __repr__(self):
        return '<Message {code}, {path}:{line}>'.format(**self.__dict__)


class BaseChecker:

    def __init__(self):
        self.code = registry.lookup(self.__class__)


class AstChecker(BaseChecker):
    # class-wide
    cache_enabled = True
    _cached_path = None
    _cached_tree = None

    def _parse(self, path, lines):
        if not self.cache_enabled or path != self._cached_path:
            self._cached_path = path
            tree = ast.parse(''.join(lines), path)
            self._cached_tree = tree
        return self._cached_tree


class AbsoluteImportChecker(AstChecker):

    def check(self, path, lines):
        tree = self._parse(path, lines)
        if len(tree.body) == 0:
            return []
        # has to be the first node
        first = tree.body[0]
        # unless the first is an string expression (doc)
        if isinstance(first, ast.Expr) and isinstance(first.value, ast.Str):
            # it's got to be second, if there is a second
            try:
                first = tree.body[1]
            except IndexError:
                return []
        if isinstance(first, ast.ImportFrom) and \
           first.module == '__future__':
            # we have the right module
            for name in first.names:
                if name.name == 'absolute_import' or name.name == '*':
                    # we found absolute_import, we're good
                    return []
        # if we're here we didn't find what we're looking for
        return [Message(path, 1, 0, self.code,
                        'missing from __future__ import absolute_import',
                        lines[0])]


class AstWalkChecker(AstChecker):

    def check(self, path, lines):
        tree = self._parse(path, lines)
        errors = []
        for node in ast.walk(tree):
            error = self._check_node(path, lines, node)
            if error:
                errors.append(error)
        return errors


class NoImportStarChecker(AstWalkChecker):

    def _check_node(self, path, lines, node):
        if isinstance(node, ast.ImportFrom) and \
           node.names[0].name == '*':
            snippet = lines[node.lineno - 1]
            col = snippet.find('*')
            return Message(path, node.lineno, col, self.code,
                           'use of import *', snippet)


class NoEmptyExceptChecker(AstWalkChecker):

    def _check_node(self, path, lines, node):
        if isinstance(node, ast.ExceptHandler) and not node.type:
            snippet = lines[node.lineno - 1]
            col = snippet.find('except:')
            return Message(path, node.lineno, col, self.code,
                           'use of empty except', snippet)


class NoExceptExceptionChecker(AstWalkChecker):

    def _check_node(self, path, lines, node):

        def create_msg(nd):
            snippet = lines[nd.lineno - 1]
            col = snippet.find('Exception')
            return Message(path, nd.lineno, col, self.code,
                           'use of except Exception', snippet)

        if isinstance(node, ast.ExceptHandler):
            typ = node.type
            if isinstance(typ, ast.Name):
                if typ.id == 'Exception':
                    return create_msg(typ)
            elif isinstance(typ, ast.Tuple):
                for elt in typ.elts:
                    if elt.id == 'Exception':
                        return create_msg(elt)


class NoPrintChecker(AstWalkChecker):

    def _check_node(self, path, lines, node):
        if isinstance(node, ast.Print):
            snippet = lines[node.lineno - 1]
            col = snippet.find('print')
            return Message(path, node.lineno, col, self.code,
                           'use of print', snippet)


class NoPprintChecker(AstWalkChecker):

    def _check_node(self, path, lines, node):
        if isinstance(node, ast.ImportFrom) and \
           node.module == 'pprint':
            snippet = lines[node.lineno - 1]
            col = snippet.find('pprint')
            return Message(path, node.lineno, col, self.code,
                           'import of pprint', snippet)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == 'pprint':
                    snippet = lines[node.lineno - 1]
                    col = snippet.find('pprint')
                    return Message(path, node.lineno, col, self.code,
                                   'import of pprint', snippet)


class ClassNamingChecker(AstWalkChecker):
    re = re.compile('^_?[A-Z][A-Za-z0-9]+$')

    def _check_node(self, path, lines, node):
        if isinstance(node, ast.ClassDef) and not self.re.match(node.name):
            snippet = lines[node.lineno - 1]
            # +6 to skip over 'class '
            col = node.col_offset + 6
            return Message(path, node.lineno, col, self.code,
                           'invalid class name "{name}"'
                           .format(name=node.name), snippet)


class FunctionNamingChecker(AstWalkChecker):
    re = re.compile('^[a-z_][a-z0-9_]+$')

    def _check_node(self, path, lines, node):
        # allowing setUp though since it's a std/common TestCase name
        if isinstance(node, ast.FunctionDef) and node.name != 'setUp' and \
           not self.re.match(node.name):
            snippet = lines[node.lineno - 1]
            # +4 to skip over 'def '
            col = node.col_offset + 4
            return Message(path, node.lineno, col, self.code,
                           'invalid function name "{name}"'
                           .format(name=node.name), snippet)


class _CustomPep8Checker(pep8.Checker):

    def __init__(self, *args, **kwargs):
        pep8.Checker.__init__(self, *args, **kwargs)
        self.messages = []

    def report_error(self, line, col, description, *args, **kwargs):
        code, description = description.split(' ', 1)
        snippet = self.lines[line - 1]
        self.messages.append(Message(self.filename, line, col, code,
                                     description, snippet))


class Pep8Checker(BaseChecker):

    def __init__(self):
        BaseChecker.__init__(self)
        arglist = ['--repeat', '--show-source']
        arglist.append('dummy')
        pep8.process_options(arglist=arglist)

    def check(self, path, lines):
        checker = _CustomPep8Checker(path, lines=lines)
        checker.check_all()
        return checker.messages


class PyFlakesChecker(AstChecker):
    msg_to_code = {}

    for code, msg in enumerate((pyflakes.messages.UnusedImport,
                                pyflakes.messages.RedefinedWhileUnused,
                                pyflakes.messages.ImportShadowedByLoopVar,
                                'xyxyxyx',
                                pyflakes.messages.UndefinedName,
                                pyflakes.messages.UndefinedExport,
                                pyflakes.messages.UndefinedLocal,
                                pyflakes.messages.DuplicateArgument,
                                pyflakes.messages.RedefinedFunction,
                                pyflakes.messages.LateFutureImport,
                                pyflakes.messages.UnusedVariable)):
        code = 'F{:=03}'.format(code + 1)
        msg_to_code[msg] = code

    def check(self, path, lines):
        checker = pyflakes.checker.Checker(self._parse(path, lines), path)
        messages = []
        for message in checker.messages:
            type_ = type(message)
            try:
                code = self.msg_to_code[type_]
            except KeyError:
                pass
            else:
                lineno = int(str(message).split(':')[1])
                line = lines[lineno - 1]
                msg = message.message % message.message_args
                # col not available :(
                messages.append(Message(path, lineno, None, code, msg, line))
        return messages


registry = Registry()
for code, cls in {'L001': AbsoluteImportChecker,
                  'L002': NoImportStarChecker,
                  'L003': NoEmptyExceptChecker,
                  'L004': NoExceptExceptionChecker,
                  'L005': NoPrintChecker,
                  'L006': NoPprintChecker,
                  'L007': FunctionNamingChecker,
                  'L008': ClassNamingChecker}.items():
    registry.register(cls, code)
