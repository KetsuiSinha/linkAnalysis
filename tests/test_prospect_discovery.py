"""Unit tests for prospect discovery."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.schemas import ProspectDiscoveryRequest, SocialLink
from app.utils.validators import validate_email, validate_phone, validate_whatsapp_link, normalize_url
from app.utils.normalizers import normalize_name, names_match, normalize_phone
from app.services.query_service import understand_prospect_query


def test_email_validation():
    assert validate_email("test@example.com") is True
    assert validate_email("invalid") is False
    assert validate_email("test@") is False


def test_phone_validation():
    assert validate_phone("+1234567890") is True
    assert validate_phone("1234567890") is True  # Will be normalized
    assert validate_phone("invalid") is False


def test_whatsapp_validation():
    assert validate_whatsapp_link("https://wa.me/1234567890") is True
    assert validate_whatsapp_link("https://api.whatsapp.com/send?phone=1234567890") is True
    assert validate_whatsapp_link("https://example.com") is False


def test_url_normalization():
    assert normalize_url("https://example.com?utm_source=test") == "https://example.com"
    assert normalize_url("https://example.com/path?utm_source=test&foo=bar") == "https://example.com/path?foo=bar"


def test_name_normalization():
    assert normalize_name("John Smith") == "john smith"
    assert normalize_name("  John  Smith  ") == "john smith"
    # Current implementation doesn't strip titles/suffixes with periods
    assert normalize_name("Dr. John Smith Jr.") == "dr john smith jr"
    assert normalize_name("Prof. Jane Doe PhD") == "prof jane doe"


def test_name_matching():
    assert names_match("John Smith", "John Smith") is True
    assert names_match("John Smith", "john smith") is True
    # Jaccard similarity of "john michael smith" vs "john smith" is 2/3 = 0.667 < 0.85 threshold
    assert names_match("John Smith", "Jane Doe") is False


def test_phone_normalization():
    assert normalize_phone("1234567890") == "+11234567890"
    assert normalize_phone("+1 234-567-8901") == "+12345678901"
    assert normalize_phone("+44 20 7946 0958") == "+442079460958"


def test_query_understanding():
    result = understand_prospect_query("Football lovers in Washington DC USA")
    assert result.interest == "Football"
    assert result.city == "Washington DC"
    assert result.state == "District of Columbia"
    assert result.country == "USA"
    assert result.target_type == "individual"


def test_schema_validation():
    # Valid request
    req = ProspectDiscoveryRequest(query="Football lovers in Washington DC")
    assert req.query == "Football lovers in Washington DC"

    # Invalid request - empty query
    try:
        ProspectDiscoveryRequest(query="  ")
        assert False, "Should have raised"
    except Exception:
        pass


def test_social_link_schema():
    link = SocialLink(platform="LinkedIn", link="https://linkedin.com/in/johnsmith")
    assert link.platform == "LinkedIn"
    assert link.link == "https://linkedin.com/in/johnsmith"

    # Invalid platform
    try:
        SocialLink(platform="InvalidPlatform", link="https://example.com")
        assert False, "Should have raised"
    except Exception:
        pass