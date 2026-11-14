import pandas as pd
import streamlit as st

from algorithms.page_replacement import faults_by_frame_count, fifo, lru
from ui import charts
from ui.styles import page_header
from views.components import cell_text, reference_inputs


def render() -> None:
    page_header("Algorithm Comparison",
                "FIFO and LRU run on exactly the same reference string and number of frames.")
    pages, frames = reference_inputs(prefix="cmp")
    if pages is None:
        return

    f, l = fifo(pages, frames), lru(pages, frames)
    results = [f, l]

    if l.faults < f.faults:
        st.success(f"LRU wins: {l.faults} faults vs {f.faults} for FIFO "
                   f"({f.faults - l.faults} fewer).")
    elif f.faults < l.faults:
        st.warning(f"FIFO wins on this input: {f.faults} faults vs {l.faults} for LRU. "
                   "LRU is usually better, but not for every reference string.")
    else:
        st.info(f"Tie: both algorithms cause {f.faults} page faults on this input.")

    cols = st.columns(2)
    for col, r in zip(cols, results):
        with col:
            st.markdown(f"#### {r.algorithm}")
            a, b, c = st.columns(3)
            a.metric("Page faults", r.faults)
            b.metric("Page hits", r.hits)
            c.metric("Hit ratio", f"{r.hit_ratio * 100:.1f}%")

    st.subheader("Comparison table")
    table = pd.DataFrame([{
        "Algorithm": r.algorithm, "References": r.total, "Page faults": r.faults, "Page hits": r.hits,
        "Hit ratio": f"{r.hit_ratio * 100:.2f}%", "Fault ratio": f"{r.fault_ratio * 100:.2f}%",
    } for r in results])
    st.dataframe(table, width="stretch", hide_index=True)

    c1, c2 = st.columns(2)
    c1.plotly_chart(charts.comparison_bars(results), width="stretch")
    c2.plotly_chart(charts.hit_ratio_bars(results), width="stretch")

    st.subheader("Step-by-step side by side")
    rows = []
    for sf, sl in zip(f.steps, l.steps):
        row = {"Step": sf.step, "Page": sf.page}
        row["FIFO frames"] = " | ".join(cell_text(v) for v in sf.frames)
        row["FIFO"] = "HIT" if sf.hit else "FAULT"
        row["LRU frames"] = " | ".join(cell_text(v) for v in sl.frames)
        row["LRU"] = "HIT" if sl.hit else "FAULT"
        rows.append(row)
    df = pd.DataFrame(rows)
    styled = df.style.apply(_colour, subset=["FIFO"]).apply(_colour, subset=["LRU"])
    st.dataframe(styled, width="stretch", hide_index=True)

    st.subheader("What if we change the number of frames?")
    max_frames = min(max(len(set(pages)), frames), 20)
    st.plotly_chart(charts.frames_sweep(faults_by_frame_count(pages, max_frames), frames),
                    width="stretch")
    st.caption("More frames normally means fewer faults. FIFO can break this rule "
               "(Belady's anomaly) – try the 'Belady's anomaly' example above.")


def _colour(col):
    return [f"background-color: {'#D1FAE5' if v == 'HIT' else '#FEE2E2'}; font-weight: 600" for v in col]
