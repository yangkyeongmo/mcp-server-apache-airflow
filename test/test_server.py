"""Tests for the server module using pytest framework."""

import pytest
from fastmcp import FastMCP
from fastmcp.tools import Tool


class TestServer:
    """Test cases for the server module."""

    def test_app_instance_type(self):
        """Test that app instance is of correct type."""
        from src.server import app

        # Verify app is an instance of FastMCP
        assert isinstance(app, FastMCP)

    def test_app_instance_name(self):
        """Test that app instance has the correct name."""
        from src.server import app

        # Verify the app name is set correctly
        assert app.name == "mcp-apache-airflow"

    def test_app_instance_is_singleton(self):
        """Test that importing the app multiple times returns the same instance."""
        from src.server import app as app1
        from src.server import app as app2

        # Verify same instance is returned
        assert app1 is app2

    def test_app_has_required_methods(self):
        """Test that app instance has required FastMCP methods."""
        from src.server import app

        # Verify essential methods exist
        assert hasattr(app, "add_tool")
        assert hasattr(app, "run")
        assert callable(app.add_tool)
        assert callable(app.run)

    def test_app_initialization_attributes(self):
        """Test that app is properly initialized with default attributes."""
        from src.server import app

        # Verify basic FastMCP attributes
        assert app.name is not None
        assert app.name == "mcp-apache-airflow"

        # Verify app can be used (doesn't raise exceptions on basic operations)
        try:
            # These should not raise exceptions
            str(app)
            repr(app)
        except Exception as e:
            pytest.fail(f"Basic app operations failed: {e}")

    def test_app_name_format(self):
        """Test that app name follows expected format."""
        from src.server import app

        # Verify name format
        assert isinstance(app.name, str)
        assert app.name.startswith("mcp-")
        assert "airflow" in app.name

    @pytest.mark.integration
    def test_app_tool_registration_capability(self):
        """Test that app can register tools without errors."""
        from src.server import app

        # Mock function to register
        def test_tool():
            return "test result"

        # This should not raise an exception
        try:
            app.add_tool(Tool.from_function(test_tool, name="test_tool", description="Test tool"))
        except Exception as e:
            pytest.fail(f"Tool registration failed: {e}")

    def test_app_module_level_initialization(self):
        """Test that app is initialized at module level."""
        # Import should work without any setup
        from src.server import app

        # App should be ready to use immediately
        assert app is not None
        assert hasattr(app, "name")
        assert app.name == "mcp-apache-airflow"
