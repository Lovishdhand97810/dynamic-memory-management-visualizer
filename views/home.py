import streamlit as st

from ui.styles import page_header


def render() -> None:
    page_header("Dynamic Memory Management Visualizer",
                "An interactive tool for learning paging, segmentation and virtual memory.")
    st.info("Use the **sidebar** to open a module. All sizes are in **bytes**.")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
**Memory organisation**
- **Paging Simulator** – split a process into pages, fill frames, view the page table and internal fragmentation.
- **Segmentation Simulator** – lay out Code, Data, Stack and Heap; check base/limit boundaries.
""")
    with c2:
        st.markdown("""
**Virtual memory & replacement**
- **Virtual Memory Simulator** – watch pages load, hit and fault.
- **FIFO / LRU Replacement** – step-by-step frame changes.
- **Algorithm Comparison** – FIFO vs LRU on identical input.
""")

    st.subheader("Key terms")
    st.markdown("""
| Term | Meaning |
|---|---|
| Page / Frame | Fixed-size block of logical / physical memory (same size) |
| Page table | Maps each page to the frame that holds it |
| Internal fragmentation | Unused bytes inside the last, partly-filled page |
| Segment | Variable-size logical unit (code, data, stack, heap) with a base and a limit |
| Page fault | The requested page is not in a frame, so the OS must load it |
| Hit ratio | Hits ÷ total references |
""")
