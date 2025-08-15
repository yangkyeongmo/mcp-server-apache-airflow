"""Tests for the main module using pytest framework."""

from unittest.mock import patch

import pytest
from click.testing import CliRunner

from src.enums import APIType
from src.main import APITYPE_TO_FUNCTIONS, Tool, main


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
        mock_app.run.assert_called_once_with(transport="sse", port=8000, host="0.0.0.0")

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

        def mock_function():
            # .add_tools in FastMCP does not allow adding functions with *args
            # it limits to use Mock and MagicMock
            pass

        mock_functions = [(mock_function, "test_name", "test_description")]

        with patch.dict(APITYPE_TO_FUNCTIONS, {APIType.CONFIG: lambda: mock_functions}, clear=True):
            result = runner.invoke(main, ["--apis", "config"])

        assert result.exit_code == 0
        mock_app.add_tool.assert_called_once_with(
            Tool.from_function(mock_function, name="test_name", description="test_description")
        )

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

    @pytest.mark.parametrize("transport", ["stdio", "sse", "http"])
    @patch("src.server.app")
    def test_main_transport_options(self, mock_app, transport, runner):
        """Test main function with different transport options."""
        mock_functions = [(lambda: None, "test_function", "Test description")]

        with patch.dict(APITYPE_TO_FUNCTIONS, {APIType.CONFIG: lambda: mock_functions}, clear=True):
            result = runner.invoke(main, ["--transport", transport, "--apis", "config"])

        assert result.exit_code == 0
        if transport == "stdio":
            mock_app.run.assert_called_once_with(transport=transport)
        else:
            mock_app.run.assert_called_once_with(transport=transport, port=8000, host="0.0.0.0")

    @pytest.mark.parametrize("transport", ["sse", "http"])
    @pytest.mark.parametrize("port", [None, "12345"])
    @pytest.mark.parametrize("host", [None, "127.0.0.1"])
    @patch("src.server.app")
    def test_port_and_host_options(self, mock_app, transport, port, host, runner):
        """Test that port and host are set for SSE and HTTP transports"""
        mock_functions = [(lambda: None, "test_function", "Test description")]

        with patch.dict(APITYPE_TO_FUNCTIONS, {APIType.CONFIG: lambda: mock_functions}, clear=True):
            ext_params = []
            if port:
                ext_params += ["--mcp-port", port]
            if host:
                ext_params += ["--mcp-host", host]
            runner.invoke(main, ["--transport", transport, "--apis", "config"] + ext_params)

        expected_params = {}
        expected_params["port"] = int(port) if port else 8000
        expected_params["host"] = host if host else "0.0.0.0"
        mock_app.run.assert_called_once_with(transport=transport, **expected_params)

    @pytest.mark.parametrize("api_name", [api.value for api in APIType])
    @patch("src.server.app")
    def test_individual_api_selection(self, mock_app, api_name, runner):
        """Test selecting individual APIs."""
        mock_functions = [(lambda: None, "test_function", "Test description")]

        with patch.dict(APITYPE_TO_FUNCTIONS, {APIType(api_name): lambda: mock_functions}, clear=True):
            result = runner.invoke(main, ["--apis", api_name])

        assert result.exit_code == 0
        assert mock_app.add_tool.call_count == 1

    def test_filter_functions_for_read_only(self):
        """Test that filter_functions_for_read_only correctly filters functions."""
        from src.main import filter_functions_for_read_only

        # Mock function objects
        def mock_read_func():
            pass

        def mock_write_func():
            pass

        # Test functions with mixed read/write status
        functions = [
            (mock_read_func, "get_something", "Get something", True),
            (mock_write_func, "create_something", "Create something", False),
            (mock_read_func, "list_something", "List something", True),
            (mock_write_func, "delete_something", "Delete something", False),
        ]

        filtered = filter_functions_for_read_only(functions)

        # Should only have the read-only functions
        assert len(filtered) == 2
        assert filtered[0][1] == "get_something"
        assert filtered[1][1] == "list_something"

        # Verify all returned functions are read-only
        for _, _, _, is_read_only in filtered:
            assert is_read_only is True

    def test_connection_functions_have_correct_read_only_status(self):
        """Test that connection functions are correctly marked as read-only or write."""
        from src.airflow.connection import get_all_functions

        functions = get_all_functions()
        function_names = {name: is_read_only for _, name, _, is_read_only in functions}

        # Verify read-only functions
        assert function_names["list_connections"] is True
        assert function_names["get_connection"] is True
        assert function_names["test_connection"] is True

        # Verify write functions
        assert function_names["create_connection"] is False
        assert function_names["update_connection"] is False
        assert function_names["delete_connection"] is False

    def test_dag_functions_have_correct_read_only_status(self):
        """Test that DAG functions are correctly marked as read-only or write."""
        from src.airflow.dag import get_all_functions

        functions = get_all_functions()
        function_names = {name: is_read_only for _, name, _, is_read_only in functions}

        # Verify read-only functions
        assert function_names["fetch_dags"] is True
        assert function_names["get_dag"] is True
        assert function_names["get_dag_details"] is True
        assert function_names["get_dag_source"] is True
        assert function_names["get_dag_tasks"] is True
        assert function_names["get_task"] is True
        assert function_names["get_tasks"] is True

        # Verify write functions
        assert function_names["pause_dag"] is False
        assert function_names["unpause_dag"] is False
        assert function_names["patch_dag"] is False
        assert function_names["patch_dags"] is False
        assert function_names["delete_dag"] is False
        assert function_names["clear_task_instances"] is False
        assert function_names["set_task_instances_state"] is False
        assert function_names["reparse_dag_file"] is False

    @patch("src.server.app")
    def test_main_read_only_mode(self, mock_app, runner):
        """Test main function with read-only flag."""
        # Create mock functions with mixed read/write status
        mock_functions = [
            (lambda: None, "read_function", "Read function", True),
            (lambda: None, "write_function", "Write function", False),
            (lambda: None, "another_read_function", "Another read function", True),
        ]

        with patch.dict(APITYPE_TO_FUNCTIONS, {APIType.CONFIG: lambda: mock_functions}, clear=True):
            result = runner.invoke(main, ["--read-only", "--apis", "config"])

        assert result.exit_code == 0
        # Should only register read-only functions (2 out of 3)
        assert mock_app.add_tool.call_count == 2

        # Verify the correct functions were registered
        call_args_list = mock_app.add_tool.call_args_list

        registered_names = [call.args[0].name for call in call_args_list]
        assert "read_function" in registered_names
        assert "another_read_function" in registered_names
        assert "write_function" not in registered_names

    @patch("src.server.app")
    def test_main_read_only_mode_with_no_read_functions(self, mock_app, runner):
        """Test main function with read-only flag when API has no read-only functions."""
        # Create mock functions with only write operations
        mock_functions = [
            (lambda: None, "write_function1", "Write function 1", False),
            (lambda: None, "write_function2", "Write function 2", False),
        ]

        with patch.dict(APITYPE_TO_FUNCTIONS, {APIType.CONFIG: lambda: mock_functions}, clear=True):
            result = runner.invoke(main, ["--read-only", "--apis", "config"])

        assert result.exit_code == 0
        # Should not register any functions
        assert mock_app.add_tool.call_count == 0

    def test_cli_read_only_flag_in_help(self, runner):
        """Test that read-only flag appears in help."""
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "--read-only" in result.output
        assert "Only expose read-only tools" in result.output
