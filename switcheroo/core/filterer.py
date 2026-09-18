"""Window filtering and scoring engine with dot-query support."""

from dataclasses import dataclass
from typing import List, Optional, Sequence
from switcheroo.core.matchers import (
    ContainsMatcher,
    IndividualCharactersMatcher,
    MatchResult,
    SignificantCharactersMatcher,
    StartsWithMatcher,
)
from switcheroo.core.window_model import AppWindow
from switcheroo.core.highlighter import PangoHighlighter


@dataclass
class FilterResult:
    """Represents a filtered and scored window match."""
    window: AppWindow
    title_match_results: List[MatchResult]
    process_match_results: List[MatchResult]
    total_score: int


class WindowFilterer:
    """Filters and ranks windows based on search query."""

    def __init__(self) -> None:
        self.starts_with = StartsWithMatcher()
        self.significant = SignificantCharactersMatcher()
        self.contains = ContainsMatcher()
        self.fuzzy = IndividualCharactersMatcher()

    def filter(
        self,
        windows: Sequence[AppWindow],
        query: str,
        foreground_process_title: Optional[str] = None,
    ) -> List[AppWindow]:
        """Filters windows by query string and updates formatted Pango markup."""
        if not query:
            for w in windows:
                w.formatted_title = PangoHighlighter.highlight(
                    self.contains.evaluate(w.title, "").string_parts
                )
                w.formatted_process_title = PangoHighlighter.highlight(
                    self.contains.evaluate(w.process_title, "").string_parts
                )
            return list(windows)

        filter_text = query
        process_filter_text: Optional[str] = None

        if "." in query:
            parts = query.split(".", 1)
            process_filter_text = parts[0]
            if not process_filter_text and foreground_process_title:
                process_filter_text = foreground_process_title
            filter_text = parts[1]

        scored_results: List[FilterResult] = []

        for w in windows:
            title_results = self._score(w.title, filter_text)
            proc_query = process_filter_text if process_filter_text is not None else filter_text
            proc_results = self._score(w.process_title, proc_query)

            # Determine whether criteria is met
            title_matched = any(r.matched for r in title_results)
            proc_matched = any(r.matched for r in proc_results)

            if process_filter_text is None:
                # Regular query: match either title or process
                if not (title_matched or proc_matched):
                    continue
            else:
                # Dot syntax query: must match both title AND process
                if not (title_matched and proc_matched):
                    continue

            total_score = sum(r.score for r in title_results if r.matched) + sum(
                r.score for r in proc_results if r.matched
            )

            scored_results.append(
                FilterResult(
                    window=w,
                    title_match_results=title_results,
                    process_match_results=proc_results,
                    total_score=total_score,
                )
            )

        # Sort descending by total score
        scored_results.sort(key=lambda r: r.total_score, reverse=True)

        matched_windows: List[AppWindow] = []
        for r in scored_results:
            win = r.window
            win.formatted_title = self._get_formatted_best_match(win.title, r.title_match_results)
            win.formatted_process_title = self._get_formatted_best_match(
                win.process_title, r.process_match_results
            )
            matched_windows.append(win)

        return matched_windows

    def _score(self, text: str, query_pattern: str) -> List[MatchResult]:
        if not query_pattern:
            return [MatchResult.non_match(text)]

        return [
            self.starts_with.evaluate(text, query_pattern),
            self.significant.evaluate(text, query_pattern),
            self.contains.evaluate(text, query_pattern),
            self.fuzzy.evaluate(text, query_pattern),
        ]

    @staticmethod
    def _get_formatted_best_match(original_text: str, match_results: List[MatchResult]) -> str:
        for r in match_results:
            if r.matched:
                return PangoHighlighter.highlight(r.string_parts)
        return PangoHighlighter.highlight(MatchResult.non_match(original_text).string_parts)
