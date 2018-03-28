# Generic modular configuration file manager.
#
# Author: Peter Odding <peter@peterodding.com>
# Last Change: March 29, 2018
# URL: https://pypi.python.org/pypi/update-dotdee

"""Test suite for `update-dotdee`."""

# Standard library modules.
import os

# External dependencies.
from humanfriendly import dedent
from humanfriendly.testing import MockedHomeDirectory, TemporaryDirectory, TestCase, run_cli

# Modules included in our package.
from update_dotdee import ConfigLoader, UpdateDotDee
from update_dotdee.cli import main


class UpdateDotDeeTestCase(TestCase):

    """:mod:`unittest` compatible container for the `update-dotdee` test suite."""

    def test_cli_usage_message(self):
        """Test the command line usage message."""
        for arguments in [], ['-h'], ['--help']:
            returncode, output = run_cli(main, *arguments)
            assert returncode == 0
            assert "Usage: update-dotdee" in output

    def test_cli_invalid_arguments(self):
        """Test the handling of invalid arguments by the command line interface."""
        for arguments in [], ['-h'], ['--help']:
            returncode, output = run_cli(main, 'first', 'second', merged=True)
            assert returncode != 0
            assert "first and only" in output

    def test_natural_order(self):
        """Verify the natural order sorting of the snippets in the configuration file."""
        first = "This should be the first line.\n"
        middle = "This should appear in the middle.\n"
        last = "This should be the last line.\n"
        with TemporaryDirectory() as temporary_directory:
            filename = os.path.join(temporary_directory, 'config')
            directory = '%s.d' % filename
            # Create the configuration file and directory.
            write_file(filename)
            os.makedirs(directory)
            # Create the files with configuration snippets.
            for number, contents in (1, first), (5, middle), (10, last):
                write_file(os.path.join(directory, '%i.conf' % number), contents)
            # Use the command line interface to update the configuration file.
            returncode, output = run_cli(main, filename)
            assert returncode == 0
            # Make sure the configuration file was updated.
            assert os.path.isfile(filename)
            assert os.path.getsize(filename) > 0
            with open(filename) as handle:
                lines = handle.readlines()
                # Make sure all of the expected lines are present.
                assert first in lines
                assert middle in lines
                assert last in lines
                # Check the order of the lines (natural order instead of lexicographical).
                assert lines.index(first) < lines.index(middle)
                assert lines.index(middle) < lines.index(last)

    def test_executable(self):
        """Test that executable files are run, and non-executable ones aren't."""
        executable = "#!/bin/sh\necho I am echo output.\n"
        exec_result = "I am echo output.\n"
        non_executable = "Don't run me.\n"
        with TemporaryDirectory() as temporary_directory:
            filename = os.path.join(temporary_directory, 'config')
            directory = '%s.d' % filename
            # Create the configuration file and directory.
            write_file(filename)
            os.makedirs(directory)
            # Create the files with configuration snippets.
            write_file(os.path.join(directory, '01-exec.conf'), executable)
            write_file(os.path.join(directory, '02-noexec.conf'), non_executable)
            # Make 01-exec.conf executable and make 02-noexec.conf not.
            os.chmod(os.path.join(directory, '01-exec.conf'), int('755', 8))
            os.chmod(os.path.join(directory, '02-noexec.conf'), int('644', 8))
            # Use the command line interface to update the configuration file.
            returncode, output = run_cli(main, filename)
            assert returncode == 0
            # Make sure the configuration file was updated.
            assert os.path.isfile(filename)
            assert os.path.getsize(filename) > 0
            with open(filename) as handle:
                lines = handle.readlines()
                # Make sure the lines are present.
                assert exec_result in lines
                assert non_executable in lines

    def test_create_directory(self):
        """Test that the ``.d`` directory is created on the first run."""
        expected_contents = "This content should be preserved.\n"
        with TemporaryDirectory() as temporary_directory:
            filename = os.path.join(temporary_directory, 'config')
            directory = '%s.d' % filename
            moved_file = os.path.join(directory, 'local')
            # Create the configuration file.
            write_file(filename, expected_contents)
            # Use the command line interface to initialize the directory.
            returncode, output = run_cli(main, filename)
            assert returncode == 0
            # Make sure the directory was created.
            assert os.path.isdir(directory)
            # Make sure the contents were moved.
            assert os.path.isfile(moved_file)
            # Validate the contents of the configuration file.
            with open(filename) as handle:
                lines = handle.readlines()
                assert lines == [expected_contents]

    def test_refuse_to_overwrite(self):
        """Test that local modifications are not overwritten."""
        with TemporaryDirectory() as temporary_directory:
            filename = os.path.join(temporary_directory, 'config')
            # Create the configuration file and directory.
            write_file(filename, "Original content.\n")
            # Use the command line interface to initialize the directory.
            returncode, output = run_cli(main, filename)
            assert returncode == 0
            # Modify the generated configuration file.
            write_file(filename, "Not the same thing.\n")
            # Use the command line interface to update the configuration file.
            returncode, output = run_cli(main, filename, merged=True)
            assert returncode != 0
            assert "refusing to overwrite" in output

    def test_force_overwrite(self):
        """Test that local modifications can be overwritten when allowed."""
        expected_contents = "Original content.\n"
        with TemporaryDirectory() as temporary_directory:
            filename = os.path.join(temporary_directory, 'config')
            # Create the configuration file and directory.
            write_file(filename, expected_contents)
            # Use the command line interface to initialize the directory.
            returncode, output = run_cli(main, filename)
            assert returncode == 0
            # Modify the generated configuration file.
            write_file(filename, "Not the same thing.\n")
            # Use the command line interface to update the configuration file,
            # overriding the normal sanity check.
            returncode, output = run_cli(main, '--force', filename, merged=True)
            assert returncode == 0
            assert "overwriting anyway" in output
            # Make sure the original content was restored.
            with open(filename) as handle:
                assert handle.read() == expected_contents

    def test_same_checksum(self):
        """Test that old and new checksums are compared correctly."""
        with TemporaryDirectory() as temporary_directory:
            # Create a configuration file to manage.
            filename = os.path.join(temporary_directory, 'config')
            write_file(filename, "Original content.\n")
            # Run update-dotdee the first time to create the checksum file.
            program = UpdateDotDee(filename=filename)
            program.update_file(force=False)
            # Sanity check that the persisted checksum matches a checksum computed at runtime.
            assert program.old_checksum == program.new_checksum

    def test_config_loader(self):
        """Tests for the :class:`ConfigLoader` class."""
        # Test support for custom filename extensions.
        loader = ConfigLoader(program_name='update-dotdee', filename_extension='conf')
        assert '/etc/update-dotdee.conf' in loader.filename_patterns
        # Test loading of multiple configuration files.
        with MockedHomeDirectory() as directory:
            # Create the main user configuration file at ~/.update-dotdee.ini.
            main_file = os.path.join(directory, '.update-dotdee.ini')
            write_file(main_file, dedent('''
                [main-section]
                main-option = value
            '''))
            # Create some modular ~/.config/update-dotdee.d/*.ini configuration files.
            config_directory = os.path.join(directory, '.config', 'update-dotdee.d')
            os.makedirs(config_directory)
            modular_file_1 = os.path.join(config_directory, '1.ini')
            modular_file_2 = os.path.join(config_directory, '2.ini')
            modular_file_11 = os.path.join(config_directory, '11.ini')
            write_file(modular_file_1, dedent('''
                [modular-section-1]
                my-option-name = value
            '''))
            write_file(modular_file_2, dedent('''
                [modular-section-2]
                my-option-name = value

                [main-section]
                modular-option = value
            '''))
            write_file(modular_file_11, dedent('''
                [modular-section-11]
                my-option-name = value
            '''))
            # Use ConfigLoader to load the configuration files.
            loader = ConfigLoader(program_name='update-dotdee')
            # Make sure all configuration files were found.
            assert len(loader.available_files) == 4
            assert loader.available_files[0] == main_file
            assert loader.available_files[1] == modular_file_1
            assert loader.available_files[2] == modular_file_2
            assert loader.available_files[3] == modular_file_11
            # Make sure all configuration file sections are loaded.
            assert set(loader.section_names) == set([
                'main-section',
                'modular-section-1',
                'modular-section-2',
                'modular-section-11',
            ])
            assert loader.get_options('main-section') == {
                'main-option': 'value',
                'modular-option': 'value',
            }


def write_file(filename, contents=''):
    """Shortcut to create files."""
    with open(filename, 'w') as handle:
        handle.write(contents)
