"""Tests for the main module using pytest framework."""

from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from src.enums import APIType
from src.main import APITYPE_TO_FUNCTIONS, main


class TestMain:
    """Test cases for the main module."""

    @pytest.fixture
    def runner(self):
        """Set up CLI test runner."""
        return CliRunner()

    def test_apitype_to_functions_mapping(self):
        """Test that all API types are mapped to functions."""
        # Verify all APIType enum values have corresponding functions
        for api_type in APIType:
            assert api_type in APITYPE_TO_FUNCTIONS
            assert APITYPE_TO_FUNCTIONS[api_type] is not None

    def test_apitype_to_functions_completeness(self):
        """Test that the function mapping is complete and contains only valid APITypes."""
        # Verify mapping keys match APIType enum values
        expected_keys = set(APIType)
        actual_keys = set(APITYPE_TO_FUNCTIONS.keys())
        assert expected_keys == actual_keys

    @patch("src.server.app")
    def test_main_default_options(self, mock_app, runner):
        """Test main function with default options."""
        # Mock get_function to return valid functions
        mock_functions = [(lambda: None, "test_function", "Test description")]

        with patch.dict(APITYPE_TO_FUNCTIONS, {api: lambda: mock_functions for api in APIType}):
            result = runner.invoke(main, [])

        assert result.exit_code == 0
        # Verify app.add_tool was called for each API type
        expected_calls = len(APIType)  # One call per API type
        assert mock_app.add_tool.call_count == expected_calls
        # Verify app.run was called with stdio transport
        mock_app.run.assert_called_once_with(transport="stdio")

    @patch("src.server.app")
    def test_main_sse_transport(self, mock_app, runner):
        """Test main function with SSE transport."""
        mock_functions = [(lambda: None, "test_function", "Test description")]

        with patch.dict(APITYPE_TO_FUNCTIONS, {api: lambda: mock_functions for api in APIType}):
            result = runner.invoke(main, ["--transport", "sse"])

        assert result.exit_code == 0
        mock_app.run.assert_called_once_with(transport="sse")

    @patch("src.server.app")
    def test_main_specific_apis(self, mock_app, runner):
        """Test main function with specific APIs selected."""
        mock_functions = [(lambda: None, "test_function", "Test description")]

        selected_apis = ["config", "connection"]
        with patch.dict(APITYPE_TO_FUNCTIONS, {api: lambda: mock_functions for api in APIType}):
            result = runner.invoke(main, ["--apis", "config", "--apis", "connection"])

        assert result.exit_code == 0
        # Should only add tools for selected APIs
        assert mock_app.add_tool.call_count == len(selected_apis)

    @patch("src.server.app")
    def test_main_not_implemented_error_handling(self, mock_app, runner):
        """Test main function handles NotImplementedError gracefully."""

        def raise_not_implemented():
            raise NotImplementedError("Not implemented")

        # Mock one API to raise NotImplementedError
        modified_mapping = APITYPE_TO_FUNCTIONS.copy()
        modified_mapping[APIType.CONFIG] = raise_not_implemented

        mock_functions = [(lambda: None, "test_function", "Test description")]

        # Other APIs should still work
        for api in APIType:
            if api != APIType.CONFIG:
                modified_mapping[api] = lambda: mock_functions

        with patch.dict(APITYPE_TO_FUNCTIONS, modified_mapping, clear=True):
            result = runner.invoke(main, [])

        assert result.exit_code == 0
        # Should add tools for all APIs except the one that raised NotImplementedError
        expected_calls = len(APIType) - 1
        assert mock_app.add_tool.call_count == expected_calls

    def test_cli_transport_choices(self, runner):
        """Test CLI transport option only accepts valid choices."""
        result = runner.invoke(main, ["--transport", "invalid"])
        assert result.exit_code != 0
        assert "Invalid value for '--transport'" in result.output

    def test_cli_apis_choices(self, runner):
        """Test CLI apis option only accepts valid choices."""
        result = runner.invoke(main, ["--apis", "invalid"])
        assert result.exit_code != 0
        assert "Invalid value for '--apis'" in result.output

    @patch("src.server.app")
    def test_function_registration_flow(self, mock_app, runner):
        """Test the complete function registration flow."""
        mock_function = MagicMock()
        mock_functions = [(mock_function, "test_name", "test_description")]

        with patch.dict(APITYPE_TO_FUNCTIONS, {APIType.CONFIG: lambda: mock_functions}, clear=True):
            result = runner.invoke(main, ["--apis", "config"])

        assert result.exit_code == 0
        mock_app.add_tool.assert_called_once_with(mock_function, name="test_name", description="test_description")

    @patch("src.server.app")
    def test_multiple_functions_per_api(self, mock_app, runner):
        """Test handling multiple functions per API."""
        mock_functions = [
            (lambda: "func1", "func1_name", "func1_desc"),
            (lambda: "func2", "func2_name", "func2_desc"),
            (lambda: "func3", "func3_name", "func3_desc"),
        ]

        with patch.dict(APITYPE_TO_FUNCTIONS, {APIType.CONFIG: lambda: mock_functions}, clear=True):
            result = runner.invoke(main, ["--apis", "config"])

        assert result.exit_code == 0
        # Should register all functions
        assert mock_app.add_tool.call_count == 3

    def test_help_option(self, runner):
        """Test CLI help option."""
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "Transport type" in result.output
        assert "APIs to run" in result.output

    @pytest.mark.parametrize("transport", ["stdio", "sse"])
    @patch("src.server.app")
    def test_main_transport_options(self, mock_app, transport, runner):
        """Test main function with different transport options."""
        mock_functions = [(lambda: None, "test_function", "Test description")]

        with patch.dict(APITYPE_TO_FUNCTIONS, {APIType.CONFIG: lambda: mock_functions}, clear=True):
            result = runner.invoke(main, ["--transport", transport, "--apis", "config"])

        assert result.exit_code == 0
        mock_app.run.assert_called_once_with(transport=transport)

    @pytest.mark.parametrize("api_name", [api.value for api in APIType])
    @patch("src.server.app")
    def test_individual_api_selection(self, mock_app, api_name, runner):
        """Test selecting individual APIs."""
        mock_functions = [(lambda: None, "test_function", "Test description")]

        with patch.dict(APITYPE_TO_FUNCTIONS, {APIType(api_name): lambda: mock_functions}, clear=True):
            result = runner.invoke(main, ["--apis", api_name])

        assert result.exit_code == 0
        assert mock_app.add_tool.call_count == 1
