"""Significant characters / acronym / camelCase matcher (Score: 2)."""

import re
from typing import Optional
from switcheroo.core.matchers.base import MatchResult, StringPart


class SignificantCharactersMatcher:
    """Matches word boundaries and uppercase / camelCase characters (Score: 2)."""

    def evaluate(self, input_str: Optional[str], pattern: Optional[str]) -> MatchResult:
        if input_str is None:
            return MatchResult(matched=False, score=0)

        if not pattern:
            return MatchResult.non_match(input_str)

        regex_pattern = self._build_regex_pattern(pattern)
        match = re.search(regex_pattern, input_str)
        if not match:
            return MatchResult.non_match(input_str)

        result = MatchResult(matched=True, score=2)
        before_match = input_str[: match.start()]
        if before_match:
            result.string_parts.append(StringPart(before_match, is_match=False))

        for group_idx in range(1, len(match.groups()) + 1):
            val = match.group(group_idx)
            if val:
                result.string_parts.append(StringPart(val, is_match=(group_idx % 2 == 0)))

        after_match = input_str[match.end() :]
        if after_match:
            result.string_parts.append(StringPart(after_match, is_match=False))

        return result

    @staticmethod
    def _build_regex_pattern(pattern: str) -> str:
        regex_pattern = ""
        for p in pattern:
            lower_p = re.escape(p.lower())
            upper_p = re.escape(p.upper())
            regex_pattern += rf"([^\sA-Z]*?\s?)(\b{lower_p}|{upper_p})"
        return regex_pattern
