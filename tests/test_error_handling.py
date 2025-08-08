"""Unit tests for error handling and user interaction."""

import unittest
from unittest.mock import patch, MagicMock, call
import tempfile
import json
from pathlib import Path
import sys
import os
import argparse

from claude_agent_environment.main import main, initialize_config


class TestErrorHandling(unittest.TestCase):
    """Test error handling and user interaction flows."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        
        # Create a test config file
        self.config = {
            "repositories": {
                "ios": {
                    "url": "https://github.com/TestOrg/ios"
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
    @patch('claude_agent_environment.main.input')
    @patch('sys.argv', ['cae', 'test-branch', 'ios', 'nonexistent', 'backend'])
    def test_invalid_repo_interactive_continue(self, mock_input, mock_check_exists, mock_subprocess, mock_init_config):
        """Test interactive prompt when invalid repo is found - user continues."""
        # Set up mock config
        mock_init_config.return_value = None
        import claude_agent_environment.main as main_module
        main_module.CONFIG = self.config
        main_module.REPO_MAPPING = {name: repo['url'] for name, repo in self.config['repositories'].items()}
        main_module.REPO_CONFIGS = self.config['repositories']
        
        # Mock repo existence checks
        mock_check_exists.side_effect = lambda url: 'nonexistent' not in url
        
        # User chooses to continue
        mock_input.return_value = 'y'
        
        # Mock subprocess for git operations
        mock_subprocess.return_value = MagicMock(
            returncode=0,
            stdout="",
            stderr="",
            check=True
        )
        
        with patch('claude_agent_environment.main.clone_or_update_repo', return_value=True):
            result = main()
        
        # Should continue with valid repos
        self.assertEqual(result, 0)
        mock_input.assert_called_once()
    
    @patch('claude_agent_environment.main.initialize_config')
    @patch('claude_agent_environment.main.subprocess.run')
    @patch('claude_agent_environment.main.check_repo_exists')
    @patch('claude_agent_environment.main.input')
    @patch('sys.argv', ['cae', 'test-branch', 'ios', 'nonexistent', 'backend'])
    def test_invalid_repo_interactive_abort(self, mock_input, mock_check_exists, mock_subprocess, mock_init_config):
        """Test interactive prompt when invalid repo is found - user aborts."""
        # Set up mock config
        mock_init_config.return_value = None
        import claude_agent_environment.main as main_module
        main_module.CONFIG = self.config
        main_module.REPO_MAPPING = {name: repo['url'] for name, repo in self.config['repositories'].items()}
        main_module.REPO_CONFIGS = self.config['repositories']
        
        # Mock repo existence checks
        mock_check_exists.side_effect = lambda url: 'nonexistent' not in url
        
        # User chooses NOT to continue
        mock_input.return_value = 'n'
        
        result = main()
        
        # Should exit with error
        self.assertEqual(result, 1)
        mock_input.assert_called_once()
    
    @patch('claude_agent_environment.main.initialize_config')
    @patch('claude_agent_environment.main.subprocess.run')
    @patch('claude_agent_environment.main.check_repo_exists')
    @patch('sys.argv', ['cae', 'test-branch', 'ios', 'nonexistent', '--continue-on-error'])
    def test_invalid_repo_continue_on_error_flag(self, mock_check_exists, mock_subprocess, mock_init_config):
        """Test --continue-on-error flag bypasses interactive prompt."""
        # Set up mock config
        mock_init_config.return_value = None
        import claude_agent_environment.main as main_module
        main_module.CONFIG = self.config
        main_module.REPO_MAPPING = {name: repo['url'] for name, repo in self.config['repositories'].items()}
        main_module.REPO_CONFIGS = self.config['repositories']
        
        # Mock repo existence checks
        mock_check_exists.side_effect = lambda url: 'nonexistent' not in url
        
        # Mock subprocess for git operations
        mock_subprocess.return_value = MagicMock(
            returncode=0,
            stdout="",
            stderr="",
            check=True
        )
        
        with patch('claude_agent_environment.main.clone_or_update_repo', return_value=True):
            with patch('claude_agent_environment.main.input') as mock_input:
                result = main()
        
        # Should not prompt user
        mock_input.assert_not_called()
        # Should succeed with valid repos only
        self.assertEqual(result, 0)
    
    @patch('claude_agent_environment.main.initialize_config')
    @patch('claude_agent_environment.main.check_repo_exists')
    @patch('sys.argv', ['cae', 'test-branch', 'nonexistent1', 'nonexistent2'])
    def test_all_repos_invalid(self, mock_check_exists, mock_init_config):
        """Test when all repositories are invalid."""
        # Set up mock config
        mock_init_config.return_value = None
        import claude_agent_environment.main as main_module
        main_module.CONFIG = self.config
        main_module.REPO_MAPPING = {name: repo['url'] for name, repo in self.config['repositories'].items()}
        main_module.REPO_CONFIGS = self.config['repositories']
        
        # All repos are invalid
        mock_check_exists.return_value = False
        
        result = main()
        
        # Should exit with error
        self.assertEqual(result, 1)
    
    @patch('claude_agent_environment.main.initialize_config')
    @patch('claude_agent_environment.main.clone_or_update_repo')
    @patch('claude_agent_environment.main.check_repo_exists')
    @patch('sys.argv', ['cae', 'test-branch', 'ios', 'backend'])
    def test_partial_setup_failure(self, mock_check_exists, mock_clone, mock_init_config):
        """Test when some repos succeed and others fail during setup."""
        # Set up mock config
        mock_init_config.return_value = None
        import claude_agent_environment.main as main_module
        main_module.CONFIG = self.config
        main_module.REPO_MAPPING = {name: repo['url'] for name, repo in self.config['repositories'].items()}
        main_module.REPO_CONFIGS = self.config['repositories']
        
        # All repos exist
        mock_check_exists.return_value = True
        
        # First repo succeeds, second fails
        mock_clone.side_effect = [True, False]
        
        result = main()
        
        # Should exit with warning
        self.assertEqual(result, 1)
    
    @patch('claude_agent_environment.main.initialize_config')
    @patch('claude_agent_environment.main.clone_or_update_repo')
    @patch('claude_agent_environment.main.check_repo_exists')
    @patch('claude_agent_environment.main.subprocess.run')
    @patch('sys.argv', ['cae', 'test-branch', 'ios'])
    def test_successful_setup(self, mock_subprocess, mock_check_exists, mock_clone, mock_init_config):
        """Test successful repository setup."""
        # Set up mock config
        mock_init_config.return_value = None
        import claude_agent_environment.main as main_module
        main_module.CONFIG = self.config
        main_module.REPO_MAPPING = {name: repo['url'] for name, repo in self.config['repositories'].items()}
        main_module.REPO_CONFIGS = self.config['repositories']
        
        # Repo exists
        mock_check_exists.return_value = True
        
        # Clone succeeds
        mock_clone.return_value = True
        
        # Mock Claude CLI check
        mock_subprocess.side_effect = [
            MagicMock(returncode=1)  # Claude not found
        ]
        
        result = main()
        
        # Should succeed
        self.assertEqual(result, 0)


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions."""
    
    @patch('claude_agent_environment.main.CONFIG', {
        'repositories': {
            'repo1': {'url': 'https://github.com/TestOrg/repo1'},
            'repo2': {'url': 'https://github.com/TestOrg/repo2'}
        }
    })
    def test_get_org_from_repos(self):
        """Test extracting organization from repository URLs."""
        from claude_agent_environment.main import get_org_from_repos
        
        repos = {
            'repo1': {'url': 'https://github.com/TestOrg/repo1'},
            'repo2': {'url': 'https://github.com/TestOrg/repo2'}
        }
        
        org = get_org_from_repos(repos)
        self.assertEqual(org, 'TestOrg')
    
    def test_extract_ticket_id(self):
        """Test extracting Linear ticket ID from branch names."""
        from claude_agent_environment.main import extract_ticket_id
        
        # Test various branch name formats
        test_cases = [
            ('eng-346-implement-feature', 'ENG-346'),
            ('kgn/eng-348-security-review', 'ENG-348'),
            ('feature/des-100-design', 'DES-100'),
            ('ENG-500', 'ENG-500'),
            ('feature-branch', None),
            ('main', None),
        ]
        
        with patch('claude_agent_environment.main.CONFIG', {'ticket_prefixes': ['eng', 'des', 'ops']}):
            for branch_name, expected in test_cases:
                result = extract_ticket_id(branch_name)
                self.assertEqual(result, expected, f"Failed for branch: {branch_name}")


if __name__ == '__main__':
    unittest.main()