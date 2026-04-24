"""Tests for the dagrun module, focusing on list_failed_dag_runs."""

from unittest.mock import MagicMock, patch

import mcp.types as types
import pytest

from src.airflow.dagrun import list_failed_dag_runs


class TestListFailedDagRuns:
    """Test cases for the list_failed_dag_runs function."""

    @pytest.fixture
    def mock_dag_run_api(self):
        """Create a mock DAG Run API instance."""
        with patch("src.airflow.dagrun.dag_run_api") as mock_api:
            yield mock_api

    @pytest.mark.parametrize(
        "test_case",
        [
            {
                "name": "no_params_returns_failed_runs",
                "input": {},
                "mock_response": {
                    "dag_runs": [
                        {"dag_id": "dag1", "dag_run_id": "run1", "state": "failed"},
                        {"dag_id": "dag2", "dag_run_id": "run2", "state": "failed"},
                    ],
                    "total_entries": 2,
                },
                "expected_form": {"state": ["failed"]},
            },
            {
                "name": "filter_by_dag_ids",
                "input": {"dag_ids": ["dag1", "dag3"]},
                "mock_response": {
                    "dag_runs": [
                        {"dag_id": "dag1", "dag_run_id": "run1", "state": "failed"},
                    ],
                    "total_entries": 1,
                },
                "expected_form": {"state": ["failed"], "dag_ids": ["dag1", "dag3"]},
            },
            {
                "name": "filter_by_date_range",
                "input": {
                    "execution_date_gte": "2024-01-01T00:00:00Z",
                    "execution_date_lte": "2024-01-31T23:59:59Z",
                },
                "mock_response": {
                    "dag_runs": [],
                    "total_entries": 0,
                },
                "expected_form": {
                    "state": ["failed"],
                    "execution_date_gte": "2024-01-01T00:00:00Z",
                    "execution_date_lte": "2024-01-31T23:59:59Z",
                },
            },
            {
                "name": "with_pagination",
                "input": {"page_offset": 10, "page_limit": 5},
                "mock_response": {
                    "dag_runs": [
                        {"dag_id": "dag5", "dag_run_id": "run5", "state": "failed"},
                    ],
                    "total_entries": 15,
                },
                "expected_form": {"state": ["failed"], "page_offset": 10, "page_limit": 5},
            },
            {
                "name": "with_order_by",
                "input": {"order_by": "-execution_date"},
                "mock_response": {
                    "dag_runs": [
                        {"dag_id": "dag1", "dag_run_id": "run2", "state": "failed"},
                        {"dag_id": "dag1", "dag_run_id": "run1", "state": "failed"},
                    ],
                    "total_entries": 2,
                },
                "expected_form": {"state": ["failed"], "order_by": "-execution_date"},
            },
            {
                "name": "with_start_and_end_date_filters",
                "input": {
                    "start_date_gte": "2024-01-01T00:00:00Z",
                    "start_date_lte": "2024-06-01T00:00:00Z",
                    "end_date_gte": "2024-01-01T00:00:00Z",
                    "end_date_lte": "2024-06-01T00:00:00Z",
                },
                "mock_response": {
                    "dag_runs": [],
                    "total_entries": 0,
                },
                "expected_form": {
                    "state": ["failed"],
                    "start_date_gte": "2024-01-01T00:00:00Z",
                    "start_date_lte": "2024-06-01T00:00:00Z",
                    "end_date_gte": "2024-01-01T00:00:00Z",
                    "end_date_lte": "2024-06-01T00:00:00Z",
                },
            },
            {
                "name": "all_params_combined",
                "input": {
                    "dag_ids": ["dag1"],
                    "execution_date_gte": "2024-01-01T00:00:00Z",
                    "execution_date_lte": "2024-12-31T23:59:59Z",
                    "start_date_gte": "2024-01-01T00:00:00Z",
                    "start_date_lte": "2024-12-31T23:59:59Z",
                    "end_date_gte": "2024-01-01T00:00:00Z",
                    "end_date_lte": "2024-12-31T23:59:59Z",
                    "order_by": "-start_date",
                    "page_offset": 0,
                    "page_limit": 100,
                },
                "mock_response": {
                    "dag_runs": [
                        {"dag_id": "dag1", "dag_run_id": "run1", "state": "failed"},
                    ],
                    "total_entries": 1,
                },
                "expected_form": {
                    "state": ["failed"],
                    "dag_ids": ["dag1"],
                    "execution_date_gte": "2024-01-01T00:00:00Z",
                    "execution_date_lte": "2024-12-31T23:59:59Z",
                    "start_date_gte": "2024-01-01T00:00:00Z",
                    "start_date_lte": "2024-12-31T23:59:59Z",
                    "end_date_gte": "2024-01-01T00:00:00Z",
                    "end_date_lte": "2024-12-31T23:59:59Z",
                    "order_by": "-start_date",
                    "page_offset": 0,
                    "page_limit": 100,
                },
            },
        ],
    )
    async def test_list_failed_dag_runs(self, test_case, mock_dag_run_api):
        """Table-driven test for list_failed_dag_runs function."""
        mock_response = MagicMock()
        mock_response.to_dict.return_value = test_case["mock_response"]
        mock_dag_run_api.get_dag_runs_batch.return_value = mock_response

        with patch("src.airflow.dagrun.AIRFLOW_HOST", "http://localhost:8080"):
            result = await list_failed_dag_runs(**test_case["input"])

        # Verify the batch API was called with state=["failed"] always included
        mock_dag_run_api.get_dag_runs_batch.assert_called_once_with(list_dag_runs_form=test_case["expected_form"])

        # Verify result structure
        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)

        # Verify UI URLs were added
        for dag_run in test_case["mock_response"].get("dag_runs", []):
            if dag_run.get("dag_id") and dag_run.get("dag_run_id"):
                assert "ui_url" in result[0].text

    async def test_list_failed_dag_runs_always_filters_failed_state(self, mock_dag_run_api):
        """Ensure state=['failed'] is always sent regardless of input."""
        mock_response = MagicMock()
        mock_response.to_dict.return_value = {"dag_runs": [], "total_entries": 0}
        mock_dag_run_api.get_dag_runs_batch.return_value = mock_response

        with patch("src.airflow.dagrun.AIRFLOW_HOST", "http://localhost:8080"):
            await list_failed_dag_runs()

        call_args = mock_dag_run_api.get_dag_runs_batch.call_args
        assert call_args.kwargs["list_dag_runs_form"]["state"] == ["failed"]

    async def test_list_failed_dag_runs_ui_urls_added(self, mock_dag_run_api):
        """Verify UI URLs are correctly added to each failed DAG run."""
        mock_response = MagicMock()
        mock_response.to_dict.return_value = {
            "dag_runs": [
                {"dag_id": "my_dag", "dag_run_id": "run_123", "state": "failed"},
            ],
            "total_entries": 1,
        }
        mock_dag_run_api.get_dag_runs_batch.return_value = mock_response

        with patch("src.airflow.dagrun.AIRFLOW_HOST", "http://localhost:8080"):
            result = await list_failed_dag_runs()

        assert "http://localhost:8080/dags/my_dag/grid?dag_run_id=run_123" in result[0].text


class TestListFailedDagRunsRegistration:
    """Test that list_failed_dag_runs is properly registered."""

    def test_registered_in_get_all_functions(self):
        """Verify list_failed_dag_runs is in the function registry."""
        from src.airflow.dagrun import get_all_functions

        functions = get_all_functions()
        func_names = [name for _, name, _, _ in functions]
        assert "list_failed_dag_runs" in func_names

    def test_registered_as_read_only(self):
        """Verify list_failed_dag_runs is marked as read-only."""
        from src.airflow.dagrun import get_all_functions

        functions = get_all_functions()
        for _func, name, _description, is_read_only in functions:
            if name == "list_failed_dag_runs":
                assert is_read_only is True
                break
