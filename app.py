"""Dynamic Memory Management Visualizer - main entry point.

Run with:  streamlit run app.py
"""
import streamlit as st

from ui.styles import apply_styles
from views import (comparison_page, fifo_page, home, lru_page, paging_page,
                   segmentation_page, virtual_memory_page)

st.set_page_config(page_title="Memory Management Visualizer", page_icon="🧠", layout="wide")
apply_styles()

PAGES = {
    "🏠 Home": home.render,
    "📄 Paging Simulator": paging_page.render,
    "🧩 Segmentation Simulator": segmentation_page.render,
    "💾 Virtual Memory Simulator": virtual_memory_page.render,
    "⏩ FIFO Page Replacement": fifo_page.render,
    "🕒 LRU Page Replacement": lru_page.render,
    "📊 Algorithm Comparison": comparison_page.render,
}

st.sidebar.title("🧠 Memory Visualizer")
choice = st.sidebar.radio("Navigation", list(PAGES), label_visibility="collapsed")
st.sidebar.divider()
st.sidebar.caption("Operating Systems project · Python, Streamlit, Pandas, Plotly")

PAGES[choice]()
