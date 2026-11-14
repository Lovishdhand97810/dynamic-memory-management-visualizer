"""Paging simulation (pure logic, no UI code).

Key ideas
---------
* A process is split into fixed-size *pages*.
* Physical memory is split into fixed-size *frames* (frame size = page size).
* A *page table* maps each page number to the frame that holds it.
* The last page is usually only partly used -> *internal fragmentation*.
"""
import math
import random
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class PageTableEntry:
    page: int
    frame: int
    bytes_used: int              # bytes of the process stored in this page
    internal_fragmentation: int  # wasted bytes inside this page


@dataclass
class PagingResult:
    process_size: int
    page_size: int
    memory_size: int
    total_pages: int
    total_frames: int
    fits: bool
    internal_fragmentation: int
    page_table: List[PageTableEntry] = field(default_factory=list)
    # frame_map[i] = page number stored in frame i, or None if the frame is free
    frame_map: List[Optional[int]] = field(default_factory=list)

    @property
    def free_frames(self) -> int:
        return sum(1 for f in self.frame_map if f is None)

    @property
    def leftover_memory(self) -> int:
        """Bytes at the end of memory too small to form a whole frame."""
        return self.memory_size % self.page_size


def simulate_paging(process_size: int, page_size: int, memory_size: int,
                    allocation: str = "sequential", seed: int = 42) -> PagingResult:
    """Divide a process into pages and place them into physical frames.

    allocation = "sequential": page i -> frame i (easy to read)
    allocation = "scattered" : pages go to random frames (shows that pages
                               need NOT be contiguous in memory)
    """
    if process_size <= 0 or page_size <= 0 or memory_size <= 0:
        raise ValueError("process_size, page_size and memory_size must be positive")
    if allocation not in ("sequential", "scattered"):
        raise ValueError("allocation must be 'sequential' or 'scattered'")

    total_pages = math.ceil(process_size / page_size)
    total_frames = memory_size // page_size
    internal_frag = total_pages * page_size - process_size
    fits = total_pages <= total_frames

    result = PagingResult(process_size, page_size, memory_size, total_pages,
                          total_frames, fits, internal_frag,
                          frame_map=[None] * total_frames)
    if not fits:
        return result  # nothing is allocated if the process does not fit

    if allocation == "sequential":
        frames = list(range(total_pages))
    else:
        frames = random.Random(seed).sample(range(total_frames), total_pages)

    for page, frame in enumerate(frames):
        used = page_size if page < total_pages - 1 else process_size - page * page_size
        result.page_table.append(
            PageTableEntry(page, frame, used, page_size - used))
        result.frame_map[frame] = page
    return result


@dataclass
class AddressTranslation:
    valid: bool
    message: str
    page: Optional[int] = None
    offset: Optional[int] = None
    frame: Optional[int] = None
    physical_address: Optional[int] = None


def translate_logical_address(address: int, result: PagingResult) -> AddressTranslation:
    """Logical address -> (page, offset) -> physical address."""
    if address < 0 or address >= result.process_size:
        return AddressTranslation(
            False, f"Invalid address: must be between 0 and {result.process_size - 1}.")
    if not result.fits:
        return AddressTranslation(False, "Process is not loaded (it does not fit in memory).")
    page, offset = divmod(address, result.page_size)
    frame = result.page_table[page].frame
    return AddressTranslation(
        True, "Translation successful.", page, offset, frame,
        frame * result.page_size + offset)
