"""Unit tests for validators and request schemas."""

import os
import sys

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.schemas import LinkAnalysisRequest
from app.services.llm_service import LLMService
from app.utils.validators import is_private_or_localhost, validate_url_for_fetch


def test_localhost_blocked():
    assert is_private_or_localhost("localhost") is True
    assert is_private_or_localhost("127.0.0.1") is True


def test_private_ips_blocked():
    assert is_private_or_localhost("192.168.1.1") is True
    assert is_private_or_localhost("10.0.0.5") is True
    assert is_private_or_localhost("172.16.0.1") is True


def test_public_host_not_blocked():
    assert is_private_or_localhost("example.com") is False


def test_valid_request():
    req = LinkAnalysisRequest(url="https://example.com")
    assert str(req.url) == "https://example.com/"


def test_invalid_scheme_rejected():
    with pytest.raises(ValidationError):
        LinkAnalysisRequest(url="ftp://example.com")


def test_private_url_rejected():
    with pytest.raises(HTTPException) as exc_info:
        validate_url_for_fetch("http://192.168.1.1/")
    assert exc_info.value.status_code == 400


def test_response_shaping_preserves_input_data():
    data = {
        "brand": {"name": "Example", "category": "Technology", "summary": ""},
        "competitor_analysis": {"competitors": []},
    }
    original_data = data.copy()

    response = LLMService._shape_response("https://example.com", data)

    assert data == original_data
    assert response["analysis"] == {"competitor_analysis": {"competitors": []}}
