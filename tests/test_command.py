#
#
#

from __future__ import absolute_import

from os.path import dirname, join
from subprocess import PIPE, Popen
from unittest2 import TestCase

FILES_DIR = join(dirname(__file__), 'files')


# TODO: figure out a way to invoke things pre-install
class TestCommand(TestCase):

    def xtest_clean(self):
        clean_file = join(FILES_DIR, 'clean', 'simple.py')
        cmd = Popen(['./lint8.py', clean_file], stdout=PIPE, stderr=PIPE)
        cmd.wait()
        self.assertEquals(0, cmd.returncode)
        self.assertEquals('', cmd.stderr.read())

        clean_file = join(FILES_DIR, 'clean', 'other.py')
        cmd = Popen(['./lint8.py', clean_file], stdout=PIPE, stderr=PIPE)
        cmd.wait()
        self.assertEquals(0, cmd.returncode)
        self.assertEquals('', cmd.stderr.read())

        clean_file = join(FILES_DIR, 'clean', 'exceptions.py')
        cmd = Popen(['./lint8.py', clean_file], stdout=PIPE, stderr=PIPE)
        cmd.wait()
        self.assertEquals(0, cmd.returncode)
        self.assertEquals('', cmd.stderr.read())

        clean_file = join(FILES_DIR, 'clean')
        cmd = Popen(['./lint8.py', clean_file], stdout=PIPE, stderr=PIPE)
        cmd.wait()
        self.assertEquals(0, cmd.returncode)
        self.assertEquals('', cmd.stderr.read())

    def xtest_bad(self):
        bad_file = join(FILES_DIR, 'bad', 'simple.py')
        cmd = Popen(['./lint8.py', bad_file], stdout=PIPE, stderr=PIPE)
        cmd.wait()
        self.assertEquals(8, cmd.returncode)
        self.assertTrue(len(cmd.stderr.readlines()) > cmd.returncode)

        bad_file = join(FILES_DIR, 'bad', 'other.py')
        cmd = Popen(['./lint8.py', bad_file], stdout=PIPE, stderr=PIPE)
        cmd.wait()
        self.assertEquals(9, cmd.returncode)
        self.assertTrue(len(cmd.stderr.readlines()) > cmd.returncode)

        bad_file = join(FILES_DIR, 'bad', 'exceptions.py')
        cmd = Popen(['./lint8.py', bad_file], stdout=PIPE, stderr=PIPE)
        cmd.wait()
        self.assertEquals(4, cmd.returncode)
        self.assertTrue(len(cmd.stderr.readlines()) > cmd.returncode)

        bad_file = join(FILES_DIR, 'bad')
        cmd = Popen(['./lint8.py', bad_file], stdout=PIPE, stderr=PIPE)
        cmd.wait()
        self.assertEquals(21, cmd.returncode)
        self.assertTrue(len(cmd.stderr.readlines()) > cmd.returncode)

    def xtest_web(self):
        bad_file = join(FILES_DIR, 'bad', 'simple.py')
        cmd = Popen(['./lint8.py', '--web', bad_file], stdout=PIPE,
                    stderr=PIPE)
        cmd.wait()
        self.assertEquals(9, cmd.returncode)
        self.assertTrue(len(cmd.stderr.readlines()) > cmd.returncode)

        bad_file = join(FILES_DIR, 'bad', 'other.py')
        cmd = Popen(['./lint8.py', '--web', bad_file], stdout=PIPE,
                    stderr=PIPE)
        cmd.wait()
        self.assertEquals(12, cmd.returncode)
        self.assertTrue(len(cmd.stderr.readlines()) > cmd.returncode)

        bad_file = join(FILES_DIR, 'bad', 'exceptions.py')
        cmd = Popen(['./lint8.py', '--web', bad_file], stdout=PIPE,
                    stderr=PIPE)
        cmd.wait()
        self.assertEquals(4, cmd.returncode)
        self.assertTrue(len(cmd.stderr.readlines()) > cmd.returncode)

        bad_file = join(FILES_DIR, 'bad')
        cmd = Popen(['./lint8.py', '--web', bad_file], stdout=PIPE,
                    stderr=PIPE)
        cmd.wait()
        self.assertEquals(25, cmd.returncode)
        self.assertTrue(len(cmd.stderr.readlines()) > cmd.returncode)

    def xtest_ignore(self):
        bad_file = join(FILES_DIR, 'bad', 'simple.py')
        cmd = Popen(['./lint8.py', '--ignore', 'W291', bad_file], stdout=PIPE,
                    stderr=PIPE)
        cmd.wait()
        self.assertEquals(7, cmd.returncode)
        self.assertTrue(len(cmd.stderr.readlines()) > cmd.returncode)

        bad_file = join(FILES_DIR, 'bad', 'simple.py')
        cmd = Popen(['./lint8.py', '--ignore', 'W291,L001', bad_file],
                    stdout=PIPE, stderr=PIPE)
        cmd.wait()
        self.assertEquals(6, cmd.returncode)
        self.assertTrue(len(cmd.stderr.readlines()) > cmd.returncode)

        bad_file = join(FILES_DIR, 'bad', 'simple.py')
        cmd = Popen(['./lint8.py', '--ignore', 'W291,L001,F001', bad_file],
                    stdout=PIPE, stderr=PIPE)
        cmd.wait()
        self.assertEquals(5, cmd.returncode)
        self.assertTrue(len(cmd.stderr.readlines()) > cmd.returncode)
