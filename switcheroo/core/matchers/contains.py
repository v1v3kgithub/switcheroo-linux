"""Substring matcher (Score: 2)."""

from typing import Optional
from switcheroo.core.matchers.base import MatchResult, StringPart


class ContainsMatcher:
    """Matches if the pattern is contained anywhere in the input string (case-insensitive)."""

    def evaluate(self, input_str: Optional[str], pattern: Optional[str]) -> MatchResult:
        if input_str is None:
            return MatchResult(matched=False, score=0)

        if not pattern:
            return MatchResult.non_match(input_str)

        idx = input_str.lower().find(pattern.lower())
        if idx == -1:
            return MatchResult.non_match(input_str)

        before = input_str[:idx]
        matched = input_str[idx : idx + len(pattern)]
        after = input_str[idx + len(pattern) :]

        result = MatchResult(matched=True, score=2)
        if before:
            result.string_parts.append(StringPart(before, is_match=False))
        result.string_parts.append(StringPart(matched, is_match=True))
        if after:
            result.string_parts.append(StringPart(after, is_match=False))

        return result
