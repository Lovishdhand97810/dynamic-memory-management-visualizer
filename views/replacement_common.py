"""One shared page used by both the FIFO and the LRU pages (no duplicated code)."""
import streamlit as st

from algorithms.page_replacement import describe_step, run_algorithm
from ui import charts
from ui.styles import page_header
from views.components import (frame_boxes, reference_inputs, steps_dataframe,
                              style_result_column, summary_metrics)


def render_replacement_page(algorithm: str, subtitle: str, rule: str) -> None:
    page_header(f"{algorithm} Page Replacement", subtitle)
    st.info(rule)

    pages, frames = reference_inputs(prefix=algorithm.lower())
    if pages is None:
        return

    result = run_algorithm(algorithm, pages, frames)
    st.success(f"Simulation complete: {result.faults} page faults and {result.hits} hits "
               f"in {result.total} references.")
    summary_metrics(result)

    st.subheader("Frame changes at every step")
    st.plotly_chart(charts.frame_timeline(result), width="stretch")

    st.subheader("Step-by-step table")
    df = steps_dataframe(result)
    st.dataframe(style_result_column(df), width="stretch", hide_index=True)

    st.subheader("Inspect a single step")
    if result.total > 1:
        n = st.slider("Step", 1, result.total, 1)
    else:
        n = 1
    step = result.steps[n - 1]
    st.write(f"**Step {step.step}:** request for page **{step.page}**")
    frame_boxes(step)
    if step.hit:
        st.success(describe_step(step))
    else:
        st.error(describe_step(step))
