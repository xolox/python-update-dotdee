# Generic modular configuration file manager.
#
# Author: Peter Odding <peter@peterodding.com>
# Last Change: March 29, 2018
# URL: https://pypi.python.org/pypi/update-dotdee

"""
Generic modular configuration file management.

The :mod:`update_dotdee` module provides two classes that implement alternative
strategies for using modular configuration files:

- :class:`UpdateDotDee` implements the Python API of the ``update-dotdee``
  program which can be used to split a monolithic configuration file into a
  directory of files with configuration snippets. The monolithic configuration
  file is updated by concatenating the files with configuration snippets to
  enable support for programs that only handle a single configuration file.

- :class:`ConfigLoader` is a lightweight alternative for :class:`UpdateDotDee`
  that makes it easy for Python programs to load ``*.ini`` configuration files
  from multiple locations including ``.d`` directories. It doesn't generate any
  files, it just finds and loads them.
"""

# Standard library modules.
import glob
import hashlib
import logging
import os

# External dependencies.
from executor.contexts import LocalContext
from humanfriendly import compact, format, format_path, parse_path, pluralize
from natsort import natsort
from property_manager import (
    PropertyManager,
    cached_property,
    mutable_property,
    required_property,
)
from six.moves import configparser

# Semi-standard module versioning.
__version__ = '4.0'

DOCUMENTATION_TEMPLATE = """
Configuration files are text files in the subset of `ini syntax`_ supported by
Python's configparser_ module. They can be located in the following places:

{table}

The available configuration files are loaded in the order given above, so that
user specific configuration files override system wide configuration files.

.. _configparser: https://docs.python.org/3/library/configparser.html
.. _ini syntax: https://en.wikipedia.org/wiki/INI_file
"""

# Initialize a logger for this module.
logger = logging.getLogger(__name__)


class UpdateDotDee(PropertyManager):

    """
    The :class:`UpdateDotDee` class implements the Python API of `update-dotdee`.

    To create an :class:`UpdateDotDee` object you need to provide a value for
    the :attr:`filename` property. You can set the values of properties by
    passing keywords arguments to the initializer, for details refer to the
    documentation of the :class:`~property_manager.PropertyManager` superclass.
    """

    @mutable_property
    def checksum_file(self):
        """The pathname of the file that stores the checksum of the generated file (a string)."""
        return os.path.join(self.directory, '.checksum')

    @mutable_property(cached=True)
    def context(self):
        """
        An execution context created by :mod:`executor.contexts`.

        Defaults to a :class:`~executor.contexts.LocalContext` object.
        """
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
        # Read the modular configuration file(s).
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


