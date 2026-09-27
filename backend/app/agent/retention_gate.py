from __future__ import annotations

import re
from typing import Tuple

# Deterministic keywords and phrases indicating durable engineering context
# per Section 8 of ContextIQ Master PRD
RETENTION_PATTERNS = [
    r"\bpreference\b",
    r"\bdecision\b",
    r"\barchitecture\b",
    r"\bincident\b",
    r"\bproduction\b",
    r"\bdatabase\b",
    r"\bdeployment\b",
    r"\bstack\b",
    r"\bteam uses\b",
    r"\bwe chose\b",
    r"\bwe rejected\b",
    r"\bwe use\b",
    r"\broot cause\b",
    r"\bfixed by\b",
    r"\bstandardized on\b",
]

COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in RETENTION_PATTERNS]


def evaluate_retention(message: str) -> Tuple[bool, str]:
    """
    Lightweight deterministic retention gate.
    Decides whether a message contains durable engineering context
    that should be sent to Hindsight Retain without adding an LLM classifier to the critical path.

    Returns:
        (should_retain, matched_category_or_signal)
    """
    if not message or len(message.strip()) < 10:
        return False, ""

    msg_lower = message.lower()
    for pattern in COMPILED_PATTERNS:
        match = pattern.search(msg_lower)
        if match:
            return True, match.group(0)

    return False, ""
