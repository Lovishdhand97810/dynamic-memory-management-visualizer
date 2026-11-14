"""Page replacement algorithms: FIFO and LRU (pure logic, no UI code).

Both functions return a PageReplacementResult that stores one `Step` per
page reference, so the UI (or a test) can replay what happened.
"""
from collections import deque
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Sequence, Tuple


@dataclass(frozen=True)
class Step:
    step: int                          # 1-based step number
    page: int                          # page requested at this step
    frames: Tuple[Optional[int], ...]  # frame contents AFTER the step (None = empty)
    hit: bool                          # True = page was already in memory
    evicted: Optional[int]             # page removed from memory (None if no eviction)
    slot: Optional[int]                # frame index that received the page (None on hit)
    order: Tuple[int, ...]             # FIFO: oldest->newest | LRU: least->most recently used


@dataclass
class PageReplacementResult:
    algorithm: str
    reference: List[int]
    num_frames: int
    steps: List[Step]

    @property
    def faults(self) -> int:
        return sum(1 for s in self.steps if not s.hit)

    @property
    def hits(self) -> int:
        return sum(1 for s in self.steps if s.hit)

    @property
    def total(self) -> int:
        return len(self.steps)

    @property
    def hit_ratio(self) -> float:
        return self.hits / self.total if self.total else 0.0

    @property
    def fault_ratio(self) -> float:
        return self.faults / self.total if self.total else 0.0


def _check(reference: Sequence[int], num_frames: int) -> None:
    if num_frames < 1:
        raise ValueError("num_frames must be at least 1")
    if len(reference) == 0:
        raise ValueError("reference string must not be empty")


def fifo(reference: Sequence[int], num_frames: int) -> PageReplacementResult:
    """First-In First-Out: evict the page that has been in memory the longest.

    A hit does NOT change the queue (that is what makes FIFO simple - and weak).
    """
    _check(reference, num_frames)
    frames: List[Optional[int]] = [None] * num_frames
    queue: deque = deque()              # pages in order of arrival (oldest on the left)
    steps: List[Step] = []

    for i, page in enumerate(reference, start=1):
        if page in frames:                                   # HIT
            steps.append(Step(i, page, tuple(frames), True, None, None, tuple(queue)))
            continue
        evicted = None                                       # FAULT
        if None in frames:                                   # a free frame exists
            slot = frames.index(None)
        else:                                                # memory full -> evict oldest
            evicted = queue.popleft()
            slot = frames.index(evicted)
        frames[slot] = page
        queue.append(page)
        steps.append(Step(i, page, tuple(frames), False, evicted, slot, tuple(queue)))
    return PageReplacementResult("FIFO", list(reference), num_frames, steps)


def lru(reference: Sequence[int], num_frames: int) -> PageReplacementResult:
    """Least Recently Used: evict the page that was used longest ago.

    Every access (hit OR fault) refreshes the page's "last used" time.
    """
    _check(reference, num_frames)
    frames: List[Optional[int]] = [None] * num_frames
    last_used: Dict[int, int] = {}      # page -> step number of its latest use
    steps: List[Step] = []

    for i, page in enumerate(reference, start=1):
        hit = page in frames
        evicted = None
        slot = None
        if not hit:
            if None in frames:
                slot = frames.index(None)
            else:
                evicted = min((p for p in frames), key=lambda p: last_used[p])
                slot = frames.index(evicted)
                del last_used[evicted]
            frames[slot] = page
        last_used[page] = i                                  # refresh recency
        order = tuple(sorted(last_used, key=lambda p: last_used[p]))
        steps.append(Step(i, page, tuple(frames), hit, evicted, slot, order))
    return PageReplacementResult("LRU", list(reference), num_frames, steps)


ALGORITHMS: Dict[str, Callable[[Sequence[int], int], PageReplacementResult]] = {
    "FIFO": fifo,
    "LRU": lru,
}


def run_algorithm(name: str, reference: Sequence[int], num_frames: int) -> PageReplacementResult:
    if name not in ALGORITHMS:
        raise ValueError(f"Unknown algorithm '{name}'. Choose from {list(ALGORITHMS)}")
    return ALGORITHMS[name](reference, num_frames)


def describe_step(step: Step) -> str:
    """One-sentence explanation of what happened at a step (for the page-load trace)."""
    if step.hit:
        return f"Page {step.page} is already in memory -> HIT (no change)."
    where = f"Frame {step.slot + 1}"
    if step.evicted is None:
        return f"Page {step.page} not in memory -> PAGE FAULT. Loaded into free {where}."
    return (f"Page {step.page} not in memory -> PAGE FAULT. Memory full: "
            f"evicted page {step.evicted}, loaded page {step.page} into {where}.")


def faults_by_frame_count(reference: Sequence[int], max_frames: int) -> Dict[str, List[int]]:
    """Page faults of every algorithm for 1..max_frames frames (for the sweep chart)."""
    return {name: [fn(reference, n).faults for n in range(1, max_frames + 1)]
            for name, fn in ALGORITHMS.items()}
