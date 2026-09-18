"""Core functionality package."""

from switcheroo.core.window_model import AppWindow
from switcheroo.core.window_finder import WindowFinder
from switcheroo.core.filterer import WindowFilterer, FilterResult

__all__ = ["AppWindow", "WindowFinder", "WindowFilterer", "FilterResult"]
