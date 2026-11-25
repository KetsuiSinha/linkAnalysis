"""Prospect service orchestrating the discovery pipeline."""

import os
from typing import List, Dict, Any

from app.schemas import UnderstoodQuery, Prospect, SocialLink, ProspectDiscoveryResponse
from app.services.query_service import understand_prospect_query
from app.services.search_service import search_all_platforms
from app.services.profile_extractor import enrich_profile_from_web
from app.services.deduplication_service import deduplicate_cross_platform
from app.services.relevance_service import filter_relevant_prospects
from app.utils.validators import is_valid_profile_url, normalize_url
from app.utils.normalizers import names_match
from app.schemas import RawProfile
from app.config import settings


def discover_prospects(query: str, max_results: int = 20) -> ProspectDiscoveryResponse:
    """Main pipeline for prospect discovery."""
    # 1. Understand the query
    understood_query = understand_prospect_query(query)
    understood_dict = {
        "search_keywords": understood_query.search_keywords,
        "city": understood_query.city,
        "state": understood_query.state,
        "country": understood_query.country,
        "interest": understood_query.interest,
        "audience": understood_query.audience,
        "target_type": understood_query.target_type,
    }

    # Check if we have any API keys configured
    has_api_keys = any([
        settings.google_search_api_key,
        settings.twitter_bearer_token,
        settings.youtube_api_key,
        settings.linkedin_access_token,
        settings.facebook_access_token,
    ])

    if not has_api_keys:
        # Return mock data for demo purposes
        return _get_mock_prospects(query, understood_query, max_results)

    # 2. Search all platforms
    raw_results = search_all_platforms(query, understood_dict, max_results_per_platform=10)

    # 2b. Convert to RawProfile objects and enrich
    raw_profiles = []
    for result in raw_results:
        # Enrich with web scraping
        enriched = enrich_profile_from_web(result.get("profile_url", ""))
        profile = {**result, **enriched}
        raw_profiles.append(profile)

    # 3. Convert to standardized format
    standardized = standardize_profiles(raw_profiles)

    # 4. Deduplicate across platforms
    deduplicated = deduplicate_cross_platform(standardized)

    # 5. Filter by relevance
    understood_dict_for_relevance = {
        "interest": understood_query.interest,
        "city": understood_query.city,
        "state": understood_query.state,
        "country": understood_query.country,
        "search_keywords": understood_query.search_keywords,
    }
    relevant = filter_relevant_prospects(standardized, understood_dict_for_relevance)

    # 6. Convert to Prospect objects
    prospects = convert_to_prospects(relevant)

    # Limit results
    prospects = prospects[:max_results]

    return ProspectDiscoveryResponse(
        success=True,
        query=query,
        total_prospects=len(prospects),
        prospects=prospects,
    )


