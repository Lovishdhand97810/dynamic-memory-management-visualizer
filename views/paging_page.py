import pandas as pd
import streamlit as st

from algorithms.paging import simulate_paging, translate_logical_address
from ui import charts
from ui.styles import page_header, show_errors
from utils.validation import validate_paging_inputs


def render() -> None:
    page_header("Paging Simulator",
                "Divide a process into pages and place them into physical memory frames.")

    c1, c2, c3 = st.columns(3)
    process = int(c1.number_input("Process size (bytes)", min_value=1, value=10500, step=100))
    page = int(c2.number_input("Page size (bytes)", min_value=1, value=1024, step=64))
    memory = int(c3.number_input("Physical memory (bytes)", min_value=1, value=16384, step=1024))
    mode = st.radio("Frame allocation", ["Sequential", "Scattered (random frames)"], horizontal=True,
                    help="Real systems place pages in any free frame. 'Scattered' shows this.")

    errors = validate_paging_inputs(process, page, memory)
    if errors:
        show_errors(errors)
        return
    if page & (page - 1):
        st.warning("Page size is not a power of two. Real systems use powers of two "
                   "(so addresses split cleanly into page number + offset), but the simulation still works.")

    res = simulate_paging(process, page, memory,
                          "sequential" if mode == "Sequential" else "scattered")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total pages", res.total_pages)
    m2.metric("Total frames", res.total_frames)
    m3.metric("Internal fragmentation", f"{res.internal_fragmentation} bytes")
    m4.metric("Free frames", res.free_frames)

    if not res.fits:
        st.error(f"Process does NOT fit: it needs {res.total_pages} frames but memory has only "
                 f"{res.total_frames}. Increase memory, reduce process size or use a larger page size.")
        return
    st.success(f"Process loaded successfully into {res.total_pages} of {res.total_frames} frames.")
    if res.leftover_memory:
        st.caption(f"Note: {res.leftover_memory} bytes of memory are left over because they "
                   "cannot form a complete frame.")

    st.subheader("Frame allocation")
    st.plotly_chart(charts.frame_grid(res), width="stretch")

    st.subheader("Page table")
    table = pd.DataFrame([{"Page": e.page, "Frame": e.frame, "Bytes used": e.bytes_used,
                           "Wasted bytes": e.internal_fragmentation} for e in res.page_table])
    st.dataframe(table, width="stretch", hide_index=True)

    with st.expander("How internal fragmentation is calculated"):
        last = res.page_table[-1]
        st.markdown(f"""
- Pages needed = ⌈{process} ÷ {page}⌉ = **{res.total_pages}**
- Space allocated = {res.total_pages} × {page} = **{res.total_pages * page}** bytes
- Internal fragmentation = {res.total_pages * page} − {process} = **{res.internal_fragmentation}** bytes
  (all of it is in the last page, which uses only {last.bytes_used} of {page} bytes)
""")

    st.subheader("Address translation")
    addr = int(st.number_input("Logical address to translate", min_value=0, value=min(2500, process - 1),
                               step=1, help=f"Valid range: 0 to {process - 1}"))
    t = translate_logical_address(addr, res)
    if t.valid:
        st.success(f"Logical address {addr} → page {t.page}, offset {t.offset} → frame {t.frame} → "
                   f"physical address {t.frame} × {page} + {t.offset} = **{t.physical_address}**")
    else:
        st.error(t.message)
