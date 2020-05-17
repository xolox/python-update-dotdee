Changelog
=========

The purpose of this document is to list all of the notable changes to this
project. The format was inspired by `Keep a Changelog`_. This project adheres
to `semantic versioning`_.

.. contents::
   :local:

.. _Keep a Changelog: http://keepachangelog.com/
.. _semantic versioning: http://semver.org/

`Release 5.0`_ (2018-03-29)
---------------------------

Add support for ``*.ini`` configuration file loading, for details refer to the
new :class:`.ConfigLoader` class.

.. _Release 5.0: https://github.com/xolox/python-update-dotdee/compare/4.0...5.0

`Release 4.0`_ (2018-03-25)
---------------------------

Merged `pull request #2`_ adding the ability to execute files and use their output.

.. _Release 4.0: https://github.com/xolox/python-update-dotdee/compare/3.0...4.0
.. _pull request #2: https://github.com/xolox/python-update-dotdee/pull/2

`Release 3.0`_ (2017-07-13)
---------------------------

Switch to :mod:`executor.contexts` to allow for remote execution.

.. _Release 3.0: https://github.com/xolox/python-update-dotdee/compare/2.0...3.0

`Release 2.0`_ (2017-07-13)
---------------------------

Cleaner Python API, separate command line interface.

Detailed changes:

- Refactor setup script, add wheel support.
- Refactor all the things! (Coveralls, Read the Docs, Travis CI, tox, pytest, a test suite, code style checks, ...).
- Separate command line interface from Python API.

.. _Release 2.0: https://github.com/xolox/python-update-dotdee/compare/1.1...2.0

`Release 1.1`_ (2017-07-12)
---------------------------

Merged `pull request #1`_ adding support for Python 3.

.. _Release 1.1: https://github.com/xolox/python-update-dotdee/compare/1.0.10...1.1
.. _pull request #1: https://github.com/xolox/python-update-dotdee/pull/1

`Release 1.0.10`_ (2014-05-06)
------------------------------

Make :exc:`.RefuseToOverwrite` error message user friendly (explain how to proceed).

.. _Release 1.0.10: https://github.com/xolox/python-update-dotdee/compare/1.0.9...1.0.10

`Release 1.0.9`_ (2013-09-08)
-----------------------------

Made the version pinning of requirements less strict.

.. _Release 1.0.9: https://github.com/xolox/python-update-dotdee/compare/1.0.8...1.0.9

`Release 1.0.8`_ (2013-08-06)
-----------------------------

Started using :func:`coloredlogs.install()`.

.. _Release 1.0.8: https://github.com/xolox/python-update-dotdee/compare/1.0.7...1.0.8

`Release 1.0.7`_ (2013-08-06)
-----------------------------

Bumped :pypi:`coloredlogs` requirement to 0.4.3.

.. _Release 1.0.7: https://github.com/xolox/python-update-dotdee/compare/1.0.6...1.0.7

`Release 1.0.6`_ (2013-07-21)
-----------------------------

- Added (absolute) version pinning to requirements.
- Moved version number from ``setup.py`` to :mod:`update_dotdee`.

.. _Release 1.0.6: https://github.com/xolox/python-update-dotdee/compare/1.0.5...1.0.6

`Release 1.0.5`_ (2013-07-16)
-----------------------------

Extracted directory creation out into a separate method.

.. _Release 1.0.5: https://github.com/xolox/python-update-dotdee/compare/1.0.4...1.0.5

`Release 1.0.4`_ (2013-07-15)
-----------------------------

Moved log handler initialization to :func:`.main()`.

.. _Release 1.0.4: https://github.com/xolox/python-update-dotdee/compare/1.0.3...1.0.4

`Release 1.0.3`_ (2013-07-08)
-----------------------------

Improved the documentation (e.g. documented natural order sorting).

.. _Release 1.0.3: https://github.com/xolox/python-update-dotdee/compare/1.0.2...1.0.3

`Release 1.0.2`_ (2013-07-08)
-----------------------------

Bug fix: Ignore checksum on the first (migration) run which moves the target
file into the source directory.

.. _Release 1.0.2: https://github.com/xolox/python-update-dotdee/compare/1.0.1...1.0.2

`Release 1.0.1`_ (2013-07-07)
-----------------------------

Moved logging initialization out of "user accessible" code which can be run
multiple times and should not cause log duplication.

.. _Release 1.0.1: https://github.com/xolox/python-update-dotdee/compare/1.0...1.0.1

`Release 1.0`_ (2013-07-06)
---------------------------

The first release didn't amount to more than a hundred lines of Python code,
but it did what it was supposed to do 😇 (generate a single text file by
concatenating a directory of text files together).

.. _Release 1.0: https://github.com/xolox/python-update-dotdee/tree/1.0
