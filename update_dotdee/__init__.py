# Generic modularized configuration file manager.
#
# Author: Peter Odding <peter@peterodding.com>
# Last Change: March 25, 2018
# URL: https://pypi.python.org/pypi/update-dotdee

"""The Python API of the update-dotdee program."""

# Standard library modules.
import hashlib
import logging
import os

# External dependencies.
from executor.contexts import LocalContext
from humanfriendly import compact, format_path, pluralize
from natsort import natsort
from property_manager import PropertyManager, mutable_property, required_property

# Semi-standard module versioning.
__version__ = '4.0'

# Initialize a logger for this module.
logger = logging.getLogger(__name__)


class UpdateDotDee(PropertyManager):

    """The :class:`UpdateDotDee` class implements the Python API of update-dotdee."""

    @mutable_property
    def checksum_file(self):
        """The pathname of the file that stores the checksum of the generated file (a string)."""
        return os.path.join(self.directory, '.checksum')

    @mutable_property(cached=True)
    def context(self):
        """An execution context created by :mod:`executor.contexts`."""
        return LocalContext()

    @mutable_property
    def directory(self):
        """The pathname of the directory with configuration snippets (a string)."""
        return self.filename + '.d'

    @required_property
    def filename(self):
        """The pathname of the configuration file to generate (a string)."""

    @mutable_property
    def force(self):
        """:data:`True` to overwrite modified files, :data:`False` to abort (the default)."""
        return False

    @property
    def new_checksum(self):
        """Get the SHA1 digest of the contents of :attr:`filename` (a string)."""
        if self.context.is_file(self.filename):
            friendly_name = format_path(self.filename)
            logger.debug("Calculating SHA1 of %s ..", friendly_name)
            context = hashlib.sha1()
            context.update(self.context.read_file(self.filename))
            checksum = context.hexdigest()
            logger.debug("The SHA1 digest of %s is %s.", friendly_name, checksum)
            return checksum

    @property
    def old_checksum(self):
        """Get the checksum stored in :attr:`checksum_file` (a string or :data:`None`)."""
        if self.context.is_file(self.checksum_file):
            logger.debug("Reading saved checksum from %s ..", format_path(self.checksum_file))
            checksum = self.context.read_file(self.checksum_file).decode('ascii')
            logger.debug("Saved checksum is %s.", checksum)
            return checksum

    def update_file(self, force=None):
        """
        Update the file with the contents of the files in the ``.d`` directory.

        :param force: Override the value of :attr:`force` (a boolean or
                      :data:`None`).
        :raises: :exc:`RefuseToOverwrite` when :attr:`force` is :data:`False`
                 and the contents of :attr:`filename` were modified.
        """
        if force is None:
            force = self.force
        if not self.context.is_directory(self.directory):
            # Create the .d directory.
            logger.info("Creating directory %s ..", format_path(self.directory))
            self.context.execute('mkdir', '-p', self.directory, tty=False)
            # Move the original file into the .d directory.
            local_file = os.path.join(self.directory, 'local')
            logger.info("Moving %s to %s ..", format_path(self.filename), format_path(local_file))
            self.context.execute('mv', self.filename, local_file, tty=False)
        # Read the modularized configuration file(s).
        blocks = []
        for entry in natsort(self.context.list_entries(self.directory)):
            if not entry.startswith('.'):
                filename = os.path.join(self.directory, entry)
                if self.context.is_executable(filename):
                    blocks.append(self.execute_file(filename))
                else:
                    blocks.append(self.read_file(filename))
        contents = b"\n\n".join(blocks)
        # Make sure the generated file was not modified? We skip this on the
        # first run, when the original file was just moved into the newly
        # created directory (see above).
        if all(map(self.context.is_file, (self.filename, self.checksum_file))):
            logger.info("Checking for local changes to %s ..", format_path(self.filename))
            if self.new_checksum != self.old_checksum:
                if force:
                    logger.warning(compact(
                        """
                        The contents of the file to generate ({filename})
                        were modified but --force was used so overwriting
                        anyway!
                        """,
                        filename=format_path(self.filename),
                    ))
                else:
                    raise RefuseToOverwrite(compact(
                        """
                        The contents of the file to generate ({filename})
                        were modified and I'm refusing to overwrite it! If
                        you're sure you want to proceed, use the --force
                        option or delete the file {checksum_file} and
                        retry.
                        """,
                        filename=format_path(self.filename),
                        checksum_file=format_path(self.checksum_file),
                    ))
        # Update the generated configuration file.
        self.write_file(self.filename, contents)
        # Update the checksum file.
        self.context.write_file(self.checksum_file, self.new_checksum)

    def read_file(self, filename):
        """
        Read a text file and provide feedback to the user.

        :param filename: The pathname of the file to read (a string).
        :returns: The contents of the file (a string).
        """
        logger.info("Reading file: %s", format_path(filename))
        contents = self.context.read_file(filename)
        num_lines = len(contents.splitlines())
        logger.debug("Read %s from %s.",
                     pluralize(num_lines, 'line'),
                     format_path(filename))
        return contents.rstrip()

    def execute_file(self, filename):
        """
        Execute a file and provide feedback to the user.

        :param filename: The pathname of the file to execute (a string).
        :returns: Whatever the executed file returns on stdout (a string).
        """
        logger.info("Executing file: %s", format_path(filename))
        contents = self.context.execute(filename, capture=True).stdout
        num_lines = len(contents.splitlines())
        logger.debug("Execution of %s yielded % of output.",
                     format_path(filename),
                     pluralize(num_lines, 'line'))
        return contents.rstrip()

    def write_file(self, filename, contents):
        """
        Write a text file and provide feedback to the user.

        :param filename: The pathname of the file to write (a string).
        :param contents: The new contents of the file (a string).
        """
        logger.info("Writing file: %s", format_path(filename))
        contents = contents.rstrip() + b"\n"
        self.context.write_file(filename, contents)
        logger.debug("Wrote %s to %s.",
                     pluralize(len(contents.splitlines()), "line"),
                     format_path(filename))


class RefuseToOverwrite(Exception):

    """Raised when update-dotdee notices that a generated file was modified."""
