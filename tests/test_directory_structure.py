"""Unit tests for directory structure creation."""

import unittest
from unittest.mock import patch, MagicMock, call
import tempfile
import json
from pathlib import Path
import sys
import os
import argparse

from claude_agent_environment.main import main, initialize_config


class TestDirectoryStructure(unittest.TestCase):
    """Test directory structure creation in current working directory."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        
        # Create a test config file
        self.config = {
            "repositories": {
                "frontend": {
                    "url": "https://github.com/TestOrg/frontend"
                },
                "backend": {
                    "url": "https://github.com/TestOrg/backend"
                }
            }
        }
        
        config_path = self.test_path / "cae_config.json"
        with open(config_path, 'w') as f:
            json.dump(self.config, f)
            
        # Change to test directory
        self.original_cwd = os.getcwd()
        os.chdir(self.test_path)
        
    def tearDown(self):
        """Clean up test fixtures."""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    @patch('claude_agent_environment.main.initialize_config')
    @patch('claude_agent_environment.main.subprocess.run')
    @patch('claude_agent_environment.main.check_repo_exists')
    @patch('claude_agent_environment.main.clone_or_update_repo')
    @patch('sys.argv', ['cae', 'test-branch', 'frontend', 'backend'])
    def test_branch_directory_created_in_cwd(self, mock_clone, mock_check_exists, mock_subprocess, mock_init_config):
        """Test that branch directory is created in current working directory."""
        # Set up mock config
        mock_init_config.return_value = None
        import claude_agent_environment.main as main_module
        main_module.CONFIG = self.config
        main_module.REPO_MAPPING = {name: repo['url'] for name, repo in self.config['repositories'].items()}
        main_module.REPO_CONFIGS = self.config['repositories']
        
        # All repos exist and clone successfully
        mock_check_exists.return_value = True
        mock_clone.return_value = True
        
        # Mock Claude CLI not found
        mock_subprocess.side_effect = FileNotFoundError()
        
        result = main()
        
        # Should succeed
        self.assertEqual(result, 0)
        
        # Verify branch directory was created in current working directory
        expected_dir = self.test_path / "test-branch"
        self.assertTrue(expected_dir.exists())
        self.assertTrue(expected_dir.is_dir())
        
        # Verify CLAUDE.md was created in the branch directory
        claude_file = expected_dir / "CLAUDE.md"
        self.assertTrue(claude_file.exists())
    
    @patch('claude_agent_environment.main.initialize_config')
    @patch('claude_agent_environment.main.subprocess.run')
    @patch('claude_agent_environment.main.check_repo_exists')
    @patch('claude_agent_environment.main.clone_or_update_repo')
    @patch('sys.argv', ['cae', 'feature/new-feature', 'frontend'])
    def test_slash_in_branch_name_converted(self, mock_clone, mock_check_exists, mock_subprocess, mock_init_config):
        """Test that slashes in branch names are converted to hyphens for directory names."""
        # Set up mock config
        mock_init_config.return_value = None
        import claude_agent_environment.main as main_module
        main_module.CONFIG = self.config
        main_module.REPO_MAPPING = {name: repo['url'] for name, repo in self.config['repositories'].items()}
        main_module.REPO_CONFIGS = self.config['repositories']
        
        # Repo exists and clones successfully
        mock_check_exists.return_value = True
        mock_clone.return_value = True
        
        # Mock Claude CLI not found
        mock_subprocess.side_effect = FileNotFoundError()
        
        result = main()
        
        # Should succeed
        self.assertEqual(result, 0)
        
        # Verify directory name has slash converted to hyphen
        expected_dir = self.test_path / "feature-new-feature"
        self.assertTrue(expected_dir.exists())
        self.assertTrue(expected_dir.is_dir())
        
        # Should NOT create a directory with slash
        invalid_dir = self.test_path / "feature/new-feature"
        self.assertFalse(invalid_dir.exists())
    
    @patch('claude_agent_environment.main.initialize_config')
    @patch('claude_agent_environment.main.subprocess.run')
    @patch('claude_agent_environment.main.check_repo_exists')
    @patch('claude_agent_environment.main.clone_or_update_repo')
    @patch('sys.argv', ['cae', 'test-branch', 'frontend', 'backend'])
    def test_repositories_cloned_to_branch_directory(self, mock_clone, mock_check_exists, mock_subprocess, mock_init_config):
        """Test that repositories are cloned into the branch directory, not cwd."""
        # Set up mock config
        mock_init_config.return_value = None
        import claude_agent_environment.main as main_module
        main_module.CONFIG = self.config
        main_module.REPO_MAPPING = {name: repo['url'] for name, repo in self.config['repositories'].items()}
        main_module.REPO_CONFIGS = self.config['repositories']
        
        # All repos exist
        mock_check_exists.return_value = True
        mock_clone.return_value = True
        
        # Mock Claude CLI not found
        mock_subprocess.side_effect = FileNotFoundError()
        
        result = main()
        
        # Should succeed
        self.assertEqual(result, 0)
        
        # Verify clone_or_update_repo was called with correct base_dir
        # Use resolve() to handle /private symlink on macOS
        expected_base_dir = (self.test_path / "test-branch").resolve()
        
        # Check that both repos were cloned to the branch directory
        calls = mock_clone.call_args_list
        self.assertEqual(len(calls), 2)
        
        # First repo
        self.assertEqual(calls[0][0][0], "frontend")  # repo name
        self.assertEqual(calls[0][0][3].resolve(), expected_base_dir)  # base_dir
        
        # Second repo
        self.assertEqual(calls[1][0][0], "backend")  # repo name
        self.assertEqual(calls[1][0][3].resolve(), expected_base_dir)  # base_dir
    
    @patch('claude_agent_environment.main.initialize_config')
    @patch('claude_agent_environment.main.subprocess.run')
    @patch('claude_agent_environment.main.check_repo_exists')
    @patch('claude_agent_environment.main.clone_or_update_repo')
    @patch('claude_agent_environment.main.os.chdir')
    @patch('sys.argv', ['cae', 'test-branch', 'frontend'])
    def test_changes_to_branch_directory_before_launching_claude(self, mock_chdir, mock_clone, mock_check_exists, mock_subprocess, mock_init_config):
        """Test that the script changes to the branch directory before launching Claude."""
        # Set up mock config
        mock_init_config.return_value = None
        import claude_agent_environment.main as main_module
        main_module.CONFIG = self.config
        main_module.REPO_MAPPING = {name: repo['url'] for name, repo in self.config['repositories'].items()}
        main_module.REPO_CONFIGS = self.config['repositories']
        
        # Repo exists and clones successfully
        mock_check_exists.return_value = True
        mock_clone.return_value = True
        
        # Mock Claude CLI found and runs
        mock_subprocess.return_value = MagicMock(returncode=0)
        
        result = main()
        
        # Should succeed
        self.assertEqual(result, 0)
        
        # Verify os.chdir was called with the branch directory
        # Use resolve() to handle /private symlink on macOS
        expected_dir = (self.test_path / "test-branch").resolve()
        actual_call = mock_chdir.call_args[0][0].resolve() if mock_chdir.called else None
        self.assertEqual(actual_call, expected_dir)
    
    @patch('claude_agent_environment.main.initialize_config')
    @patch('claude_agent_environment.main.subprocess.run')
    @patch('claude_agent_environment.main.check_repo_exists')
    @patch('claude_agent_environment.main.clone_or_update_repo')
    @patch('sys.argv', ['cae', 'existing-branch', 'frontend'])
    def test_existing_branch_directory_reused(self, mock_clone, mock_check_exists, mock_subprocess, mock_init_config):
        """Test that existing branch directories are reused, not recreated."""
        # Set up mock config
        mock_init_config.return_value = None
        import claude_agent_environment.main as main_module
        main_module.CONFIG = self.config
        main_module.REPO_MAPPING = {name: repo['url'] for name, repo in self.config['repositories'].items()}
        main_module.REPO_CONFIGS = self.config['repositories']
        
        # Create existing branch directory with a test file
        branch_dir = self.test_path / "existing-branch"
        branch_dir.mkdir(parents=True)
        test_file = branch_dir / "existing-file.txt"
        test_file.write_text("This file should persist")
        
        # Repo exists and clones successfully
        mock_check_exists.return_value = True
        mock_clone.return_value = True
        
        # Mock Claude CLI not found
        mock_subprocess.side_effect = FileNotFoundError()
        
        result = main()
        
        # Should succeed
        self.assertEqual(result, 0)
        
        # Verify the existing file is still there
        self.assertTrue(test_file.exists())
        self.assertEqual(test_file.read_text(), "This file should persist")
        
        # Verify CLAUDE.md was created/updated
        claude_file = branch_dir / "CLAUDE.md"
        self.assertTrue(claude_file.exists())


if __name__ == '__main__':
    unittest.main()