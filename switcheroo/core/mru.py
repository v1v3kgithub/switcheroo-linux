"""Most-recently-used (MRU) ordering of desktop windows."""

from typing import Dict, Iterable, List, Sequence

from switcheroo.core.window_model import AppWindow


class MruTracker:
    """Tracks window XIDs in most-recently-used order, most recent first."""

    def __init__(self) -> None:
        self._order: List[int] = []

    @property
    def xids(self) -> List[int]:
        """Returns a copy of the tracked XIDs, most recently used first."""
        return list(self._order)

    def touch(self, xid: int) -> None:
        """Marks a window as the most recently used."""
        if xid in self._order:
            self._order.remove(xid)
        self._order.insert(0, xid)

    def forget(self, xid: int) -> None:
        """Stops tracking a window, e.g. once it has been closed."""
        if xid in self._order:
            self._order.remove(xid)

    def seed(self, xids: Iterable[int]) -> None:
        """Appends untracked XIDs, given most recent first, behind the tracked ones.

        Used to give windows that were focused before tracking began a sensible
        initial order without overriding activations already observed.
        """
        for xid in xids:
            if xid not in self._order:
                self._order.append(xid)

    def sort(self, windows: Sequence[AppWindow]) -> List[AppWindow]:
        """Returns windows in MRU order; untracked windows follow in their given order."""
        rank: Dict[int, int] = {xid: i for i, xid in enumerate(self._order)}
        untracked = len(rank)
        return sorted(windows, key=lambda w: rank.get(w.xid, untracked))
