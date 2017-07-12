# Generic modularized configuration file manager.
#
# Author: Peter Odding <peter@peterodding.com>
# Last Change: July 12, 2017
# URL: https://pypi.python.org/pypi/update-dotdee

"""
Usage: update-dotdee FILENAME

Generate a (configuration) file based on the contents of the files in the
directory with the same name as FILENAME but ending in '.d'.

If FILENAME exists but the corresponding directory does not exist yet, the
directory is created and FILENAME is moved into the directory so that its
existing contents are preserved.

Supported options:

  -f, --force

    Update FILENAME even if it contains local modifications,
    instead of aborting with an error message.

  -v, --verbose

    Increase logging verbosity (can be repeated).

  -q, --quiet

    Decrease logging verbosity (can be repeated).

  -h, --help

    Show this message and exit.
"""

# Standard library modules.
import getopt
import logging
import os
import sys

# External dependencies.
import coloredlogs
from humanfriendly.terminal import usage, warning

# Modules included in our package.
from update_dotdee import UpdateDotDee

# Initialize a logger for this module.
logger = logging.getLogger(__name__)


def main():
    """Command line interface for the ``update-dotdee`` program."""
    # Initialize logging to the terminal and system log.
    coloredlogs.install(syslog=True)
    # Parse the command line arguments.
    program_opts = {}
    try:
        options, arguments = getopt.getopt(sys.argv[1:], 'fvqh', [
            'force', 'verbose', 'quiet', 'help',
        ])
        for option, value in options:
            if option in ('-f', '--force'):
                program_opts['force'] = True
            elif option in ('-v', '--verbose'):
                coloredlogs.increase_verbosity()
            elif option in ('-q', '--quiet'):
                coloredlogs.decrease_verbosity()
            elif option in ('-h', '--help'):
                usage(__doc__)
                sys.exit(0)
            else:
                # Programming error...
                assert False, "Unhandled option!"
        if not arguments:
            usage(__doc__)
            sys.exit(0)
        if len(arguments) != 1:
            raise Exception("Expected a filename as the first and only argument!")
        elif not os.path.isfile(arguments[0]):
            raise Exception("The given filename doesn't point to an existing file!")
        program_opts['filename'] = arguments[0]
    except Exception as e:
        warning("Error: %s", e)
        sys.exit(1)
    # Run the program.
    try:
        UpdateDotDee(**program_opts).update_file()
    except Exception as e:
        logger.exception("Encountered unexpected exception, aborting!")
        sys.exit(1)
