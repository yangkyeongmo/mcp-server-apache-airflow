"""Unit tests for variable module using pytest framework."""

import json
from unittest.mock import MagicMock, patch

import mcp.types as types
import pytest

from src.airflow.variable import create_variable, delete_variable, get_variable, update_variable


class TestVariableModule:
    """
    Test suite for verifying the behavior of variable module's functions.

    Covers:
    - create_variable
    - get_variable
    - update_variable
    - delete_variable

    Variable values are strings in Airflow, so JSON documents passed as
    structured values are serialized with json.dumps before reaching the API.
    """

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "key, value",
        [
            ("var_plain", "hello"),
            ("var_json", {"a": 1}),
            ("var_list", [1, "two"]),
            ("var_bool", True),
            ("var_number", 42),
        ],
        ids=["plain", "json_object", "json_list", "bool", "number"],
    )
    async def test_create_variable_stringifies_value(self, key, value):
        mock_response = MagicMock()
        mock_response.to_dict.return_value = {"key": key, "value": value}

        with patch(
            "src.airflow.variable.variable_api.post_variables",
            return_value=mock_response,
        ) as mock_post:
            result = await create_variable(key=key, value=value)

        expected_value = value if isinstance(value, str) else json.dumps(value)
        mock_post.assert_called_once_with(variable={"key": key, "value": expected_value})

        assert isinstance(result, list)
        content = result[0]
        assert isinstance(content, types.TextContent)
        assert key in content.text

    @pytest.mark.asyncio
    async def test_get_variable(self):
        mock_response = MagicMock()
        mock_response.to_dict.return_value = {"key": "var_a", "value": "v1"}

        with patch(
            "src.airflow.variable.variable_api.get_variable",
            return_value=mock_response,
        ) as mock_get:
            result = await get_variable(key="var_a")

        mock_get.assert_called_once_with(variable_key="var_a")
        assert isinstance(result[0], types.TextContent)
        assert "var_a" in result[0].text

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "key, value, description, expected_value",
        [
            ("var_a", "world", None, "world"),
            ("var_b", {"a": 2}, None, '{"a": 2}'),
            ("var_c", None, "only description", "current"),
        ],
        ids=["plain_string", "json_object", "value_fetched"],
    )
    async def test_update_variable(self, key, value, description, expected_value):
        mock_response = MagicMock()
        mock_response.to_dict.return_value = {"key": key, "value": expected_value}

        with patch(
            "src.airflow.variable.variable_api.get_variable",
            return_value=MagicMock(to_dict=MagicMock(return_value={"key": key, "value": "current"})),
        ), patch(
            "src.airflow.variable.variable_api.patch_variable",
            return_value=mock_response,
        ) as mock_patch:
            result = await update_variable(key=key, value=value, description=description)

        expected_body = {"key": key, "value": expected_value}
        if description is not None:
            expected_body["description"] = description
        mock_patch.assert_called_once_with(variable_key=key, variable=expected_body)

        assert isinstance(result, list)
        content = result[0]
        assert isinstance(content, types.TextContent)
        assert key in content.text

    @pytest.mark.asyncio
    async def test_delete_variable(self):
        with patch(
            "src.airflow.variable.variable_api.delete_variable",
            return_value=None,
        ) as mock_delete:
            result = await delete_variable(key="var_a")

        mock_delete.assert_called_once_with(variable_key="var_a")
        assert isinstance(result[0], types.TextContent)
        assert "var_a" in result[0].text
