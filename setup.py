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
      version=version,
      description="Python style guide checker",
      long_description=long_description,
      classifiers=[],
      keywords='lint8',
      author='Johann C. Rocholl',
      author_email='johann@rocholl.net',
      url='http://github.com/ross/python-lint8',
      license='Expat license',
      py_modules=['lint8'],
      namespace_packages=[],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      requires=[
          'pep8', 
          'pyflakes'
      ],
      entry_points={
          'console_scripts': [
              'lint8 = lint8:_main',
              ],
          },
      )
