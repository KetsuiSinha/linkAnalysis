"""Deduplication service for consolidating duplicate profiles."""

from typing import List, Dict, Any, Optional
from collections import defaultdict

from app.utils.normalizers import names_match, locations_match, merge_social_links, normalize_name, normalize_business_name


def deduplicate_profiles(profiles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Deduplicate profiles by name and location."""
    if not profiles:
        return []

    # Group by normalized name
    groups = defaultdict(list)
    for profile in profiles:
        norm_name = normalize_name(profile.get("name", ""))
        groups[norm_name].append(profile)

    deduplicated = []
    for norm_name, group in groups.items():
        if len(group) == 1:
            deduplicated.append(group[0])
        else:
            # Merge profiles in the same group
            merged = merge_profile_group(group)
            deduplicated.append(merged)

    return deduplicated


def merge_profile_group(profiles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Merge a group of profiles into one consolidated profile."""
    if len(profiles) == 1:
        return profiles[0]

    # Use the profile with the most complete info as base
    base = max(profiles, key=lambda p: len(str(p.get("bio", ""))) + (1 if p.get("email") else 0))

    merged = base.copy()
    merged_social = []

    for profile in profiles:
        # Merge social links
        for link in profile.get("social_link", []):
            platform = link.get("platform")
            link_url = link.get("link")
            if platform and link_url:
                # Check if already exists
                exists = any(l["platform"] == platform for l in merged_social)
                if not exists:
                    merged_social.append(link)

    merged["social_link"] = merged_social

    # Merge location if available
    locations = [p.get("location") for p in profiles if p.get("location")]
    if locations:
        merged["location"] = locations[0]

    # Merge contact info
    for profile in profiles:
        for field in ["email", "phone", "whatsapp_link"]:
            if profile.get(field) and not merged.get(field):
                merged[field] = profile[field]

    return merged


def deduplicate_cross_platform(profiles: List[dict]) -> List[dict]:
    """Deduplicate across platforms using name and location matching."""
    if not profiles:
        return []

    # Build clusters of similar profiles
    clusters = []
    for profile in profiles:
        matched_cluster = None
        for cluster in clusters:
            # Check if this profile matches any in the cluster
            for member in cluster:
                if profiles_match(profile, member):
                    matched_cluster = cluster
                    break
            if matched_cluster:
                break

        if matched_cluster:
            matched_cluster.append(profile)
        else:
            clusters.append([profile])

    # Merge each cluster
    deduplicated = []
    for cluster in clusters:
        if len(cluster) == 1:
            deduplicated.append(cluster[0])
        else:
            deduplicated.append(merge_profile_group(cluster))

    return deduplicated


def profiles_match(p1: dict, p2: dict, name_threshold: float = 0.85) -> bool:
    """Check if two profiles likely represent the same person."""
    from app.utils.normalizers import names_match, locations_match

    name1 = p1.get("name", "")
    name2 = p2.get("name", "")
    loc1 = p1.get("location")
    loc2 = p2.get("location")

    name_match = names_match(name1, name2, name_threshold)
    loc_match = locations_match(loc1, loc2)

    # If names match strongly, consider it a match
    if name_match and (loc_match or not loc1 or not loc2):
        return True

    # If locations match strongly and names are similar
    if loc_match and names_match(name1, name2, 0.7):
        return True

    return False