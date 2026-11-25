"""Text normalization and name/entity matching utilities."""

import re
from typing import List, Optional, Tuple


# Common name prefixes/suffixes to strip
NAME_PREFIXES = {"mr.", "mrs.", "ms.", "dr.", "prof.", "sir.", "madam."}
NAME_SUFFIXES = {"jr.", "sr.", "ii", "iii", "iv", "phd", "md", "esq"}

# Common business suffixes
BUSINESS_SUFFIXES = {"inc", "inc.", "llc", "llc.", "ltd", "ltd.", "corp", "corp.", "co", "co.", "gmbh", "ag", "pvt", "pvt."}


def normalize_name(name: str) -> str:
    """Normalize a person's name for comparison."""
    if not name:
        return ""
    # Lowercase, strip
    name = name.strip().lower()
    # Remove extra whitespace
    name = re.sub(r"\s+", " ", name)
    # Remove titles/suffixes
    words = name.split()
    words = [w.rstrip(".") for w in words if w.rstrip(".") not in NAME_PREFIXES and w.rstrip(".") not in NAME_SUFFIXES]
    return " ".join(words)


def normalize_business_name(name: str) -> str:
    """Normalize a business name for comparison."""
    if not name:
        return ""
    name = name.strip().lower()
    name = re.sub(r"\s+", " ", name)
    words = name.split()
    words = [w.rstrip(".") for w in words if w.rstrip(".") not in BUSINESS_SUFFIXES]
    return " ".join(words)


def names_match(name1: str, name2: str, threshold: float = 0.85) -> bool:
    """Check if two names likely refer to the same person using Jaccard similarity."""
    norm1 = normalize_name(name1)
    norm2 = normalize_name(name2)
    if not norm1 or not norm2:
        return False
    if norm1 == norm2:
        return True
    # Jaccard similarity on words
    set1 = set(norm1.split())
    set2 = set(norm2.split())
    if not set1 or not set2:
        return False
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return (intersection / union) >= threshold


def locations_match(loc1: Optional[str], loc2: Optional[str]) -> bool:
    """Check if two location strings likely refer to the same place."""
    if not loc1 or not loc2:
        return False
    loc1_norm = loc1.lower().strip()
    loc2_norm = loc2.lower().strip()
    if loc1_norm == loc2_norm:
        return True
    # Check if one contains the other (e.g., "Washington DC" vs "Washington DC, USA")
    return loc1_norm in loc2_norm or loc2_norm in loc1_norm


def extract_location_parts(location: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Extract city, state, country from a location string."""
    if not location:
        return (None, None, None)
    parts = [p.strip() for p in location.split(",")]
    if len(parts) >= 3:
        return (parts[0], parts[1], parts[2])
    elif len(parts) == 2:
        return (parts[0], parts[1], None)
    elif len(parts) == 1:
        return (parts[0], None, None)
    return (None, None, None)


def merge_social_links(existing: List[dict], new: List[dict]) -> List[dict]:
    """Merge two lists of social links, deduplicating by platform."""
    merged = {item["platform"]: item for item in existing}
    for item in new:
        platform = item["platform"]
        if platform not in merged:
            merged[platform] = item
        else:
            # Keep the first one (already verified)
            pass
    return list(merged.values())


def normalize_phone(phone: str) -> str:
    """Normalize phone number to E.164 format."""
    import re
    cleaned = re.sub(r"[\s\-\(\)]", "", phone)
    if not cleaned.startswith("+"):
        # Assume US if no country code
        if len(cleaned) == 10:
            cleaned = "+1" + cleaned
        elif len(cleaned) == 11 and cleaned.startswith("1"):
            cleaned = "+" + cleaned
    return cleaned


def calculate_jaccard_similarity(set1: set, set2: set) -> float:
    """Calculate Jaccard similarity between two sets."""
    if not set1 and not set2:
        return 1.0
    if not set1 or not set2:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0


def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """Extract keywords from text (simple approach)."""
    if not text:
        return []
    # Remove URLs, emails, special chars
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"\S+@\S+", " ", text)
    text = re.sub(r"[^\w\s]", " ", text)
    # Split and filter
    words = [w.lower() for w in text.split() if len(w) > 2]
    # Remove common stop words
    stop_words = {"the", "and", "for", "are", "but", "not", "you", "all", "can", "has", "had", "was", "were", "with", "this", "that", "from", "they", "have", "been", "will", "would", "could", "should", "their", "there", "about", "which", "when", "what", "who", "whom", "where", "why", "how", "your", "our", "its", "his", "her", "she", "him"}
    words = [w for w in words if w not in stop_words]
    # Count frequency
    freq = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1
    # Sort by frequency
    sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [w for w, _ in sorted_words[:max_keywords]]