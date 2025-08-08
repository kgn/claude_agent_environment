"""Unit tests for branch handling functionality."""

import unittest
from unittest.mock import patch, MagicMock, call
import tempfile
from pathlib import Path
import sys
import os

from claude_agent_environment.main import clone_or_update_repo


class TestBranchHandling(unittest.TestCase):
    """Test branch creation and checkout functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        self.repo_path = self.test_path / "test-repo"
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    @patch('claude_agent_environment.main.REPO_CONFIGS', {})
    @patch('claude_agent_environment.main.run_command')
    def test_existing_local_branch(self, mock_run_command):
        """Test handling of existing local branch."""
        # Create repo directory to simulate existing repo
        self.repo_path.mkdir(parents=True)
        
        # Mock command responses
        mock_run_command.side_effect = [
            (True, ""),  # git fetch --all
            (True, "  test-branch"),  # git branch --list (branch exists locally)
            (True, "abc123 refs/heads/test-branch"),  # git ls-remote (exists remotely)
            (True, ""),  # git checkout test-branch
            (True, ""),  # git pull origin test-branch
        ]
        
        result = clone_or_update_repo(
            "test-repo",
            "https://github.com/user/test-repo",
            "test-branch",
            self.test_path
        )
        
        self.assertTrue(result)
        
        # Verify correct git commands were called
        calls = mock_run_command.call_args_list
        self.assertIn(
            call("git checkout test-branch", cwd=self.repo_path),
            calls
        )
    
    @patch('claude_agent_environment.main.REPO_CONFIGS', {})
    @patch('claude_agent_environment.main.run_command')
    def test_existing_remote_branch_not_local(self, mock_run_command):
        """Test checking out remote branch that doesn't exist locally."""
        # Create repo directory
        self.repo_path.mkdir(parents=True)
        
        # Mock command responses
        mock_run_command.side_effect = [
            (True, ""),  # git fetch --all
            (True, ""),  # git branch --list (no local branch)
            (True, "abc123 refs/heads/test-branch"),  # git ls-remote (exists remotely)
            (True, ""),  # git checkout -b test-branch origin/test-branch
        ]
        
        result = clone_or_update_repo(
            "test-repo",
            "https://github.com/user/test-repo",
            "test-branch",
            self.test_path
        )
        
        self.assertTrue(result)
        
        # Verify checkout from remote was attempted
        calls = mock_run_command.call_args_list
        self.assertIn(
            call("git checkout -b test-branch origin/test-branch", cwd=self.repo_path),
            calls
        )
    
    @patch('claude_agent_environment.main.REPO_CONFIGS', {})
    @patch('claude_agent_environment.main.run_command')
    def test_create_new_branch(self, mock_run_command):
        """Test creating a new branch that doesn't exist anywhere."""
        # Create repo directory
        self.repo_path.mkdir(parents=True)
        
        # Mock command responses
        mock_run_command.side_effect = [
            (True, ""),  # git fetch --all
            (True, ""),  # git branch --list (no local branch)
            (True, ""),  # git ls-remote (no remote branch)
            (True, ""),  # git checkout main || git checkout master
            (True, ""),  # git pull
            (True, ""),  # git checkout -b test-branch
        ]
        
        result = clone_or_update_repo(
            "test-repo",
            "https://github.com/user/test-repo",
            "test-branch",
            self.test_path
        )
        
        self.assertTrue(result)
        
        # Verify new branch creation
        calls = mock_run_command.call_args_list
        self.assertIn(
            call("git checkout -b test-branch", cwd=self.repo_path),
            calls
        )
    
    @patch('claude_agent_environment.main.REPO_CONFIGS', {})
    @patch('claude_agent_environment.main.run_command')
    def test_branch_creation_failure(self, mock_run_command):
        """Test handling of branch creation failure."""
        # Create repo directory
        self.repo_path.mkdir(parents=True)
        
        # Mock command responses with failure
        mock_run_command.side_effect = [
            (True, ""),  # git fetch --all
            (True, ""),  # git branch --list (no local branch)
            (True, ""),  # git ls-remote (no remote branch)
            (True, ""),  # git checkout main || git checkout master
            (True, ""),  # git pull
            (False, "fatal: A branch named 'test-branch' already exists"),  # git checkout -b fails
        ]
        
        result = clone_or_update_repo(
            "test-repo",
            "https://github.com/user/test-repo",
            "test-branch",
            self.test_path
        )
        
        self.assertFalse(result)
    
    @patch('claude_agent_environment.main.REPO_CONFIGS', {})
    @patch('claude_agent_environment.main.run_command')
    def test_clone_and_create_branch(self, mock_run_command):
        """Test cloning a new repo and creating a branch."""
        # Mock command responses for clone and branch creation
        mock_run_command.side_effect = [
            (True, ""),  # git clone
            (True, ""),  # git branch --list (no local branch)
            (True, ""),  # git ls-remote (no remote branch)
            (True, ""),  # git checkout main || git checkout master
            (True, ""),  # git pull
            (True, ""),  # git checkout -b test-branch
        ]
        
        result = clone_or_update_repo(
            "test-repo",
            "https://github.com/user/test-repo",
            "new-feature",
            self.test_path
        )
        
        self.assertTrue(result)
        
        # Verify clone was called
        calls = mock_run_command.call_args_list
        self.assertEqual(
            calls[0],
            call(f"git clone https://github.com/user/test-repo {self.repo_path}")
        )
    
    @patch('claude_agent_environment.main.REPO_CONFIGS', {'test-repo': {'setup': 'npm install'}})
    @patch('claude_agent_environment.main.run_command')
    def test_setup_command_execution(self, mock_run_command):
        """Test that setup commands are executed after branch setup."""
        # Create repo directory
        self.repo_path.mkdir(parents=True)
        
        # Mock command responses
        mock_run_command.side_effect = [
            (True, ""),  # git fetch --all
            (True, ""),  # git branch --list
            (True, ""),  # git ls-remote
            (True, ""),  # git checkout main || git checkout master
            (True, ""),  # git pull
            (True, ""),  # git checkout -b test-branch
            (True, ""),  # npm install (setup command)
        ]
        
        result = clone_or_update_repo(
            "test-repo",
            "https://github.com/user/test-repo",
            "test-branch",
            self.test_path
        )
        
        self.assertTrue(result)
        
        # Verify setup command was called
        calls = mock_run_command.call_args_list
        self.assertIn(
            call("npm install", cwd=self.repo_path),
            calls
        )


if __name__ == '__main__':
    unittest.main()