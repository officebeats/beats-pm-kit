
import unittest
from unittest.mock import patch, MagicMock, call
import sys
import os

# Add system/ directory to path so 'from scripts import ...' resolves to system/scripts/
# __file__ = system/tests/test_core_setup.py
# parent  = system/tests/
# parent  = system/   ← this is what we insert
_TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
_SYSTEM_DIR = os.path.dirname(_TESTS_DIR)
sys.path.insert(0, _SYSTEM_DIR)


# Clean up sys.modules to avoid pollution from other tests
for mod in ['utils', 'utils.config', 'scripts.core_setup']:
    if mod in sys.modules:
        del sys.modules[mod]

from scripts import core_setup

class TestCoreSetup(unittest.TestCase):

    @patch('scripts.core_setup.get_required_directories')
    @patch('scripts.core_setup.file_exists')
    @patch('scripts.core_setup.ensure_directory')
    @patch('scripts.core_setup.print_success')
    @patch('scripts.core_setup.print_error')
    def test_create_directories(self, mock_print_error, mock_print_success, mock_ensure_dir, mock_file_exists, mock_get_dirs):
        # Setup
        mock_get_dirs.return_value = ['dir1', 'dir2']
        mock_file_exists.side_effect = [False, True] # dir1 missing, dir2 exists
        mock_ensure_dir.return_value = True

        # Execute
        core_setup.create_directories()

        # Verify
        mock_ensure_dir.assert_called_once_with('dir1')
        mock_print_success.assert_called_once() # For dir1
        mock_print_error.assert_not_called()

    @patch('scripts.core_setup.file_exists')
    @patch('scripts.core_setup.ensure_directory')
    @patch('scripts.core_setup.copy_file')
    @patch('scripts.core_setup.print_success')
    def test_copy_template_file_success(self, mock_print_success, mock_copy, mock_ensure_dir, mock_file_exists):
        # Setup
        mock_file_exists.side_effect = [
            False, # dst exists? No
            False, # target_dir exists? No (so ensure_directory called)
            True   # src exists? Yes
        ]
        mock_copy.return_value = True

        # Execute
        core_setup._copy_template_file('src/tmpl', 'dst/file')

        # Verify
        mock_ensure_dir.assert_called_once_with('dst')
        mock_copy.assert_called_once_with('src/tmpl', 'dst/file')
        mock_print_success.assert_called_once()

    @patch('scripts.core_setup.file_exists')
    def test_copy_template_file_skip_existing(self, mock_file_exists):
        # Setup
        mock_file_exists.return_value = True # dst exists

        # Execute
        with patch('scripts.core_setup.print_gray') as mock_print_gray:
            core_setup._copy_template_file('src/tmpl', 'dst/file')
            mock_print_gray.assert_called_once()

    @patch('scripts.core_setup.get_config')
    @patch('scripts.core_setup._copy_template_file')
    def test_copy_templates(self, mock_copy_helper, mock_get_config):
        # Setup
        mock_get_config.side_effect = lambda key: f"path/to/{key}"

        # Execute
        core_setup.copy_templates()

        # Verify
        self.assertEqual(mock_copy_helper.call_count, 5) # 5 templates defined

    @patch('scripts.core_setup.get_extensions')
    @patch('scripts.core_setup.check_extension_installed')
    @patch('builtins.input')
    @patch('scripts.core_setup.install_extension')
    def test_install_extensions(self, mock_install, mock_input, mock_check_installed, mock_get_extensions):
        # Setup
        mock_get_extensions.return_value = [
            {'id': 'ext1', 'name': 'Extension 1', 'url': 'url1'},
            {'id': 'ext2', 'name': 'Extension 2', 'url': 'url2'}
        ]
        mock_check_installed.side_effect = [True, False] # ext1 installed, ext2 not
        mock_input.return_value = 'y' # User says yes to ext2

        # Execute
        core_setup.install_extensions()

        # Verify
        mock_check_installed.assert_has_calls([call('ext1'), call('ext2')])
        mock_install.assert_called_once_with('ext2', 'Extension 2', 'url2')

    @patch('scripts.core_setup.file_exists')
    @patch('scripts.core_setup.ensure_directory')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_initialize_tracker_file(self, mock_open, mock_ensure_dir, mock_file_exists):
        # Setup
        mock_file_exists.return_value = False # File doesn't exist

        # Execute
        core_setup._initialize_tracker_file('root', 'path/to/tracker.md', '# Header')

        # Verify
        mock_ensure_dir.assert_called_once()
        mock_open.assert_called_once_with(os.path.join('root', 'path/to/tracker.md'), 'w', encoding='utf-8')
        mock_open().write.assert_called_once_with('# Header')

if __name__ == '__main__':
    unittest.main()
