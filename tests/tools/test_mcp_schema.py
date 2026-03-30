from __future__ import annotations

from typing import Any
import pytest

from TARS.agent.tools.mcp import _extract_nullable_branch, _normalize_schema_for_openai

def test_extract_nullable_branch_non_list() -> None:
    assert _extract_nullable_branch(None) is None
    assert _extract_nullable_branch({}) is None
    assert _extract_nullable_branch(42) is None
    assert _extract_nullable_branch("not a list") is None

def test_extract_nullable_branch_with_non_dict_elements() -> None:
    assert _extract_nullable_branch([1, 2]) is None
    assert _extract_nullable_branch([{"type": "string"}, "not a dict"]) is None

def test_extract_nullable_branch_no_null_type() -> None:
    options = [{"type": "string"}, {"type": "integer"}]
    assert _extract_nullable_branch(options) is None

def test_extract_nullable_branch_multiple_non_null_branches() -> None:
    options = [
        {"type": "string"},
        {"type": "integer"},
        {"type": "null"},
    ]
    assert _extract_nullable_branch(options) is None

def test_extract_nullable_branch_only_null() -> None:
    options = [{"type": "null"}]
    assert _extract_nullable_branch(options) is None

def test_extract_nullable_branch_valid_nullable_union() -> None:
    non_null_branch = {"type": "string", "description": "a string"}
    options = [
        non_null_branch,
        {"type": "null"},
    ]
    result = _extract_nullable_branch(options)
    assert result is not None
    branch, saw_null = result
    assert branch == non_null_branch
    assert saw_null is True

def test_extract_nullable_branch_valid_nullable_union_reversed() -> None:
    non_null_branch = {"type": "integer"}
    options = [
        {"type": "null"},
        non_null_branch,
    ]
    result = _extract_nullable_branch(options)
    assert result is not None
    branch, saw_null = result
    assert branch == non_null_branch
    assert saw_null is True

def test_normalize_schema_non_dict() -> None:
    expected = {"type": "object", "properties": {}}
    assert _normalize_schema_for_openai(None) == expected
    assert _normalize_schema_for_openai(42) == expected

def test_normalize_schema_type_list_nullable() -> None:
    schema = {"type": ["string", "null"], "description": "a nullable string"}
    normalized = _normalize_schema_for_openai(schema)
    assert normalized["type"] == "string"
    assert normalized["nullable"] is True
    assert normalized["description"] == "a nullable string"

def test_normalize_schema_anyof_nullable() -> None:
    schema = {
        "anyOf": [{"type": "string", "description": "some string"}, {"type": "null"}],
        "title": "NullableString",
    }
    normalized = _normalize_schema_for_openai(schema)
    assert normalized["type"] == "string"
    assert normalized["nullable"] is True
    assert normalized["description"] == "some string"
    assert normalized["title"] == "NullableString"
    assert "anyOf" not in normalized

def test_normalize_schema_oneof_nullable() -> None:
    schema = {
        "oneOf": [{"type": "null"}, {"type": "integer", "minimum": 1}],
    }
    normalized = _normalize_schema_for_openai(schema)
    assert normalized["type"] == "integer"
    assert normalized["nullable"] is True
    assert normalized["minimum"] == 1
    assert "oneOf" not in normalized

def test_normalize_schema_recursive_properties() -> None:
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": ["string", "null"]},
            "tags": {
                "type": "array",
                "items": {"type": ["string", "null"]}
            }
        }
    }
    normalized = _normalize_schema_for_openai(schema)
    assert normalized["properties"]["name"] == {"type": "string", "nullable": True}
    assert normalized["properties"]["tags"]["items"] == {"type": "string", "nullable": True}

def test_normalize_schema_recursive_items() -> None:
    schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"}
            }
        }
    }
    normalized = _normalize_schema_for_openai(schema)
    assert normalized["items"]["type"] == "object"
    assert normalized["items"]["properties"]["id"] == {"type": "integer"}
    assert normalized["items"]["required"] == []

def test_normalize_schema_object_defaults() -> None:
    schema = {"type": "object"}
    normalized = _normalize_schema_for_openai(schema)
    assert normalized["properties"] == {}
    assert normalized["required"] == []

def test_normalize_schema_non_object_no_defaults() -> None:
    schema = {"type": "string"}
    normalized = _normalize_schema_for_openai(schema)
    assert "properties" not in normalized
    assert "required" not in normalized
