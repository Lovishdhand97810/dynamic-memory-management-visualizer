import pandas as pd
import streamlit as st

from algorithms.page_replacement import ALGORITHMS, describe_step, run_algorithm
from ui import charts
from ui.styles import page_header
from views.components import reference_inputs, style_result_column, summary_metrics


def render() -> None:
    page_header("Virtual Memory Simulator",
                "Pages are loaded from disk into frames only when needed (demand paging).")
    st.info("When a process touches a page that is not in a frame, a **page fault** occurs: the OS loads "
            "the page from disk. If all frames are full, a replacement algorithm picks a victim page.")

    pages, frames = reference_inputs(prefix="vm")
    if pages is None:
        return
    algorithm = st.radio("Replacement algorithm", list(ALGORITHMS), horizontal=True)

    result = run_algorithm(algorithm, pages, frames)
    distinct = len(set(pages))
    if frames >= distinct:
        st.warning(f"There are {frames} frames but only {distinct} distinct pages, so only the "
                   f"{distinct} unavoidable first-time faults can occur.")
    st.success(f"{algorithm} finished: {result.faults} faults, {result.hits} hits.")
    summary_metrics(result)

    st.subheader("Page loading trace")
    trace = pd.DataFrame([{
        "Step": s.step, "Page": s.page, "Result": "HIT" if s.hit else "FAULT",
        "What happened": describe_step(s),
    } for s in result.steps])
    st.dataframe(style_result_column(trace), width="stretch", hide_index=True)

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(charts.cumulative_faults(result), width="stretch")
    with c2:
        st.plotly_chart(charts.frame_timeline(result), width="stretch")
