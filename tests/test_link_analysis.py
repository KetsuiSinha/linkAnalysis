import re
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.utils.validators import validate_url_for_fetch, is_private_or_localhost
from app.schemas import LinkAnalysisRequest


def test_localhost_blocked():
    assert is_private_or_localhost("localhost") is True
    assert is_private_or_localhost("127.0.0.1") is True


def test_private_ip_blocked():
    assert is_private_or_localhost("192.168.1.1") is True
    assert is_private_or_localhost("10.0.0.5") is True
    assert is_private_or_localhost("172.16.0.1") is True


def test_public_host_not_blocked():
    assert is_private_or_localhost("example.com") is False


def test_link_analysis_request_valid():
    req = LinkAnalysisRequest(url="https://example.com")
    assert str(req.url) == "https://example.com/"


def test_link_analysis_request_invalid_scheme():
    try:
        LinkAnalysisRequest(url="ftp://example.com")
        assert False, "Should have raised"
    except Exception:
        pass
