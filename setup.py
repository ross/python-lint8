#!/usr/bin/env python

from setuptools import setup
from os.path import join, dirname

try:
    long_description = open(join(dirname(__file__), 'README.rst')).read()
except Exception:
    long_description = None

setup(
    name='lint8',
    version='0.0.1',
    description='',
    author='Ross McFarland',
    author_email='ross@gmail.com',
    url='http://github.com/ross/python-lint8',

    long_description=long_description,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    packages=['lint8'],
    provides=['lint8'],
    requires=['pep8', 'pyflakes'],
    install_requires=['pep8', 'pyflakes'],
)
