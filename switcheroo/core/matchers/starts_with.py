"""Prefix matcher (Score: 4)."""

from typing import Optional
from switcheroo.core.matchers.base import MatchResult, StringPart


class StartsWithMatcher:
    """Matches if the input starts with the pattern (case-insensitive)."""

    def evaluate(self, input_str: Optional[str], pattern: Optional[str]) -> MatchResult:
        if input_str is None:
            return MatchResult(matched=False, score=0)

        if not pattern:
            return MatchResult.non_match(input_str)

        if not input_str.lower().startswith(pattern.lower()):
            return MatchResult.non_match(input_str)

        matched_part = input_str[:len(pattern)]
        rest_of_input = input_str[len(pattern):]

        result = MatchResult(matched=True, score=4)
        result.string_parts.append(StringPart(matched_part, is_match=True))
        if rest_of_input:
            result.string_parts.append(StringPart(rest_of_input, is_match=False))

        return result