class ConfigLoader(PropertyManager):

    """
    Wrapper for :mod:`configparser` that searches ``*.d`` directories.

    The :class:`ConfigLoader` class is a simple wrapper for :mod:`configparser`
    that searches for ``*.ini`` configuration files in system-wide and/or
    user-specific configuration directories:

    - In normal usage the caller is expected to set :attr:`program_name` and
      let :class:`ConfigLoader` take care of details like searching for
      available configuration files.

    - Alternatively the caller can set :attr:`available_files` to bypass the
      usage of :attr:`program_name`, :attr:`base_directories` and
      :attr:`filename_extension` to generate :attr:`filename_patterns`.

    The :attr:`parser` and :attr:`section_names` properties and the
    :func:`get_options()` method provide access to the configuration.
    """

    @mutable_property(cached=True)
    def available_files(self):
        """
        The filenames of the available configuration files (a list of strings).

        The value of :attr:`available_files` is computed the first time its
        needed by searching for available configuration files that match
        :attr:`filename_patterns` using :func:`~glob.glob()`. If you set
        :attr:`available_files` this effectively disables searching for
        configuration files.
        """
        matches = []
        for pattern in self.filename_patterns:
            logger.debug("Matching filename pattern: %s", pattern)
            matches.extend(natsort(glob.glob(parse_path(pattern))))
        return matches

    @mutable_property(cached=True)
    def base_directories(self):
        """
        The directories that are searched for configuration files (a list of strings).

        By default this list contains three entries in the following order:

        =============  =====================================================
        Directory      Description
        =============  =====================================================
        ``/etc``       The directory for system wide configuration files on
                       Unix like operating systems.
        ``~``          The profile directory of the current user (also
                       available as the environment variable ``$HOME``).
        ``~/.config``  Alternative directory for user specific configuration
                       files (also known as `$XDG_CONFIG_HOME`_).
        =============  =====================================================

        The order of these entries is significant because it defines the order
        in which configuration files are loaded by :attr:`parser` which
        controls how overrides work (when multiple files are loaded).

        In this order, user specific configuration files override system wide
        configuration files. The reasoning behind this is that the operator may
        not be in a position to change system wide configuration files, even
        though this is an important use case to support.

        .. _$XDG_CONFIG_HOME: https://specifications.freedesktop.org/basedir-spec/latest/ar01s03.html
        """
        return ['/etc', '~', os.environ.get('XDG_CONFIG_HOME', '~/.config')]

    @cached_property
    def documentation(self):
        r"""
        Configuration documentation in reStructuredText_ syntax (a string).

        The purpose of the :attr:`documentation` property is to provide
        documentation on the integration of :class:`ConfigLoader` into other
        projects without denormalizing the required knowledge via copy/paste.

        .. _reStructuredText: https://en.wikipedia.org/wiki/ReStructuredText
        """
        from humanfriendly.tables import format_rst_table
        formatted_table = format_rst_table([
            (directory,
             self.get_main_pattern(directory).replace('*', r'\*'),
             self.get_modular_pattern(directory).replace('*', r'\*'))
            for directory in self.base_directories
        ], [
            "Directory",
            "Main configuration file",
            "Modular configuration files",
        ])
        return format(DOCUMENTATION_TEMPLATE, table=formatted_table).strip()

    @mutable_property
    def filename_extension(self):
        """The filename extension of configuration files (a string, defaults to ``.ini``)."""
        return '.ini'

    @mutable_property(cached=True)
    def filename_patterns(self):
        """
        Filename patterns to search for available configuration files (a list of strings).

        The value of :attr:`filename_patterns` is computed the first time it is
        needed. Each of the :attr:`base_directories` generates two patterns:

        1. A pattern generated by :func:`get_main_pattern()`.
        2. A pattern generated by :func:`get_modular_pattern()`.

        Here's an example:

        >>> from update_dotdee import ConfigLoader
        >>> loader = ConfigLoader(program_name='update-dotdee')
        >>> loader.filename_patterns
        ['/etc/update-dotdee.ini',
         '/etc/update-dotdee.d/*.ini',
         '~/.update-dotdee.ini',
         '~/.update-dotdee.d/*.ini',
         '~/.config/update-dotdee.ini',
         '~/.config/update-dotdee.d/*.ini']
        """
        patterns = []
        for directory in self.base_directories:
            patterns.append(self.get_main_pattern(directory))
            patterns.append(self.get_modular_pattern(directory))
        return patterns

    @cached_property(repr=False)
    def parser(self):
        """A :class:`configparser.RawConfigParser` object with :attr:`available_files` loaded."""
        parser = configparser.RawConfigParser()
        for filename in self.available_files:
            friendly_name = format_path(filename)
            logger.debug("Loading configuration file: %s", friendly_name)
            loaded_files = parser.read(filename)
            if len(loaded_files) == 0:
                self.report_issue("Failed to load configuration file! (%s)", friendly_name)
        logger.debug("Loaded %s from %s.",
                     pluralize(len(parser.sections()), "section"),
                     pluralize(len(self.available_files), "configuration file"))
        return parser

    @mutable_property
    def program_name(self):
        """
        The name of the application whose configuration we're managing (a string).

        The value of this property is used by :attr:`filename_patterns`
        to generate filenames of configuration files and directories.
        """

    @cached_property
    def section_names(self):
        """The names of the available sections (a list of strings)."""
        return sorted(self.parser.sections())

    @mutable_property
    def strict(self):
        """
        Whether to be strict or forgiving when something goes wrong (a boolean).

        When :attr:`strict` is :data:`True` and something goes wrong an
        exception will be raised, whereas if it is :data:`False` (the default)
        a warning message will be logged but no exception is raised.
        """
        return False

    def get_main_pattern(self, directory):
        """
        Get the :func:`~glob.glob()` pattern to find the main configuration file.

        :param directory: The pathname of a base directory (a string).
        :returns: A filename pattern (a string).

        This method generates a pattern that matches a filename based on
        :attr:`program_name` with the suffix :attr:`filename_extension` in the
        given base `directory`. Here's an example:

        >>> from update_dotdee import ConfigLoader
        >>> loader = ConfigLoader(program_name='update-dotdee')
        >>> [loader.get_main_pattern(d) for d in loader.base_directories]
        ['/etc/update-dotdee.ini',
         '~/.update-dotdee.ini',
         '~/.config/update-dotdee.ini']
        """
        return os.path.join(directory, format(
            '{prefix}{program_name}.{extension}',
            extension=self.filename_extension.lstrip('.'),
            program_name=self.program_name,
            prefix=self.get_prefix(directory),
        ))

    def get_modular_pattern(self, directory):
        """
        Get the :func:`~glob.glob()` pattern to find modular configuration files.

        :param directory: The pathname of a base directory (a string).
        :returns: A filename pattern (a string).

        This method generates a pattern that matches a directory whose name is
        based on :attr:`program_name` with the suffix ``.d`` containing files
        matching the configured :attr:`filename_extension`. Here's an example:

        >>> from update_dotdee import ConfigLoader
        >>> loader = ConfigLoader(program_name='update-dotdee')
        >>> [loader.get_modular_pattern(d) for d in loader.base_directories]
        ['/etc/update-dotdee.d/*.ini',
         '~/.update-dotdee.d/*.ini',
         '~/.config/update-dotdee.d/*.ini']
        """
        return os.path.join(directory, format(
            '{prefix}{program_name}.d/*.{extension}',
            extension=self.filename_extension.lstrip('.'),
            program_name=self.program_name,
            prefix=self.get_prefix(directory),
        ))

    def get_options(self, section_name):
        """
        Get the options defined in a specific section.

        :param section_name: The name of the section (a string).
        :returns: A :class:`dict` with options.
        """
        return dict(self.parser.items(section_name))

    def get_prefix(self, directory):
        """
        Get the filename prefix for the given base directory.

        :param directory: The pathname of a directory (a string).
        :returns: The string '.' for the user's profile directory, an empty
                  string otherwise.
        """
        return '.' if directory == '~' else ''

    def report_issue(self, message, *args, **kw):
        """Handle a problem by raising an exception or logging a warning (depending on :attr:`strict`)."""
        if self.strict:
            raise ValueError(format(message, *args, **kw))
        else:
            logger.warning(format(message, *args, **kw))


class RefuseToOverwrite(Exception):

    """Raised when `update-dotdee` notices that a generated file was modified."""


def inject_documentation(**options):
    """
    Generate configuration documentation in reStructuredText_ syntax.

    :param options: Any keyword arguments are passed on to the
                    :class:`ConfigLoader` initializer.

    This methods injects the generated documentation into the output generated
    by cog_.

    .. _cog: https://pypi.python.org/pypi/cogapp
    """
    import cog
    loader = ConfigLoader(**options)
    cog.out("\n" + loader.documentation + "\n\n")
