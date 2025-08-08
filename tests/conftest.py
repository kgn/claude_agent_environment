"""Pytest configuration and fixtures."""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up test configuration before importing main module
import claude_agent_environment.main as main_module

@pytest.fixture(autouse=True)
def setup_test_config():
    """Automatically set up test configuration for all tests."""
    # Save original values
    original_config = main_module.CONFIG
    original_mapping = main_module.REPO_MAPPING
    original_configs = main_module.REPO_CONFIGS
    
    # Set test values
    main_module.CONFIG = {'repositories': {}}
    main_module.REPO_MAPPING = {}
    main_module.REPO_CONFIGS = {}
    
    yield
    
    # Restore original values
    main_module.CONFIG = original_config
    main_module.REPO_MAPPING = original_mapping
    main_module.REPO_CONFIGS = original_configs