"""
Basic tests for CodeCompass
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

def test_imports():
    """Test that all modules can be imported."""
    try:
        from core.analyzer import CodeAnalyzer
        from config.settings import Settings
        from utils.safety import PathValidator
        from simple_mcp_server import server
        assert True
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")

def test_simple_mcp_server():
    """Test the simple MCP server."""
    from simple_mcp_server import server, list_tools
    
    # Test that server exists
    assert server is not None
    assert server.name == "codecompass"

def test_settings():
    """Test settings loading."""
    from config.settings import Settings
    
    settings = Settings()
    assert settings.server.name == "CodeCompass"
    assert settings.server.version == "1.0.0"
    assert isinstance(settings.repositories.ignore_patterns, list)

def test_path_validator():
    """Test path validator."""
    from utils.safety import PathValidator
    
    validator = PathValidator(["."])
    assert validator.is_safe_path(".")
    assert not validator.is_safe_path("../")
    assert not validator.is_safe_path("/etc/passwd")