def _get_mock_prospects(query: str, understood_query, max_results: int) -> ProspectDiscoveryResponse:
    """Generate mock prospects for demo when no API keys are configured."""
    from app.schemas import Prospect, SocialLink, ProspectDiscoveryResponse

    # Generate contextual mock prospects based on query
    interest = understood_query.interest.lower()
    city = understood_query.city or "Unknown City"
    country = understood_query.country or "USA"

    # Generate contextual names and profiles
    if "football" in interest or "soccer" in interest:
        mock_prospects = [
            Prospect(
                name="Michael Johnson",
                location=f"{city}, {country}",
                social_link=[
                    SocialLink(platform="LinkedIn", link="https://linkedin.com/in/mjohnson-football"),
                    SocialLink(platform="X", link="https://x.com/mjohnson_fc"),
                    SocialLink(platform="Instagram", link="https://instagram.com/mjohnson_fc"),
                    SocialLink(platform="Email", link="mailto:mjohnson@footballclub.com"),
                ]
            ),
            Prospect(
                name="Sarah Williams",
                location=f"{city}, {country}",
                social_link=[
                    SocialLink(platform="Facebook", link="https://facebook.com/sarah.williams.fc"),
                    SocialLink(platform="Instagram", link="https://instagram.com/sarahw_fc"),
                    SocialLink(platform="YouTube", link="https://youtube.com/@sarahwilliamsfc"),
                    SocialLink(platform="WhatsApp", link="https://wa.me/15551234567"),
                ]
            ),
            Prospect(
                name="David Chen",
                location=f"{city}, {country}",
                social_link=[
                    SocialLink(platform="LinkedIn", link="https://linkedin.com/in/dchen-soccer"),
                    SocialLink(platform="X", link="https://x.com/dchen_soccer"),
                    SocialLink(platform="Email", link="mailto:dchen@socceracademy.com"),
                ]
            ),
        ]
    elif "startup" in interest or "founder" in interest:
        mock_prospects = [
            Prospect(
                name="Alexandra Rivera",
                location=f"{city}, {country}",
                social_link=[
                    SocialLink(platform="LinkedIn", link="https://linkedin.com/in/alexrivera-startup"),
                    SocialLink(platform="X", link="https://x.com/alexrivera_vc"),
                    SocialLink(platform="Email", link="mailto:alex@venturefund.com"),
                ]
            ),
            Prospect(
                name="James Park",
                location=f"{city}, {country}",
                social_link=[
                    SocialLink(platform="LinkedIn", link="https://linkedin.com/in/jpark-founder"),
                    SocialLink(platform="X", link="https://x.com/jpark_startup"),
                    SocialLink(platform="YouTube", link="https://youtube.com/@jparkfounder"),
                ]
            ),
        ]
    elif "cricket" in interest:
        mock_prospects = [
            Prospect(
                name="Rahul Sharma",
                location=f"{city}, {country}",
                social_link=[
                    SocialLink(platform="LinkedIn", link="https://linkedin.com/in/rsharma-cricket"),
                    SocialLink(platform="Instagram", link="https://instagram.com/rsharma_cricket"),
                    SocialLink(platform="WhatsApp", link="https://wa.me/919876543210"),
                ]
            ),
            Prospect(
                name="Priya Patel",
                location=f"{city}, {country}",
                social_link=[
                    SocialLink(platform="Facebook", link="https://facebook.com/priya.patel.cricket"),
                    SocialLink(platform="X", link="https://x.com/priya_patel_cric"),
                    SocialLink(platform="Email", link="mailto:priya@cricketacademy.com"),
                ]
            ),
        ]
    elif "restaurant" in interest or "food" in interest:
        mock_prospects = [
            Prospect(
                name="Marco Rossi",
                location=f"{city}, {country}",
                social_link=[
                    SocialLink(platform="Instagram", link="https://instagram.com/marcorossi_chef"),
                    SocialLink(platform="Facebook", link="https://facebook.com/marcorossirestaurant"),
                    SocialLink(platform="Email", link="mailto:marco@rossirestaurant.com"),
                ]
            ),
            Prospect(
                name="Aisha Khan",
                location=f"{city}, {country}",
                social_link=[
                    SocialLink(platform="LinkedIn", link="https://linkedin.com/in/aishakhan-restaurateur"),
                    SocialLink(platform="Instagram", link="https://instagram.com/aishakhan_eats"),
                    SocialLink(platform="WhatsApp", link="https://wa.me/971501234567"),
                ]
            ),
        ]
    elif "digital marketing" in interest or "marketing" in interest:
        mock_prospects = [
            Prospect(
                name="Jennifer Liu",
                location=f"{city}, {country}",
                social_link=[
                    SocialLink(platform="LinkedIn", link="https://linkedin.com/in/jliu-marketing"),
                    SocialLink(platform="X", link="https://x.com/jliu_marketing"),
                    SocialLink(platform="Email", link="mailto:jliu@digitalagency.com"),
                ]
            ),
            Prospect(
                name="Robert Kim",
                location=f"{city}, {country}",
                social_link=[
                    SocialLink(platform="LinkedIn", link="https://linkedin.com/in/rkim-seo"),
                    SocialLink(platform="YouTube", link="https://youtube.com/@rkimseo"),
                    SocialLink(platform="Email", link="mailto:rk@seoexperts.com"),
                ]
            ),
        ]
    else:
        # Generic mock prospects
        mock_prospects = [
            Prospect(
                name="John Smith",
                location=f"{city}, {country}",
                social_link=[
                    SocialLink(platform="LinkedIn", link="https://linkedin.com/in/johnsmith"),
                    SocialLink(platform="X", link="https://x.com/johnsmith"),
                    SocialLink(platform="Email", link="mailto:john.smith@example.com"),
                ]
            ),
            Prospect(
                name="Jane Doe",
                location=f"{city}, {country}",
                social_link=[
                    SocialLink(platform="LinkedIn", link="https://linkedin.com/in/janedoe"),
                    SocialLink(platform="Instagram", link="https://instagram.com/janedoe"),
                    SocialLink(platform="Email", link="mailto:jane.doe@example.com"),
                ]
            ),
        ]

    # Limit results
    mock_prospects = mock_prospects[:max_results]

    return ProspectDiscoveryResponse(
        success=True,
        query=query,
        total_prospects=len(mock_prospects),
        prospects=mock_prospects,
    )


def standardize_profiles(raw_profiles: List[dict]) -> List[dict]:
    """Convert raw platform results to standardized format."""
    standardized = []
    for profile in raw_profiles:
        if not profile.get("name"):
            continue

        # Build social links
        social_links = []
        platform = profile.get("platform", "Unknown")
        url = profile.get("profile_url", "")

        if platform and url:
            social_links.append({
                "platform": platform,
                "link": url,
            })

        # Add email if available
        if profile.get("email"):
            social_links.append({
                "platform": "Email",
                "link": f"mailto:{profile['email']}",
            })

        # Add phone if available
        if profile.get("phone"):
            social_links.append({
                "platform": "Phone",
                "link": f"tel:{profile['phone']}",
            })

        # Add WhatsApp if available
        if profile.get("whatsapp_link"):
            social_links.append({
                "platform": "WhatsApp",
                "link": profile["whatsapp_link"],
            })

        standardized.append({
            "name": profile.get("name", "Unknown"),
            "location": profile.get("location"),
            "social_link": social_links,
            "bio": profile.get("bio"),
            "email": profile.get("email"),
            "phone": profile.get("phone"),
            "whatsapp_link": profile.get("whatsapp_link"),
            "platform": profile.get("platform"),
            "profile_url": profile.get("profile_url"),
        })

    return standardized


def convert_to_prospects(standardized: List[dict]) -> List:
    """Convert standardized profiles to Prospect objects."""
    from app.schemas import Prospect, SocialLink

    prospects = []
    for profile in standardized:
        social_links = []
        for link in profile.get("social_link", []):
            social_links.append(SocialLink(
                platform=link["platform"],
                link=link["link"],
            ))

        prospects.append(Prospect(
            name=profile.get("name", "Unknown"),
            location=profile.get("location"),
            social_link=social_links,
        ))

    return prospects