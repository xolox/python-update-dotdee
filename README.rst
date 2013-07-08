update-dotdee: Generic modularized configuration file manager
=============================================================

The ``update-dotdee`` program makes it very easy to manage (configuration)
files with modular contents in the style of Debian_ and dotdee_. The program
takes the pathname of an existing file and updates that file based on the
contents of the files in the directory with the same name as the file but
ending in ``.d``. For example::

    peter@macbook> sudo update-dotdee /etc/hosts
    2013-07-06 19:32:03 macbook INFO Reading file: /etc/hosts.d/1-local
    2013-07-06 19:32:03 macbook INFO Reading file: /etc/hosts.d/2-work
    2013-07-06 19:32:03 macbook INFO Reading file: /etc/hosts.d/3-ipv6
    2013-07-06 20:59:24 macbook INFO Checking for local changes to /etc/hosts
    2013-07-06 19:32:03 macbook INFO Writing file: /etc/hosts

Some notes about how it works:

- If the given file exists but the corresponding directory does not exist yet,
  the directory is created and the file is moved into the directory (and
  renamed to ``local``) so that its existing contents are preserved.

- If the generated file has been modified since the last run, ``update-dotdee``
  will refuse to overwrite its contents (unless you use the ``--force``
  option).

- The files in the ``.d`` directory are concatenated in the natural sorting
  order of the filenames (as implemented by the naturalsort_ package).

Installation
------------

You can install the ``update-dotdee`` program using the following command::

    pip install update-dotdee

Contact
-------

The latest version of ``update-dotdee`` is available on PyPi_ and GitHub_. For
bug reports please create an issue on GitHub_. If you have questions,
suggestions, etc. feel free to send me an e-mail at `peter@peterodding.com`_.

License
-------

This software is licensed under the `MIT license`_.

© 2013 Peter Odding.

.. External references:
.. _Debian: http://www.debian.org/
.. _dotdee: http://blog.dustinkirkland.com/2011/04/dotdee-modern-proposal-for-improving.html
.. _GitHub: https://github.com/xolox/python-update-dotdee
.. _MIT license: http://en.wikipedia.org/wiki/MIT_License
.. _naturalsort: https://pypi.python.org/pypi/naturalsort
.. _peter@peterodding.com: peter@peterodding.com
.. _PyPi: https://pypi.python.org/pypi/update-dotdee
