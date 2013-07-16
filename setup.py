#!/usr/bin/env python

from os.path import abspath, dirname, join
from setuptools import setup

# Fill in the long description (for the benefit of PyPi)
# with the contents of README.rst (rendered by GitHub).
readme_file = join(dirname(abspath(__file__)), 'README.rst')
readme_text = open(readme_file, 'r').read()

setup(name='update-dotdee',
      version='1.0.5',
      description="Generic modularized configuration file manager",
      long_description=readme_text,
      url='https://github.com/xolox/python-update-dotdee',
      author='Peter Odding',
      author_email='peter@peterodding.com',
      py_modules=['update_dotdee'],
      entry_points={'console_scripts': ['update-dotdee = update_dotdee:main']},
      install_requires=['coloredlogs', 'humanfriendly', 'naturalsort'])
