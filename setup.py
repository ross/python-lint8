#!/usr/bin/env python

from setuptools import setup, find_packages

version = '0.0.1'
long_description = ''
for fn in ['README.rst', 'CHANGES.txt', 'TODO.txt']:
    try:
        long_description += open(fn).read() + '\n\n'
    except IOError:
        pass

setup(name='lint8',
      license='GPLv3',
      version=version,
      description="Python style guide checker",
      long_description=long_description,
      keywords='lint8',
      author='Johann C. Rocholl',
      author_email='johann@rocholl.net',
      url='http://github.com/ross/python-lint8',
      packages=['lint8', 'lint8.scripts'],
      scripts=['bin/lint8'],
      classifiers=["Development Status :: 6 - Mature",
                   "Environment :: Console",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: MIT License",
                   "Programming Language :: Python",
                   "Topic :: Software Development",
                   "Topic :: Utilities"],
      install_requires=['setuptools'],
      requires=['pep8 (>= 1.3.3)',
                'pyflakes'])
