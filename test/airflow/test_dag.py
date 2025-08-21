"""Table-driven tests for the dag module using pytest framework."""

from unittest.mock import ANY, MagicMock, patch

import mcp.types as types
import pytest

from src.airflow.dag import (
    clear_task_instances,
    delete_dag,
    get_dag,
    get_dag_details,
    get_dag_source,
    get_dag_tasks,
    get_dag_url,
    get_dags,
    get_task,
    get_tasks,
    patch_dag,
    pause_dag,
    reparse_dag_file,
    set_task_instances_state,
    unpause_dag,
)


class TestDagModule:
    """Table-driven test cases for the dag module."""

    @pytest.fixture
    def mock_dag_api(self):
        """Create a mock DAG API instance."""
        with patch("src.airflow.dag.dag_api") as mock_api:
            yield mock_api

    def test_get_dag_url(self):
        """Test DAG URL generation."""
        test_cases = [
            # (dag_id, expected_url)
            ("test_dag", "http://localhost:8080/dags/test_dag/grid"),
            ("my-complex_dag.v2", "http://localhost:8080/dags/my-complex_dag.v2/grid"),
            ("", "http://localhost:8080/dags//grid"),
        ]

        for dag_id, expected_url in test_cases:
            with patch("src.airflow.dag.AIRFLOW_HOST", "http://localhost:8080"):
                result = get_dag_url(dag_id)
                assert result == expected_url

    @pytest.mark.parametrize(
        "test_case",
        [
            # Test case structure: (input_params, mock_response_dict, expected_result_partial)
            {
                "name": "get_dags_no_params",
                "input": {},
                "mock_response": {"dags": [{"dag_id": "test_dag", "description": "Test"}], "total_entries": 1},
                "expected_call_kwargs": {},
                "expected_ui_urls": True,
            },
            {
                "name": "get_dags_with_limit_offset",
                "input": {"limit": 10, "offset": 5},
                "mock_response": {"dags": [{"dag_id": "dag1"}, {"dag_id": "dag2"}], "total_entries": 2},
                "expected_call_kwargs": {"limit": 10, "offset": 5},
                "expected_ui_urls": True,
            },
            {
                "name": "get_dags_with_filters",
                "input": {"tags": ["prod", "daily"], "only_active": True, "paused": False, "dag_id_pattern": "prod_*"},
                "mock_response": {"dags": [{"dag_id": "prod_dag1"}], "total_entries": 1},
                "expected_call_kwargs": {
                    "tags": ["prod", "daily"],
                    "only_active": True,
                    "paused": False,
                    "dag_id_pattern": "prod_*",
                },
                "expected_ui_urls": True,
            },
        ],
    )
    async def test_get_dags_table_driven(self, test_case, mock_dag_api):
        """Table-driven test for get_dags function."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.to_dict.return_value = test_case["mock_response"]
        mock_dag_api.get_dags.return_value = mock_response

        # Execute function
        with patch("src.airflow.dag.AIRFLOW_HOST", "http://localhost:8080"):
            result = await get_dags(**test_case["input"])

        # Verify API call
        mock_dag_api.get_dags.assert_called_once_with(**test_case["expected_call_kwargs"])

        # Verify result structure
        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)

        # Parse result and verify UI URLs were added if expected
        if test_case["expected_ui_urls"]:
            result_text = result[0].text
            assert "ui_url" in result_text

    @pytest.mark.parametrize(
        "test_case",
        [
            {
                "name": "get_dag_basic",
                "input": {"dag_id": "test_dag"},
                "mock_response": {"dag_id": "test_dag", "description": "Test DAG", "is_paused": False},
                "expected_call_kwargs": {"dag_id": "test_dag"},
            },
            {
                "name": "get_dag_complex_id",
                "input": {"dag_id": "complex-dag_name.v2"},
                "mock_response": {"dag_id": "complex-dag_name.v2", "description": "Complex DAG", "is_paused": True},
                "expected_call_kwargs": {"dag_id": "complex-dag_name.v2"},
            },
        ],
    )
    async def test_get_dag_table_driven(self, test_case, mock_dag_api):
        """Table-driven test for get_dag function."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.to_dict.return_value = test_case["mock_response"]
        mock_dag_api.get_dag.return_value = mock_response

        # Execute function
        with patch("src.airflow.dag.AIRFLOW_HOST", "http://localhost:8080"):
            result = await get_dag(**test_case["input"])

        # Verify API call
        mock_dag_api.get_dag.assert_called_once_with(**test_case["expected_call_kwargs"])

        # Verify result structure and UI URL addition
        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert "ui_url" in result[0].text

    @pytest.mark.parametrize(
        "test_case",
        [
            {
                "name": "get_dag_details_no_fields",
                "input": {"dag_id": "test_dag"},
                "mock_response": {"dag_id": "test_dag", "file_path": "/path/to/dag.py"},
                "expected_call_kwargs": {"dag_id": "test_dag"},
            },
            {
                "name": "get_dag_details_with_fields",
                "input": {"dag_id": "test_dag", "fields": ["dag_id", "description"]},
                "mock_response": {"dag_id": "test_dag", "description": "Test"},
                "expected_call_kwargs": {"dag_id": "test_dag", "fields": ["dag_id", "description"]},
            },
        ],
    )
    async def test_get_dag_details_table_driven(self, test_case, mock_dag_api):
        """Table-driven test for get_dag_details function."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.to_dict.return_value = test_case["mock_response"]
        mock_dag_api.get_dag_details.return_value = mock_response

        # Execute function
        result = await get_dag_details(**test_case["input"])

        # Verify API call and result
        mock_dag_api.get_dag_details.assert_called_once_with(**test_case["expected_call_kwargs"])
        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)

    @pytest.mark.parametrize(
        "test_case",
        [
            {
                "name": "pause_dag",
                "function": pause_dag,
                "input": {"dag_id": "test_dag"},
                "mock_response": {"dag_id": "test_dag", "is_paused": True},
                "expected_call_kwargs": {"dag_id": "test_dag", "dag": ANY, "update_mask": ["is_paused"]},
                "expected_dag_is_paused": True,
            },
            {
                "name": "unpause_dag",
                "function": unpause_dag,
                "input": {"dag_id": "test_dag"},
                "mock_response": {"dag_id": "test_dag", "is_paused": False},
                "expected_call_kwargs": {"dag_id": "test_dag", "dag": ANY, "update_mask": ["is_paused"]},
                "expected_dag_is_paused": False,
            },
        ],
    )
    async def test_pause_unpause_dag_table_driven(self, test_case, mock_dag_api):
        """Table-driven test for pause_dag and unpause_dag functions."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.to_dict.return_value = test_case["mock_response"]
        mock_dag_api.patch_dag.return_value = mock_response

        # Execute function
        result = await test_case["function"](**test_case["input"])

        # Verify API call and result
        mock_dag_api.patch_dag.assert_called_once_with(**test_case["expected_call_kwargs"])

        # Verify the DAG object has correct is_paused value
        actual_call_args = mock_dag_api.patch_dag.call_args
        actual_dag = actual_call_args.kwargs["dag"]
        assert actual_dag["is_paused"] == test_case["expected_dag_is_paused"]

        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)

    @pytest.mark.parametrize(
        "test_case",
        [
            {
                "name": "get_tasks_no_order",
                "input": {"dag_id": "test_dag"},
                "mock_response": {
                    "tasks": [
                        {"task_id": "task1", "operator": "BashOperator"},
                        {"task_id": "task2", "operator": "PythonOperator"},
                    ]
                },
                "expected_call_kwargs": {"dag_id": "test_dag"},
            },
            {
                "name": "get_tasks_with_order",
                "input": {"dag_id": "test_dag", "order_by": "task_id"},
                "mock_response": {
                    "tasks": [
                        {"task_id": "task1", "operator": "BashOperator"},
                        {"task_id": "task2", "operator": "PythonOperator"},
                    ]
                },
                "expected_call_kwargs": {"dag_id": "test_dag", "order_by": "task_id"},
            },
        ],
    )
    async def test_get_tasks_table_driven(self, test_case, mock_dag_api):
        """Table-driven test for get_tasks function."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.to_dict.return_value = test_case["mock_response"]
        mock_dag_api.get_tasks.return_value = mock_response

        # Execute function
        result = await get_tasks(**test_case["input"])

        # Verify API call and result
        mock_dag_api.get_tasks.assert_called_once_with(**test_case["expected_call_kwargs"])
        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)

    @pytest.mark.parametrize(
        "test_case",
        [
            {
                "name": "patch_dag_pause_only",
                "input": {"dag_id": "test_dag", "is_paused": True},
                "mock_response": {"dag_id": "test_dag", "is_paused": True},
                "expected_update_mask": ["is_paused"],
            },
            {
                "name": "patch_dag_tags_only",
                "input": {"dag_id": "test_dag", "tags": ["prod", "daily"]},
                "mock_response": {"dag_id": "test_dag", "tags": ["prod", "daily"]},
                "expected_update_mask": ["tags"],
            },
            {
                "name": "patch_dag_both_fields",
                "input": {"dag_id": "test_dag", "is_paused": False, "tags": ["dev"]},
                "mock_response": {"dag_id": "test_dag", "is_paused": False, "tags": ["dev"]},
                "expected_update_mask": ["is_paused", "tags"],
            },
        ],
    )
    async def test_patch_dag_table_driven(self, test_case, mock_dag_api):
        """Table-driven test for patch_dag function."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.to_dict.return_value = test_case["mock_response"]
        mock_dag_api.patch_dag.return_value = mock_response

        # Execute function
        with patch("src.airflow.dag.DAG") as mock_dag_class:
            mock_dag_instance = MagicMock()
            mock_dag_class.return_value = mock_dag_instance

            result = await patch_dag(**test_case["input"])

            # Verify DAG instance creation and API call
            expected_update_request = {k: v for k, v in test_case["input"].items() if k != "dag_id"}
            mock_dag_class.assert_called_once_with(**expected_update_request)

            mock_dag_api.patch_dag.assert_called_once_with(
                dag_id=test_case["input"]["dag_id"],
                dag=mock_dag_instance,
                update_mask=test_case["expected_update_mask"],
            )

        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)

    @pytest.mark.parametrize(
        "test_case",
        [
            {
                "name": "clear_task_instances_minimal",
                "input": {"dag_id": "test_dag"},
                "mock_response": {"message": "Task instances cleared"},
                "expected_clear_request": {},
            },
            {
                "name": "clear_task_instances_full",
                "input": {
                    "dag_id": "test_dag",
                    "task_ids": ["task1", "task2"],
                    "start_date": "2023-01-01",
                    "end_date": "2023-01-31",
                    "include_subdags": True,
                    "include_upstream": True,
                    "dry_run": True,
                },
                "mock_response": {"message": "Dry run completed"},
                "expected_clear_request": {
                    "task_ids": ["task1", "task2"],
                    "start_date": "2023-01-01",
                    "end_date": "2023-01-31",
                    "include_subdags": True,
                    "include_upstream": True,
                    "dry_run": True,
                },
            },
        ],
    )
    async def test_clear_task_instances_table_driven(self, test_case, mock_dag_api):
        """Table-driven test for clear_task_instances function."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.to_dict.return_value = test_case["mock_response"]
        mock_dag_api.post_clear_task_instances.return_value = mock_response

        # Execute function
        with patch("src.airflow.dag.ClearTaskInstances") as mock_clear_class:
            mock_clear_instance = MagicMock()
            mock_clear_class.return_value = mock_clear_instance

            result = await clear_task_instances(**test_case["input"])

            # Verify ClearTaskInstances creation and API call
            mock_clear_class.assert_called_once_with(**test_case["expected_clear_request"])
            mock_dag_api.post_clear_task_instances.assert_called_once_with(
                dag_id=test_case["input"]["dag_id"], clear_task_instances=mock_clear_instance
            )

        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)

    @pytest.mark.parametrize(
        "test_case",
        [
            {
                "name": "set_task_state_minimal",
                "input": {"dag_id": "test_dag", "state": "success"},
                "mock_response": {"message": "Task state updated"},
                "expected_state_request": {"state": "success"},
            },
            {
                "name": "set_task_state_full",
                "input": {
                    "dag_id": "test_dag",
                    "state": "failed",
                    "task_ids": ["task1"],
                    "execution_date": "2023-01-01T00:00:00Z",
                    "include_upstream": True,
                    "include_downstream": False,
                    "dry_run": True,
                },
                "mock_response": {"message": "Dry run state update"},
                "expected_state_request": {
                    "state": "failed",
                    "task_ids": ["task1"],
                    "execution_date": "2023-01-01T00:00:00Z",
                    "include_upstream": True,
                    "include_downstream": False,
                    "dry_run": True,
                },
            },
        ],
    )
    async def test_set_task_instances_state_table_driven(self, test_case, mock_dag_api):
        """Table-driven test for set_task_instances_state function."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.to_dict.return_value = test_case["mock_response"]
        mock_dag_api.post_set_task_instances_state.return_value = mock_response

        # Execute function
        with patch("src.airflow.dag.UpdateTaskInstancesState") as mock_state_class:
            mock_state_instance = MagicMock()
            mock_state_class.return_value = mock_state_instance

            result = await set_task_instances_state(**test_case["input"])

            # Verify UpdateTaskInstancesState creation and API call
            mock_state_class.assert_called_once_with(**test_case["expected_state_request"])
            mock_dag_api.post_set_task_instances_state.assert_called_once_with(
                dag_id=test_case["input"]["dag_id"], update_task_instances_state=mock_state_instance
            )

        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)

    @pytest.mark.parametrize(
        "test_case",
        [
            {
                "name": "simple_functions_get_dag_source",
                "function": get_dag_source,
                "api_method": "get_dag_source",
                "input": {"file_token": "test_token"},
                "mock_response": {"content": "DAG source code"},
                "expected_call_kwargs": {"file_token": "test_token"},
            },
            {
                "name": "simple_functions_get_dag_tasks",
                "function": get_dag_tasks,
                "api_method": "get_tasks",
                "input": {"dag_id": "test_dag"},
                "mock_response": {"tasks": []},
                "expected_call_kwargs": {"dag_id": "test_dag"},
            },
            {
                "name": "simple_functions_get_task",
                "function": get_task,
                "api_method": "get_task",
                "input": {"dag_id": "test_dag", "task_id": "test_task"},
                "mock_response": {"task_id": "test_task", "operator": "BashOperator"},
                "expected_call_kwargs": {"dag_id": "test_dag", "task_id": "test_task"},
            },
            {
                "name": "simple_functions_delete_dag",
                "function": delete_dag,
                "api_method": "delete_dag",
                "input": {"dag_id": "test_dag"},
                "mock_response": {"message": "DAG deleted"},
                "expected_call_kwargs": {"dag_id": "test_dag"},
            },
            {
                "name": "simple_functions_reparse_dag_file",
                "function": reparse_dag_file,
                "api_method": "reparse_dag_file",
                "input": {"file_token": "test_token"},
                "mock_response": {"message": "DAG file reparsed"},
                "expected_call_kwargs": {"file_token": "test_token"},
            },
        ],
    )
    async def test_simple_functions_table_driven(self, test_case, mock_dag_api):
        """Table-driven test for simple functions that directly call API methods."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.to_dict.return_value = test_case["mock_response"]
        getattr(mock_dag_api, test_case["api_method"]).return_value = mock_response

        # Execute function
        result = await test_case["function"](**test_case["input"])

        # Verify API call and result
        getattr(mock_dag_api, test_case["api_method"]).assert_called_once_with(**test_case["expected_call_kwargs"])
        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert str(test_case["mock_response"]) in result[0].text

    @pytest.mark.integration
    async def test_dag_functions_integration_flow(self, mock_dag_api):
        """Integration test showing typical DAG management workflow."""
        # Test data for a complete workflow
        dag_id = "integration_test_dag"

        # Mock responses for each step
        mock_responses = {
            "get_dag": {"dag_id": dag_id, "is_paused": True},
            "patch_dag": {"dag_id": dag_id, "is_paused": False},
            "get_tasks": {"tasks": [{"task_id": "task1"}, {"task_id": "task2"}]},
            "delete_dag": {"message": "DAG deleted successfully"},
        }

        # Setup mock responses
        for method, response in mock_responses.items():
            mock_response = MagicMock()
            mock_response.to_dict.return_value = response
            getattr(mock_dag_api, method).return_value = mock_response

        # Execute workflow steps
        with patch("src.airflow.dag.AIRFLOW_HOST", "http://localhost:8080"):
            # 1. Get DAG info
            dag_info = await get_dag(dag_id)
            assert len(dag_info) == 1

            # 2. Unpause DAG
            with patch("src.airflow.dag.DAG") as mock_dag_class:
                mock_dag_class.return_value = MagicMock()
                unpause_result = await patch_dag(dag_id, is_paused=False)
                assert len(unpause_result) == 1

            # 3. Get tasks
            tasks_result = await get_tasks(dag_id)
            assert len(tasks_result) == 1

            # 4. Delete DAG
            delete_result = await delete_dag(dag_id)
            assert len(delete_result) == 1

        # Verify all API calls were made
        mock_dag_api.get_dag.assert_called_once_with(dag_id=dag_id)
        mock_dag_api.patch_dag.assert_called_once()
        mock_dag_api.get_tasks.assert_called_once_with(dag_id=dag_id)
        mock_dag_api.delete_dag.assert_called_once_with(dag_id=dag_id)
