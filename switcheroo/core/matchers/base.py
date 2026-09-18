"""Base data models for string matching and scoring."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class StringPart:
    """Represents a substring portion, marking whether it contributed to a match."""
    value: str
    is_match: bool = False


@dataclass
class MatchResult:
    """Represents the outcome of a matcher evaluation."""
    matched: bool = False
    score: int = 0
    string_parts: List[StringPart] = field(default_factory=list)

    @classmethod
    def non_match(cls, input_str: str = "") -> "MatchResult":
        """Creates a non-matching result preserving the original input string."""
        res = cls(matched=False, score=0)
        if input_str:
            res.string_parts.append(StringPart(input_str, is_match=False))
        return res
