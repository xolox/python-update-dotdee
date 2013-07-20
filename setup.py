#!/usr/bin/env python

import re
from os.path import abspath, dirname, join
from setuptools import setup

# Find the directory where the source distribution was unpacked.
source_directory = dirname(abspath(__file__))

# Find the current version.
module = join(source_directory, 'update_dotdee.py')
for line in open(module, 'r'):
    match = re.match(r'^__version__\s*=\s*["\']([^"\']+)["\']$', line)
    if match:
        version_string = match.group(1)
        break
else:
    raise Exception, "Failed to extract version from pip_accel/__init__.py!"

# Fill in the long description (for the benefit of PyPi)
# with the contents of README.rst (rendered by GitHub).
readme_file = join(source_directory, 'README.rst')
readme_text = open(readme_file, 'r').read()

# Fill in the "install_requires" field based on requirements.txt.
requirements = [l.strip() for l in open(join(source_directory, 'requirements.txt'), 'r')]

setup(name='update-dotdee',
      version=version_string,
      description="Generic modularized configuration file manager",
      long_description=readme_text,
      url='https://github.com/xolox/python-update-dotdee',
      author='Peter Odding',
      author_email='peter@peterodding.com',
      py_modules=['update_dotdee'],
      entry_points={'console_scripts': ['update-dotdee = update_dotdee:main']},
      install_requires=requirements)
