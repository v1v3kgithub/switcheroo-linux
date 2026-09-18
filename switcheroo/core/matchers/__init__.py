"""Matchers package."""

from switcheroo.core.matchers.base import MatchResult, StringPart
from switcheroo.core.matchers.starts_with import StartsWithMatcher
from switcheroo.core.matchers.significant import SignificantCharactersMatcher
from switcheroo.core.matchers.contains import ContainsMatcher
from switcheroo.core.matchers.fuzzy import IndividualCharactersMatcher

__all__ = [
    "MatchResult",
    "StringPart",
    "StartsWithMatcher",
    "SignificantCharactersMatcher",
    "ContainsMatcher",
    "IndividualCharactersMatcher",
]
