"""Unit tests for taskinstance module using pytest framework."""

from unittest.mock import MagicMock, patch

import mcp.types as types
import pytest

from src.airflow.taskinstance import (
    get_task_instance,
    list_task_instance_tries,
    list_task_instances,
    update_task_instance,
)


class TestTaskInstanceModule:
    """
    Test suite for verifying the behavior of taskinstance module's functions.

    Covers:
    - get_task_instance
    - list_task_instances
    - update_task_instance
    - list_task_instance_tries

    Each test uses parameterization to exercise a range of valid inputs and asserts:
    - Correct structure and content of the returned TextContent
    - Proper use of optional parameters
    - That the underlying API client methods are invoked with the right arguments
    """

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "dag_id, task_id, dag_run_id, expected_state",
        [
            ("dag_1", "task_a", "run_001", "success"),
            ("dag_2", "task_b", "run_002", "failed"),
            ("dag_3", "task_c", "run_003", "running"),
        ],
        ids=[
            "success-task-dag_1",
            "failed-task-dag_2",
            "running-task-dag_3",
        ],
    )
    async def test_get_task_instance(self, dag_id, task_id, dag_run_id, expected_state):
        """
        Test `get_task_instance` returns correct TextContent output and calls API once
        for different task states.
        """
        mock_response = MagicMock()
        mock_response.to_dict.return_value = {
            "dag_id": dag_id,
            "task_id": task_id,
            "dag_run_id": dag_run_id,
            "state": expected_state,
        }

        with patch(
            "src.airflow.taskinstance.task_instance_api.get_task_instance",
            return_value=mock_response,
        ) as mock_get:
            result = await get_task_instance(dag_id=dag_id, task_id=task_id, dag_run_id=dag_run_id)

        assert isinstance(result, list)
        assert len(result) == 1
        content = result[0]
        assert isinstance(content, types.TextContent)
        assert content.type == "text"
        assert dag_id in content.text
        assert task_id in content.text
        assert dag_run_id in content.text
        assert expected_state in content.text

        mock_get.assert_called_once_with(dag_id=dag_id, dag_run_id=dag_run_id, task_id=task_id)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "params",
        [
            {"dag_id": "dag_basic", "dag_run_id": "run_basic"},
            {
                "dag_id": "dag_with_state",
                "dag_run_id": "run_with_state",
                "state": ["success", "failed"],
            },
            {
                "dag_id": "dag_with_dates",
                "dag_run_id": "run_with_dates",
                "start_date_gte": "2024-01-01T00:00:00Z",
                "end_date_lte": "2024-01-10T23:59:59Z",
            },
            {
                "dag_id": "dag_with_filters",
                "dag_run_id": "run_filters",
                "pool": ["default_pool"],
                "queue": ["default"],
                "limit": 5,
                "offset": 10,
                "duration_gte": 5.0,
                "duration_lte": 100.5,
            },
            {
                "dag_id": "dag_with_all",
                "dag_run_id": "run_all",
                "execution_date_gte": "2024-01-01T00:00:00Z",
                "execution_date_lte": "2024-01-02T00:00:00Z",
                "start_date_gte": "2024-01-01T01:00:00Z",
                "start_date_lte": "2024-01-01T23:00:00Z",
                "end_date_gte": "2024-01-01T02:00:00Z",
                "end_date_lte": "2024-01-01T23:59:00Z",
                "updated_at_gte": "2024-01-01T03:00:00Z",
                "updated_at_lte": "2024-01-01T04:00:00Z",
                "duration_gte": 1.0,
                "duration_lte": 99.9,
                "state": ["queued"],
                "pool": ["my_pool"],
                "queue": ["my_queue"],
                "limit": 50,
                "offset": 0,
            },
            {
                "dag_id": "dag_with_empty_lists",
                "dag_run_id": "run_empty_lists",
                "state": [],
                "pool": [],
                "queue": [],
            },
        ],
        ids=[
            "basic-required-params",
            "with-state-filter",
            "with-date-range",
            "with-resource-filters",
            "all-filters-included",
            "empty-lists-filter",
        ],
    )
    async def test_list_task_instances(self, params):
        """
        Test `list_task_instances` with various combinations of filters.
        Validates output content and verifies API call arguments.
        """
        mock_response = MagicMock()
        mock_response.to_dict.return_value = {
            "dag_id": params["dag_id"],
            "dag_run_id": params["dag_run_id"],
            "instances": [
                {"task_id": "task_1", "state": "success"},
                {"task_id": "task_2", "state": "running"},
            ],
        }

        with patch(
            "src.airflow.taskinstance.task_instance_api.get_task_instances",
            return_value=mock_response,
        ) as mock_get:
            result = await list_task_instances(**params)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert result[0].type == "text"
        assert params["dag_id"] in result[0].text
        assert params["dag_run_id"] in result[0].text

        mock_get.assert_called_once_with(
            dag_id=params["dag_id"],
            dag_run_id=params["dag_run_id"],
            **{k: v for k, v in params.items() if k not in {"dag_id", "dag_run_id"} and v is not None},
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "dag_id, dag_run_id, task_id, state",
        [
            ("dag_1", "run_001", "task_a", "success"),
            ("dag_2", "run_002", "task_b", "failed"),
            ("dag_3", "run_003", "task_c", None),
        ],
        ids=["set-success-state", "set-failed-state", "no-state-update"],
    )
    async def test_update_task_instance(self, dag_id, dag_run_id, task_id, state):
        """
        Test `update_task_instance` for updating state and validating request payload.
        Also verifies that patch API is called with the correct update mask.
        """
        mock_response = MagicMock()
        mock_response.to_dict.return_value = {
            "dag_id": dag_id,
            "dag_run_id": dag_run_id,
            "task_id": task_id,
            "state": state,
        }

        with patch(
            "src.airflow.taskinstance.task_instance_api.patch_task_instance",
            return_value=mock_response,
        ) as mock_patch:
            result = await update_task_instance(dag_id=dag_id, dag_run_id=dag_run_id, task_id=task_id, state=state)

        assert isinstance(result, list)
        assert len(result) == 1
        content = result[0]
        assert isinstance(content, types.TextContent)
        assert content.type == "text"
        assert dag_id in content.text
        assert dag_run_id in content.text
        assert task_id in content.text
        if state is not None:
            assert state in content.text

        expected_mask = ["state"] if state is not None else []
        expected_request = {"state": state} if state is not None else {}
        mock_patch.assert_called_once_with(
            dag_id=dag_id,
            dag_run_id=dag_run_id,
            task_id=task_id,
            update_mask=expected_mask,
            task_instance_request=expected_request,
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "dag_id, dag_run_id, task_id, limit, offset, order_by",
        [
            ("dag_basic", "run_001", "task_a", None, None, None),
            ("dag_with_limit", "run_002", "task_b", 5, None, None),
            ("dag_with_offset", "run_003", "task_c", None, 10, None),
            ("dag_with_order_by", "run_004", "task_d", None, None, "-start_date"),
            ("dag_all_params", "run_005", "task_e", 10, 0, "end_date"),
            ("dag_zero_limit", "run_006", "task_f", 0, None, None),
            ("dag_zero_offset", "run_007", "task_g", None, 0, None),
            ("dag_empty_order", "run_008", "task_h", None, None, ""),
        ],
        ids=[
            "basic-required-only",
            "with-limit",
            "with-offset",
            "with-order_by-desc",
            "with-all-filters",
            "limit-zero",
            "offset-zero",
            "order_by-empty-string",
        ],
    )
    async def test_list_task_instance_tries(self, dag_id, dag_run_id, task_id, limit, offset, order_by):
        """
        Test `list_task_instance_tries` across various filter combinations,
        validating correct API call and response formatting.
        """
        mock_response = MagicMock()
        mock_response.to_dict.return_value = {
            "dag_id": dag_id,
            "dag_run_id": dag_run_id,
            "task_id": task_id,
            "tries": [
                {"try_number": 1, "state": "queued"},
                {"try_number": 2, "state": "success"},
            ],
        }

        with patch(
            "src.airflow.taskinstance.task_instance_api.get_task_instance_tries",
            return_value=mock_response,
        ) as mock_get:
            result = await list_task_instance_tries(
                dag_id=dag_id,
                dag_run_id=dag_run_id,
                task_id=task_id,
                limit=limit,
                offset=offset,
                order_by=order_by,
            )

        assert isinstance(result, list)
        assert len(result) == 1
        content = result[0]
        assert isinstance(content, types.TextContent)
        assert content.type == "text"
        assert dag_id in content.text
        assert dag_run_id in content.text
        assert task_id in content.text
        assert "tries" in content.text

        mock_get.assert_called_once_with(
            dag_id=dag_id,
            dag_run_id=dag_run_id,
            task_id=task_id,
            **{
                k: v
                for k, v in {
                    "limit": limit,
                    "offset": offset,
                    "order_by": order_by,
                }.items()
                if v is not None
            },
        )
