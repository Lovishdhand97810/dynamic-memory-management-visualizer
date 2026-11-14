"""Segmentation simulation (pure logic, no UI code).

A process is split into logical segments (Code, Data, Stack, Heap).
Each segment has a BASE (where it starts in physical memory) and a
LIMIT (its length). A logical address is (segment, offset) and is valid
only when offset < limit.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional

SEGMENT_NAMES = ("Code", "Data", "Stack", "Heap")


@dataclass
class Segment:
    name: str
    base: int
    limit: int

    @property
    def end(self) -> int:
        """Last valid physical address of the segment."""
        return self.base + self.limit - 1


@dataclass
class SegmentationResult:
    memory_size: int
    segments: List[Segment] = field(default_factory=list)

    @property
    def total_used(self) -> int:
        return sum(s.limit for s in self.segments)

    @property
    def free(self) -> int:
        return max(self.memory_size - self.total_used, 0)

    @property
    def overflow(self) -> int:
        return max(self.total_used - self.memory_size, 0)

    @property
    def fits(self) -> bool:
        return self.total_used <= self.memory_size

    @property
    def utilization(self) -> float:
        return min(self.total_used / self.memory_size, 1.0) * 100

    def within_memory(self, seg: Segment) -> bool:
        return seg.end < self.memory_size


def build_segment_table(sizes: Dict[str, int], memory_size: int) -> SegmentationResult:
    """Place segments one after another starting at physical address 0."""
    if memory_size <= 0:
        raise ValueError("memory_size must be positive")
    result = SegmentationResult(memory_size)
    base = 0
    for name in SEGMENT_NAMES:
        size = sizes[name]
        if size <= 0:
            raise ValueError(f"{name} segment size must be positive")
        result.segments.append(Segment(name, base, size))
        base += size
    return result


@dataclass
class SegmentTranslation:
    valid: bool
    message: str
    physical_address: Optional[int] = None


def translate_segment_address(result: SegmentationResult, segment_name: str,
                              offset: int) -> SegmentTranslation:
    """(segment, offset) -> physical address, with boundary checking."""
    seg = next((s for s in result.segments if s.name == segment_name), None)
    if seg is None:
        return SegmentTranslation(False, f"Unknown segment '{segment_name}'.")
    if offset < 0:
        return SegmentTranslation(False, "Offset cannot be negative.")
    if offset >= seg.limit:
        return SegmentTranslation(
            False, f"Segmentation fault: offset {offset} >= limit {seg.limit} of {seg.name}.")
    physical = seg.base + offset
    if physical >= result.memory_size:
        return SegmentTranslation(
            False, f"Address {physical} is outside physical memory (size {result.memory_size}).")
    return SegmentTranslation(True, "Access allowed.", physical)
