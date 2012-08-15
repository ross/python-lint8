#
#
#

from __future__ import absolute_import

from lint8.checks import AbsoluteImportChecker, NoImportStarChecker, \
    NoEmptyExceptChecker, NoExceptExceptionChecker, NoPrintChecker, \
    NoPprintChecker, ClassNamingChecker, FunctionNamingChecker, \
    Pep8Checker, PyFlakesChecker
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
                         FunctionNamingChecker()]

        if web:
            self.checkers += [NoPrintChecker(),
                              NoPprintChecker()]

    def process_file(self, filename):
        messages = []
        for checker in self.checkers:
            with open(filename) as f:
                lines = f.readlines()
                messages.extend(checker.check(filename, lines))
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
