"""Individual / subsequence character matcher (Score: 1)."""

import re
from typing import Optional
from switcheroo.core.matchers.base import MatchResult, StringPart


class IndividualCharactersMatcher:
    """Matches characters appearing in sequential order (fuzzy subsequence, Score: 1)."""

    def evaluate(self, input_str: Optional[str], pattern: Optional[str]) -> MatchResult:
        if input_str is None:
            return MatchResult(matched=False, score=0)

        if not pattern:
            return MatchResult.non_match(input_str)

        regex_pattern = self._build_regex_pattern(pattern)
        match = re.match(regex_pattern, input_str, re.IGNORECASE)
        if not match:
            return MatchResult.non_match(input_str)

        result = MatchResult(matched=True, score=1)
        for group_idx in range(1, len(match.groups()) + 1):
            val = match.group(group_idx)
            if val:
                result.string_parts.append(StringPart(val, is_match=(group_idx % 2 == 0)))

        return result

    @staticmethod
    def _build_regex_pattern(pattern: str) -> str:
        regex_pattern = ""
        prev_char = None
        for p in pattern:
            if prev_char is not None:
                regex_pattern += rf"([^{re.escape(prev_char)}]*?)({re.escape(p)})"
            else:
                regex_pattern += rf"(.*?)({re.escape(p)})"
            prev_char = p
        return regex_pattern + "(.*)"
