#
#
#

from __future__ import absolute_import, print_function, unicode_literals

from codecs import open as codecs_open
from lint8.checks import AbsoluteImportChecker, NoImportStarChecker, \
    NoEmptyExceptChecker, NoExceptExceptionChecker, NoPrintChecker, \
    NoPprintChecker, ClassNamingChecker, FunctionNamingChecker, \
    Pep8Checker, PyFlakesChecker, PrintFunctionChecker, UnicodeLiteralsChecker
from os.path import isdir, join
from os import walk
import re


class Checker:

    def __init__(self, ignores=[], web=False):
        self.ignores = ignores
        self.checkers = [Pep8Checker(),
                         PyFlakesChecker(),
                         AbsoluteImportChecker(),
                         NoImportStarChecker(),
                         NoEmptyExceptChecker(),
                         NoExceptExceptionChecker(),
                         ClassNamingChecker(),
                         FunctionNamingChecker(),
                         PrintFunctionChecker(),
                         UnicodeLiteralsChecker()]

        if web:
            self.checkers += [NoPrintChecker(),
                              NoPprintChecker()]

    def process_file(self, filename):
        messages = []
        for checker in self.checkers:
            with codecs_open(filename, encoding='utf-8') as f:
                lines = f.readlines()
                # if the first or second line of the file is a coding, strip it
                # as it'll break ast.parse/compile
                n = len(lines)
                if n and '# -*- coding:' in lines[0]:
                    lines = lines[1:]
                elif n > 1 and '# -*- coding:' in lines[1]:
                    lines = [lines[0]] + lines[2:]
                try:
                    messages.extend(checker.check(filename, lines))
                except UnicodeDecodeError:
                    from pprint import pprint
                    pprint(lines)
                    raise
        return messages

    def process(self, paths, excludes=[]):

        excludes = [re.compile(exclude) for exclude in excludes]

        def exclude(filename):
            for exclude in excludes:
                if exclude.search(filename):
                    return True
            return False

        messages = []
        for path in paths:
            if isdir(path):
                for dirpath, dirnames, filenames in walk(path):
                    for filename in filenames:
                        filename = join(dirpath, filename)
                        if filename.endswith('.py') and not exclude(filename):
                            messages.extend(self.process_file(filename))
            elif not exclude(path):
                messages.extend(self.process_file(path))

        def cleanout(message):
            # TODO: partial matches
            return not self.ignores.count(message.code)

        # filter out ignored message
        messages = filter(cleanout, messages)

        self.messages = messages

        return len(messages)
