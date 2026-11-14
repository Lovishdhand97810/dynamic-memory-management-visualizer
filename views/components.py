"""Reusable Streamlit widgets and table builders shared by several pages."""
from typing import List, Optional, Tuple

import pandas as pd
import streamlit as st

from algorithms.page_replacement import PageReplacementResult, Step
from ui.styles import FAULT, HIT, show_errors
from utils.validation import (MAX_REPLACEMENT_FRAMES, parse_reference_string,
                              validate_frame_count)

EXAMPLES = {
    "Textbook example": "7 0 1 2 0 3 0 4 2 3 0 3 2 1 2 0 1 7 0 1",
    "Belady's anomaly": "1 2 3 4 1 2 5 1 2 3 4 5",
    "Strong locality": "1 2 1 3 1 2 1 4 1 2 1 3 1 2",
    "Custom": None,
}


def reference_inputs(prefix: str, default_frames: int = 3) -> Tuple[Optional[List[int]], Optional[int]]:
    """Draw the reference-string + frame-count inputs. Returns (pages, frames),
    or (None, None) after showing error messages if the input is invalid."""
    text_key, ex_key, frames_key = f"{prefix}_text", f"{prefix}_example", f"{prefix}_frames"
    if text_key not in st.session_state:
        st.session_state[text_key] = EXAMPLES["Textbook example"]
    if ex_key not in st.session_state:
        st.session_state[ex_key] = "Textbook example"

    def load_example():
        chosen = EXAMPLES[st.session_state[ex_key]]
        if chosen is not None:
            st.session_state[text_key] = chosen

    col1, col2 = st.columns([3, 1])
    with col1:
        st.selectbox("Example reference strings", list(EXAMPLES), key=ex_key, on_change=load_example)
        st.text_input("Page reference string (separate numbers with spaces or commas)", key=text_key)
    with col2:
        frames = st.number_input("Number of frames", min_value=1, max_value=MAX_REPLACEMENT_FRAMES,
                                 value=default_frames, step=1, key=frames_key)
    frames = int(frames)

    pages, errors = parse_reference_string(st.session_state[text_key])
    errors = errors + validate_frame_count(frames)
    if errors:
        show_errors(errors)
        return None, None
    return pages, frames


def cell_text(v: Optional[int]) -> str:
    return "–" if v is None else str(v)


def steps_dataframe(result: PageReplacementResult, show_order: bool = True) -> pd.DataFrame:
    order_label = "Queue (oldest → newest)" if result.algorithm == "FIFO" else "Recency (least → most recent)"
    rows = []
    for s in result.steps:
        row = {"Step": s.step, "Page": s.page}
        for i, v in enumerate(s.frames):
            row[f"Frame {i + 1}"] = cell_text(v)
        row["Result"] = "HIT" if s.hit else "FAULT"
        row["Evicted"] = cell_text(s.evicted)
        if show_order:
            row[order_label] = " → ".join(map(str, s.order))
        rows.append(row)
    return pd.DataFrame(rows)


def style_result_column(df: pd.DataFrame, column: str = "Result"):
    """Colour HIT cells green and FAULT cells red."""
    def colour(col):
        return [f"background-color: {'#D1FAE5' if v == 'HIT' else '#FEE2E2'}; "
                f"color: {HIT if v == 'HIT' else FAULT}; font-weight: 600" for v in col]
    return df.style.apply(colour, subset=[column])


def frame_boxes(step: Step) -> None:
    """Show the frames after a single step as coloured boxes."""
    boxes = []
    for i, page in enumerate(step.frames):
        if page is None:
            css, label = "", "empty"
        elif not step.hit and i == step.slot:
            css, label = "loaded", str(page)
        elif step.hit and page == step.page:
            css, label = "hitbox", str(page)
        else:
            css, label = "filled", str(page)
        boxes.append(f'<div class="frame-box {css}"><small>Frame {i + 1}</small>{label}</div>')
    st.markdown(f'<div class="frame-row">{"".join(boxes)}</div>', unsafe_allow_html=True)


def summary_metrics(result: PageReplacementResult) -> None:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total references", result.total)
    c2.metric("Page faults", result.faults)
    c3.metric("Page hits", result.hits)
    c4.metric("Hit ratio", f"{result.hit_ratio * 100:.1f}%")
