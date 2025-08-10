#!/usr/bin/env python3

import json
import pytest
from unittest.mock import patch, MagicMock
from urllib.error import URLError

from claude_agent_environment.version_check import (
    get_current_version,
    get_latest_version,
    check_for_update,
    display_update_notice
)


def test_get_current_version():
    """Test that we can get the current version."""
    version = get_current_version()
    assert version is not None
    assert isinstance(version, str)
    assert len(version) > 0


@patch('claude_agent_environment.version_check.urlopen')
def test_get_latest_version_success(mock_urlopen):
    """Test fetching latest version from GitHub."""
    # Mock successful response
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({
        "tag_name": "v2.0.0"
    }).encode('utf-8')
    mock_urlopen.return_value.__enter__.return_value = mock_response
    
    version = get_latest_version()
    assert version == "2.0.0"


@patch('claude_agent_environment.version_check.urlopen')
def test_get_latest_version_failure(mock_urlopen):
    """Test handling of network failures."""
    # Mock network error
    mock_urlopen.side_effect = URLError("Network error")
    
    version = get_latest_version()
    assert version is None


@patch('claude_agent_environment.version_check.get_current_version')
@patch('claude_agent_environment.version_check.get_latest_version')
def test_check_for_update_available(mock_latest, mock_current):
    """Test when an update is available."""
    mock_current.return_value = "1.0.0"
    mock_latest.return_value = "2.0.0"
    
    result = check_for_update()
    assert result is not None
    assert result["update_available"] is True
    assert result["current"] == "1.0.0"
    assert result["latest"] == "2.0.0"


@patch('claude_agent_environment.version_check.get_current_version')
@patch('claude_agent_environment.version_check.get_latest_version')
def test_check_for_update_not_available(mock_latest, mock_current):
    """Test when no update is available."""
    mock_current.return_value = "2.0.0"
    mock_latest.return_value = "2.0.0"
    
    result = check_for_update()
    assert result is not None
    assert result["update_available"] is False
    assert result["current"] == "2.0.0"
    assert result["latest"] == "2.0.0"


@patch('claude_agent_environment.version_check.get_current_version')
@patch('claude_agent_environment.version_check.get_latest_version')
def test_check_for_update_network_failure(mock_latest, mock_current):
    """Test handling of network failures during update check."""
    mock_current.return_value = "1.0.0"
    mock_latest.return_value = None  # Simulates network failure
    
    result = check_for_update()
    assert result is None


@patch('claude_agent_environment.version_check.check_for_update')
@patch('builtins.print')
def test_display_update_notice_with_update(mock_print, mock_check):
    """Test displaying update notice when update is available."""
    mock_check.return_value = {
        "current": "1.0.0",
        "latest": "2.0.0",
        "update_available": True
    }
    
    display_update_notice()
    
    # Check that update notice was printed
    calls = [str(call) for call in mock_print.call_args_list]
    assert any("new version" in str(call).lower() for call in calls)
    assert any("1.0.0" in str(call) for call in calls)
    assert any("2.0.0" in str(call) for call in calls)


@patch('claude_agent_environment.version_check.check_for_update')
@patch('builtins.print')
def test_display_update_notice_no_update(mock_print, mock_check):
    """Test no notice when update is not available."""
    mock_check.return_value = {
        "current": "2.0.0",
        "latest": "2.0.0",
        "update_available": False
    }
    
    display_update_notice()
    
    # Check that no update notice was printed
    mock_print.assert_not_called()


@patch('claude_agent_environment.version_check.check_for_update')
@patch('builtins.print')
def test_display_update_notice_check_failed(mock_print, mock_check):
    """Test no notice when update check fails."""
    mock_check.return_value = None
    
    display_update_notice()
    
    # Check that no update notice was printed
    mock_print.assert_not_called()