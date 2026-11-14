"""Input validation helpers. Each function returns a list of error messages
(empty list = input is valid) so the UI can show them all at once."""
from typing import Dict, List, Optional, Tuple

MAX_UNITS = 1024          # max pages / frames we will draw on screen
MAX_REFERENCE_LENGTH = 200
MAX_PAGE_NUMBER = 999
MAX_REPLACEMENT_FRAMES = 30


def _is_positive_int(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def validate_paging_inputs(process_size, page_size, memory_size) -> List[str]:
    errors = []
    for label, v in (("Process size", process_size), ("Page size", page_size),
                     ("Physical memory size", memory_size)):
        if not _is_positive_int(v):
            errors.append(f"{label} must be a positive whole number.")
    if errors:
        return errors
    if page_size > memory_size:
        errors.append("Page size cannot be larger than physical memory.")
        return errors
    pages = -(-process_size // page_size)
    frames = memory_size // page_size
    if pages > MAX_UNITS:
        errors.append(f"This gives {pages} pages; the visualizer supports at most {MAX_UNITS}. "
                      "Use a larger page size or a smaller process.")
    if frames > MAX_UNITS:
        errors.append(f"This gives {frames} frames; the visualizer supports at most {MAX_UNITS}. "
                      "Use a larger page size or less memory.")
    return errors


def validate_segment_inputs(sizes: Dict[str, int], memory_size) -> List[str]:
    errors = []
    if not _is_positive_int(memory_size):
        errors.append("Physical memory size must be a positive whole number.")
    for name, v in sizes.items():
        if not _is_positive_int(v):
            errors.append(f"{name} segment size must be a positive whole number.")
    return errors


def parse_reference_string(text: str) -> Tuple[Optional[List[int]], List[str]]:
    """Turn '7, 0 1 2' into [7, 0, 1, 2]. Commas and/or spaces may separate numbers."""
    tokens = text.replace(",", " ").split()
    if not tokens:
        return None, ["Enter at least one page number (e.g. 7 0 1 2 0 3)."]
    pages, errors = [], []
    for tok in tokens:
        if not (tok.isascii() and tok.isdigit()):
            errors.append(f"'{tok}' is not a valid page number (use whole numbers 0 or greater).")
        else:
            pages.append(int(tok))
    if errors:
        return None, errors[:5]
    if len(pages) > MAX_REFERENCE_LENGTH:
        return None, [f"Reference string is too long ({len(pages)}). Maximum is {MAX_REFERENCE_LENGTH}."]
    if max(pages) > MAX_PAGE_NUMBER:
        return None, [f"Page numbers must be at most {MAX_PAGE_NUMBER}."]
    return pages, []


def validate_frame_count(num_frames) -> List[str]:
    if not _is_positive_int(num_frames):
        return ["Number of frames must be a positive whole number."]
    if num_frames > MAX_REPLACEMENT_FRAMES:
        return [f"Number of frames must be at most {MAX_REPLACEMENT_FRAMES}."]
    return []
