update-dotdee: Generic modularized configuration file manager
=============================================================

.. image:: https://travis-ci.org/xolox/python-update-dotdee.svg?branch=master
   :target: https://travis-ci.org/xolox/python-update-dotdee

.. image:: https://coveralls.io/repos/xolox/python-update-dotdee/badge.svg?branch=master
   :target: https://coveralls.io/r/xolox/python-update-dotdee?branch=master

The update-dotdee program makes it easy to manage configuration files with
modular contents in the style of Debian_ and dotdee_. The program takes the
pathname of a configuration file and updates that file based on the contents of
the files in the directory with the same name as the file but ending in ``.d``.
It's currently tested on cPython 2.6, 2.7, 3.4, 3.5, 3.6 and PyPy (2.7).

.. contents::
   :local:

Installation
------------

The `update-dotdee` package is available on PyPI_ which means installation
should be as simple as:

.. code-block:: sh

   $ pip install update-dotdee

There's actually a multitude of ways to install Python packages (e.g. the `per
user site-packages directory`_, `virtual environments`_ or just installing
system wide) and I have no intention of getting into that discussion here, so
if this intimidates you then read up on your options before returning to these
instructions ;-).

Usage
-----

There are two ways to use the update-dotdee package: As the command line
program ``update-dotdee`` and as a Python API. For details about the Python API
please refer to the API documentation available on `Read the Docs`_. The
command line interface is described below.

.. contents::
   :local:

.. A DRY solution to avoid duplication of the `update-dotdee --help' text:
..
.. [[[cog
.. from humanfriendly.usage import inject_usage
.. inject_usage('update_dotdee.cli')
.. ]]]

**Usage:** `update-dotdee FILENAME`

Generate a (configuration) file based on the contents of the files in the
directory with the same name as FILENAME but ending in '.d'.

If FILENAME exists but the corresponding directory does not exist yet, the
directory is created and FILENAME is moved into the directory so that its
existing contents are preserved.

**Supported options:**

.. csv-table::
   :header: Option, Description
   :widths: 30, 70


   "``-f``, ``--force``","Update FILENAME even if it contains local modifications,
   instead of aborting with an error message."
   "``-u``, ``--use-sudo``","Enable the use of ""sudo"" to update configuration files that are not
   readable and/or writable for the current user (or the user logged
   in to a remote system over SSH)."
   "``-r``, ``--remote-host=SSH_ALIAS``","Operate on a remote system instead of the local system. The
   ``SSH_ALIAS`` argument gives the SSH alias of the remote host."
   "``-v``, ``--verbose``",Increase logging verbosity (can be repeated).
   "``-q``, ``--quiet``",Decrease logging verbosity (can be repeated).
   "``-h``, ``--help``",Show this message and exit.

.. [[[end]]]

Example
-------

The `/etc/hosts`_ file is a simple example of a configuration file that can be
managed using update-dotdee. Individual files in the ``/etc/hosts.d`` directory
contain snippets that are added to the configuration file on each run. For
example::

 peter@macbook> sudo update-dotdee /etc/hosts
 2013-07-06 19:32:03 macbook INFO Reading file: /etc/hosts.d/1-local
 2013-07-06 19:32:03 macbook INFO Reading file: /etc/hosts.d/2-work
 2013-07-06 19:32:03 macbook INFO Reading file: /etc/hosts.d/3-ipv6
 2013-07-06 20:59:24 macbook INFO Checking for local changes to /etc/hosts
 2013-07-06 19:32:03 macbook INFO Writing file: /etc/hosts

How it works
------------

Some notes about how update-dotdee works:

- If the given file exists but the corresponding directory does not exist yet,
  the directory is created and the file is moved into the directory (and
  renamed to ``local``) so that its existing contents are preserved.

- If the generated file has been modified since the last run, update-dotdee
  will refuse to overwrite its contents (unless you use the ``-f`` or
  ``--force`` option).

- The files in the ``.d`` directory are concatenated in the natural sorting
  order of the filenames (as implemented by the naturalsort_ package).

- Executable files in the ``.d`` directory are executed and their standard
  output is incorporated into the generated contents (since version 4.0).

Use cases
---------

Here are some example use cases for update-dotdee:

**SSH client configuration**
 The update-dotdee program was created in 2013 to provide modular SSH client
 configurations. It was used to generate the ``~/.ssh/config`` file from the
 contents of the files in the ``~/.ssh/config.d`` directory. This functionality
 was needed because I developed an SSH client configuration generator based on
 a database of server metadata and I was looking for a way to update the user's
 ``~/.ssh/config`` without trashing the existing (carefully handcrafted)
 contents.

**System wide configuration files**
 Linux system configuration files like `/etc/crypttab`_, `/etc/fstab`_ and
 `/etc/hosts`_ lack modularity and manipulating them using command line tools
 like awk_ and sed_ can be fragile and/or become unwieldy :-). However if you
 can get your configuration sources (for example Ansible playbooks, Debian
 packages and manual configuration) to agree on the use of update-dotdee then
 you have an elegant, robust and predictable alternative.

Contact
-------

The latest version of update-dotdee is available on PyPI_ and GitHub_. For bug
reports please create an issue on GitHub_. If you have questions, suggestions,
etc. feel free to send me an e-mail at `peter@peterodding.com`_.

License
-------

This software is licensed under the `MIT license`_.

© 2018 Peter Odding.

.. External references:
.. _/etc/crypttab: https://manpages.debian.org/crypttab
.. _/etc/fstab: https://manpages.debian.org/fstab
.. _/etc/hosts: https://manpages.debian.org/hosts
.. _awk: https://manpages.debian.org/awk
.. _Debian: http://www.debian.org/
.. _dotdee: http://blog.dustinkirkland.com/2011/04/dotdee-modern-proposal-for-improving.html
.. _GitHub: https://github.com/xolox/python-update-dotdee
.. _MIT license: http://en.wikipedia.org/wiki/MIT_License
.. _naturalsort: https://pypi.python.org/pypi/naturalsort
.. _per user site-packages directory: https://www.python.org/dev/peps/pep-0370/
.. _peter@peterodding.com: peter@peterodding.com
.. _PyPI: https://pypi.python.org/pypi/update-dotdee
.. _Read the Docs: https://update-dotdee.readthedocs.io/
.. _sed: https://manpages.debian.org/sed
.. _virtual environments: http://docs.python-guide.org/en/latest/dev/virtualenvs/
