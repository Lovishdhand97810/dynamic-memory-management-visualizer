"""Shared colours and CSS so every page looks consistent."""
import streamlit as st

# One palette used by CSS and Plotly charts
PRIMARY = "#2563EB"   # blue
FAULT = "#EF4444"     # red
HIT = "#10B981"       # green
FREE = "#E5E7EB"      # light grey
ACCENT = "#F59E0B"    # amber
SEGMENT_COLORS = {"Code": "#2563EB", "Data": "#10B981", "Stack": "#F59E0B", "Heap": "#8B5CF6"}
ALGO_COLORS = {"FIFO": "#F59E0B", "LRU": "#2563EB"}

_CSS = f"""
<style>
.block-container {{ padding-top: 2rem; max-width: 1200px; }}
.page-title {{ font-size: 2rem; font-weight: 700; margin-bottom: 0; }}
.page-subtitle {{ color: #6B7280; margin-bottom: 1.2rem; }}
div[data-testid="stMetric"] {{
    background: rgba(37, 99, 235, 0.06);
    border: 1px solid rgba(37, 99, 235, 0.25);
    border-radius: 10px; padding: 12px 16px;
}}
.frame-row {{ display: flex; gap: 10px; flex-wrap: wrap; margin: 8px 0 14px 0; }}
.frame-box {{
    min-width: 76px; padding: 10px 8px; text-align: center; border-radius: 8px;
    border: 2px solid #9CA3AF; background: {FREE}; color: #111827;
    font-weight: 700; font-size: 1.2rem;
}}
.frame-box small {{ display: block; font-weight: 400; font-size: 0.7rem; color: #4B5563; }}
.frame-box.loaded {{ background: #FEE2E2; border-color: {FAULT}; }}
.frame-box.hitbox {{ background: #D1FAE5; border-color: {HIT}; }}
.frame-box.filled {{ background: #DBEAFE; border-color: {PRIMARY}; }}
</style>
"""


def apply_styles() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)


def page_header(title: str, subtitle: str) -> None:
    st.markdown(f'<div class="page-title">{title}</div>'
                f'<div class="page-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def show_errors(errors) -> None:
    for e in errors:
        st.error(e)
