# Generic modularized configuration file manager.
#
# Author: Peter Odding <peter@peterodding.com>
# Last Change: July 12, 2017
# URL: https://pypi.python.org/pypi/update-dotdee

"""The Python API of the update-dotdee program."""

# Standard library modules.
import hashlib
import logging
import os
import shutil

# External dependencies.
from humanfriendly import compact, format_path
from natsort import natsort
from property_manager import PropertyManager, mutable_property, required_property

# Semi-standard module versioning.
__version__ = '2.0'

# Initialize a logger for this module.
logger = logging.getLogger(__name__)


class UpdateDotDee(PropertyManager):

    """The :class:`UpdateDotDee` class implements the Python API of update-dotdee."""

    @mutable_property
    def checksum_file(self):
        """The pathname of the file that stores the checksum of the generated file (a string)."""
        return os.path.join(self.directory, '.checksum')

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

    def update_file(self, force=None):
        """
        Update the file with the contents of the files in the ``.d`` directory.

        :param force: Override the value of :attr:`force` (a boolean or
                      :data:`None`).
        """
        if force is None:
            force = self.force
        if not os.path.isdir(self.directory):
            # Create the .d directory.
            self.create_directory()
            # Move the original file into the .d directory.
            local_file = os.path.join(self.directory, 'local')
            logger.info("Moving %s to %s", format_path(self.filename), format_path(local_file))
            shutil.move(self.filename, local_file)
        # Read the modularized configuration file(s).
        blocks = []
        for filename in natsort(os.listdir(self.directory)):
            if not filename.startswith('.'):
                blocks.append(self.read_file(os.path.join(self.directory, filename)))
        contents = "\n\n".join(blocks)
        # Make sure the generated file was not modified? We skip this on the
        # first run, when the original file was just moved into the newly
        # created directory (see above).
        if os.path.isfile(self.filename):
            logger.info("Checking for local changes to %s", format_path(self.filename))
            current_checksum = self.hash_contents()
            if os.path.isfile(self.checksum_file):
                # Recall the previous checksum.
                handle = open(self.checksum_file)
                previous_checksum = handle.read()
                handle.close()
                # Compare the checksums.
                if current_checksum != previous_checksum:
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
        # Update the generated file.
        self.write_file(self.filename, contents)
        # Update the checksum.
        handle = open(self.checksum_file, 'w')
        handle.write(self.hash_contents())
        handle.close()

    def read_file(self, filename):
        """
        Read a text file and provide feedback to the user.

        :param filename: The pathname of the file to read (a string).
        :returns: The contents of the file (a string).
        """
        logger.info("Reading file: %s", format_path(filename))
        handle = open(filename)
        contents = handle.read()
        handle.close()
        num_lines = len(contents.splitlines())
        logger.debug("Read %i line%s from %s",
                     num_lines, '' if num_lines == 1 else 's',
                     format_path(filename))
        return contents.rstrip()

    def write_file(self, filename, contents):
        """
        Write a text file and provide feedback to the user.

        :param filename: The pathname of the file to write (a string).
        :param contents: The new contents of the file (a string).
        """
        logger.info("Writing file: %s", format_path(filename))
        handle = open(filename, 'w')
        handle.write(contents.rstrip() + "\n")
        handle.close()
        num_lines = len(contents.splitlines())
        logger.debug("Wrote %i line%s to %s",
                     num_lines,
                     '' if num_lines == 1 else 's',
                     format_path(filename))

    def hash_contents(self):
        """
        Hash the text file using the SHA1 algorithm.

        :returns: A string containing a hexadecimal SHA1 digest.
        """
        logger.debug("Calculating SHA1 of %s", format_path(self.filename))
        context = hashlib.sha1()
        with open(self.filename, 'rb') as handle:
            context.update(handle.read())
        hexdigest = context.hexdigest()
        logger.debug("SHA1 of %s is %s", format_path(self.filename), hexdigest)
        return hexdigest

    def create_directory(self):
        """Make sure :attr:`directory` exists."""
        if not os.path.isdir(self.directory):
            logger.info("Creating directory %s", format_path(self.directory))
            os.makedirs(self.directory)


class RefuseToOverwrite(Exception):

    """Raised when update-dotdee notices that a generated file was modified."""
