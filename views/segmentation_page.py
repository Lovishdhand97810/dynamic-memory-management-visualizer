import pandas as pd
import streamlit as st

from algorithms.segmentation import (SEGMENT_NAMES, build_segment_table,
                                     translate_segment_address)
from ui import charts
from ui.styles import page_header, show_errors
from utils.validation import validate_segment_inputs

DEFAULTS = {"Code": 1000, "Data": 500, "Stack": 300, "Heap": 700}


def render() -> None:
    page_header("Segmentation Simulator",
                "Place Code, Data, Stack and Heap segments in memory and check their boundaries.")

    memory = int(st.number_input("Physical memory (bytes)", min_value=1, value=4096, step=256))
    cols = st.columns(4)
    sizes = {name: int(col.number_input(f"{name} size (bytes)", min_value=1, value=DEFAULTS[name], step=50))
             for name, col in zip(SEGMENT_NAMES, cols)}

    errors = validate_segment_inputs(sizes, memory)
    if errors:
        show_errors(errors)
        return
    res = build_segment_table(sizes, memory)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Memory used", f"{res.total_used} bytes")
    m2.metric("Free memory", f"{res.free} bytes")
    m3.metric("Utilisation", f"{res.utilization:.1f}%")
    m4.metric("Segments", len(res.segments))

    if res.fits:
        st.success("All segments fit inside physical memory.")
    else:
        st.error(f"Memory overflow: segments need {res.total_used} bytes but memory is only {memory} bytes "
                 f"({res.overflow} bytes too many).")

    st.subheader("Segment table")
    table = pd.DataFrame([{
        "Segment": i, "Name": s.name, "Base": s.base, "Limit": s.limit, "End address": s.end,
        "Status": "✅ Within memory" if res.within_memory(s) else "❌ Exceeds memory",
    } for i, s in enumerate(res.segments)])
    st.dataframe(table, width="stretch", hide_index=True)

    st.subheader("Memory map")
    st.plotly_chart(charts.segment_map(res), width="stretch")
    if res.fits:
        st.plotly_chart(charts.usage_pie(res), width="stretch")

    st.subheader("Check a memory access (boundary validation)")
    c1, c2 = st.columns(2)
    seg_name = c1.selectbox("Segment", SEGMENT_NAMES)
    offset = int(c2.number_input("Offset within segment", min_value=0, value=0, step=1))
    t = translate_segment_address(res, seg_name, offset)
    if t.valid:
        base = next(s.base for s in res.segments if s.name == seg_name)
        st.success(f"{t.message} Physical address = base {base} + offset {offset} = **{t.physical_address}**")
    else:
        st.error(t.message)
