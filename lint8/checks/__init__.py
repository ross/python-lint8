#
#
#

from __future__ import absolute_import

import ast


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


registry = Registry()


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
        return '{path}:{line}:{col} {code} {description}\n{snippet}{shift}^' \
                .format(shift=' ' * self.col, **self.__dict__)


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


class AbsoluteImportCheck(AstChecker):

    def check(self, path, lines):
        tree = self._parse(path, lines)
        if len(tree.body) == 0:
            return []
        # has to be the first node
        first = tree.body[0]
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
            else:  # if isinstance(typ, ast.Tuple):
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
                if alias.name =='pprint':
                    snippet = lines[node.lineno - 1]
                    col = snippet.find('pprint')
                    return Message(path, node.lineno, col, self.code,
                                   'import of pprint', snippet)
