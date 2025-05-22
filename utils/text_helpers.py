# utils/text_helpers.py

import yaml
from collections import namedtuple
import re
from config.norm_config import NUM_AS_WORDS
import inflect

_inflect = inflect.engine()
PatternSpec = namedtuple("PatternSpec", ["op", "pattern", "priority"])

def normalize_sentence(sentence):
    """
    Lowercases and trims whitespace, collapses multiple spaces, strips punctuation if needed.
    """
    # Lowercase and remove periods
    sentence = sentence.lower().strip().replace('.', '')
    sentence = re.sub(r'\s+', ' ', sentence)
    for word, digit in NUM_AS_WORDS.items():
        sentence = re.sub(rf'\b{word}\b', digit, sentence)
    return sentence

def normalize_ordinal(text):
    """
    If text is like 'nth', 'kth', '3rd', '2nd', etc., reduce to 'n','k','3','2'
    Otherwise, leave unchanged ('furthest', 'closest' etc.).
    """
    if text is None:
        return None
    
    t = str(text).strip().lower()
    # Try inflect's direct conversion for English words ("third" -> 3)
    try:
        as_num = _inflect.ordinal_to_number(t)
        if as_num is not None:
            return as_num
    except Exception:
        pass
    
    # Single-symbol ordinals ("nth", "kth", "mth", "pth")
    if re.match(r"^[a-z]th$", t):
        return t[0]  # Convert 'nth' -> 'n', etc.

    # Digit + suffix e.g. "3rd", "21st"
    match = re.match(r"^(\d+)(?:st|nd|rd|th)$", t)
    if match:
        return int(match.group(1))

    # Standalone "n", "k", "m" (no suffix: likely variable)
    if t in {"n", "k", "m", "p"}:
        return t

    # Fallback: let through special words for domain logic
    return t

def convert_int(val):
    """
    Try to convert string-like val to int, else return as is.
    - For lists, will apply recursively.
    """
    if isinstance(val, str):
        clean = val.replace(',', '')
        # Remove ordinal endings
        for end in ['st', 'nd', 'rd', 'th']:
            if clean.endswith(end):
                clean = clean[:-len(end)]
        try:
            return int(clean)
        except Exception:
            pass
    try:
        return int(val)
    except Exception:
        return val

def load_patterns(yaml_file):
    with open(yaml_file, "r") as fh:
        data = yaml.safe_load(fh)
    all_patterns = []
    for op, pats in data.items():
        for entry in pats:
            all_patterns.append(
                PatternSpec(op=op, pattern=entry["pattern"], priority=entry.get("priority", 50))
            )
    # Sort: lower priority number = higher priority
    all_patterns.sort(key=lambda x: x.priority)
    return all_patterns