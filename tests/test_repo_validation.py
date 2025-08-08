"""Unit tests for repository validation functionality."""

import unittest
from unittest.mock import patch, MagicMock
import tempfile
import json
from pathlib import Path
import sys
import os

from claude_agent_environment.main import check_repo_exists, clone_or_update_repo, run_command


class TestRepoValidation(unittest.TestCase):
    """Test repository validation and existence checking."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    @patch('claude_agent_environment.main.run_command')
    def test_check_repo_exists_valid(self, mock_run_command):
        """Test checking if a valid repository exists."""
        mock_run_command.return_value = (True, "ref: refs/heads/main")
        
        result = check_repo_exists("https://github.com/user/repo")
        
        self.assertTrue(result)
        mock_run_command.assert_called_once_with(
            "git ls-remote https://github.com/user/repo HEAD"
        )
    
    @patch('claude_agent_environment.main.run_command')
    def test_check_repo_exists_invalid(self, mock_run_command):
        """Test checking if an invalid repository exists."""
        mock_run_command.return_value = (False, "Repository not found")
        
        result = check_repo_exists("https://github.com/user/nonexistent")
        
        self.assertFalse(result)
    
    @patch('claude_agent_environment.main.run_command')
    @patch('claude_agent_environment.main.REPO_CONFIGS', {})
    def test_clone_repo_not_found(self, mock_run_command):
        """Test cloning a repository that doesn't exist."""
        # Mock git clone failure with 404 error
        mock_run_command.side_effect = [
            (False, "ERROR: Repository not found.\nfatal: Could not read from remote repository.")
        ]
        
        result = clone_or_update_repo(
            "nonexistent", 
            "https://github.com/user/nonexistent",
            "test-branch",
            self.test_path
        )
        
        self.assertFalse(result)
        # Verify git clone was attempted
        mock_run_command.assert_called_with(
            f"git clone https://github.com/user/nonexistent {self.test_path / 'nonexistent'}"
        )
    
    @patch('claude_agent_environment.main.run_command')
    @patch('claude_agent_environment.main.REPO_CONFIGS', {})
    def test_clone_repo_other_error(self, mock_run_command):
        """Test cloning a repository with non-404 error."""
        # Mock git clone failure with non-404 error
        mock_run_command.side_effect = [
            (False, "fatal: Authentication failed")
        ]
        
        result = clone_or_update_repo(
            "private-repo",
            "https://github.com/user/private-repo", 
            "test-branch",
            self.test_path
        )
        
        self.assertFalse(result)
    
    @patch('claude_agent_environment.main.run_command')
    @patch('claude_agent_environment.main.REPO_MAPPING', {'configured-repo': 'https://github.com/org/configured'})
    @patch('claude_agent_environment.main.REPO_CONFIGS', {})
    def test_clone_configured_repo_message(self, mock_run_command):
        """Test that configured repos don't show 'not in config' message."""
        # Mock git clone failure with 404 error for a non-configured repo
        mock_run_command.side_effect = [
            (False, "ERROR: Repository not found")
        ]
        
        # This repo is NOT in REPO_MAPPING, so should show the note
        result = clone_or_update_repo(
            "unconfigured-repo",
            "https://github.com/org/unconfigured",
            "test-branch", 
            self.test_path
        )
        
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()