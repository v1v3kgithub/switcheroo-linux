"""Pango markup highlighter for search match results."""

import html
from typing import Sequence
from switcheroo.core.matchers.base import StringPart


class PangoHighlighter:
    """Formats string parts into Pango markup with bold tags for matching characters."""

    @staticmethod
    def highlight(parts: Sequence[StringPart]) -> str:
        if not parts:
            return ""

        output = []
        for part in parts:
            escaped_val = html.escape(part.value)
            if part.is_match:
                output.append(f"<b>{escaped_val}</b>")
            else:
                output.append(escaped_val)

        return "".join(output)
