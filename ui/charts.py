"""Plotly figure builders. They only draw; all calculations come from /algorithms."""
from typing import List, Optional, Sequence

import plotly.graph_objects as go

from algorithms.page_replacement import PageReplacementResult
from algorithms.paging import PagingResult
from algorithms.segmentation import SegmentationResult
from ui.styles import ALGO_COLORS, FAULT, FREE, HIT, PRIMARY, SEGMENT_COLORS

_LAYOUT = dict(margin=dict(l=10, r=10, t=50, b=10), template="plotly_white")


def frame_grid(result: PagingResult, columns: int = 8) -> go.Figure:
    """Physical memory drawn as a grid of frames (blue = used, grey = free)."""
    n = result.total_frames
    rows = -(-n // columns)
    z = [[None] * columns for _ in range(rows)]
    text = [[""] * columns for _ in range(rows)]
    hover = [[""] * columns for _ in range(rows)]
    for f, page in enumerate(result.frame_map):
        r, c = divmod(f, columns)
        z[r][c] = 0 if page is None else 1
        text[r][c] = "free" if page is None else f"P{page}"
        hover[r][c] = (f"Frame {f}: free" if page is None
                       else f"Frame {f}: page {page}")
    fig = go.Figure(go.Heatmap(
        z=z, text=text, hovertext=hover, texttemplate="%{text}", hovertemplate="%{hovertext}<extra></extra>",
        colorscale=[[0, FREE], [1, PRIMARY]], zmin=0, zmax=1, showscale=False,
        xgap=4, ygap=4))
    fig.update_xaxes(showticklabels=False, showgrid=False, zeroline=False)
    fig.update_yaxes(showticklabels=False, showgrid=False, zeroline=False, autorange="reversed")
    fig.update_layout(title="Physical memory (frame numbers increase left→right, top→bottom)",
                      height=min(80 + rows * 55, 700), **_LAYOUT)
    return fig


def segment_map(result: SegmentationResult) -> go.Figure:
    """Memory map: one horizontal bar split into segments + free space."""
    fig = go.Figure()
    for seg in result.segments:
        fig.add_trace(go.Bar(
            y=["Memory"], x=[seg.limit], orientation="h", name=seg.name,
            marker_color=SEGMENT_COLORS[seg.name], text=seg.name, textposition="inside",
            hovertemplate=f"{seg.name}<br>Base {seg.base}<br>Limit {seg.limit}<br>"
                          f"End {seg.end}<extra></extra>"))
    if result.free:
        fig.add_trace(go.Bar(y=["Memory"], x=[result.free], orientation="h", name="Free",
                             marker_color=FREE, text="Free", textposition="inside",
                             hovertemplate=f"Free: {result.free} bytes<extra></extra>"))
    fig.add_vline(x=result.memory_size, line_dash="dash", line_color=FAULT,
                  annotation_text="end of memory", annotation_position="top")
    fig.update_layout(barmode="stack", height=220, title="Physical memory map (bytes)",
                      xaxis_title="Physical address", yaxis_visible=False,
                      legend=dict(orientation="h", y=-0.5), **_LAYOUT)
    return fig


def usage_pie(result: SegmentationResult) -> go.Figure:
    labels = [s.name for s in result.segments] + ["Free"]
    values = [s.limit for s in result.segments] + [result.free]
    colors = [SEGMENT_COLORS[s.name] for s in result.segments] + [FREE]
    fig = go.Figure(go.Pie(labels=labels, values=values, marker=dict(colors=colors), hole=0.45,
                           sort=False))
    fig.update_layout(title="Memory usage", height=300, **_LAYOUT)
    return fig


def frame_timeline(result: PageReplacementResult) -> go.Figure:
    """Frames (rows) over time (columns). Red = page just loaded (fault),
    green = page found in frame (hit), blue = unchanged, grey = empty."""
    n = result.num_frames
    z = [[0] * result.total for _ in range(n)]
    text = [[""] * result.total for _ in range(n)]
    hover = [[""] * result.total for _ in range(n)]
    for j, s in enumerate(result.steps):
        for i in range(n):
            page = s.frames[i]
            if page is None:
                state, label = 0, ""
            elif not s.hit and i == s.slot:
                state, label = 2, str(page)
            elif s.hit and page == s.page:
                state, label = 3, str(page)
            else:
                state, label = 1, str(page)
            z[i][j], text[i][j] = state, label
            hover[i][j] = (f"Step {s.step}: request page {s.page} → "
                           f"{'HIT' if s.hit else 'FAULT'}<br>Frame {i + 1}: "
                           f"{'empty' if page is None else 'page ' + str(page)}")
    # 4 discrete colour bins for z = 0,1,2,3
    colors = [FREE, "#BFDBFE", "#FCA5A5", "#6EE7B7"]
    scale = []
    for k, c in enumerate(colors):
        scale += [[k / 4, c], [(k + 1) / 4, c]]
    fig = go.Figure(go.Heatmap(
        z=z, text=text, hovertext=hover, texttemplate="%{text}",
        hovertemplate="%{hovertext}<extra></extra>", colorscale=scale, zmin=-0.5, zmax=3.5,
        showscale=False, xgap=3, ygap=3, x=list(range(1, result.total + 1)),
        y=[f"Frame {i + 1}" for i in range(n)]))
    fig.update_xaxes(tickmode="array", tickvals=list(range(1, result.total + 1)),
                     ticktext=[str(p) for p in result.reference], side="top",
                     title="Page reference string (request order)")
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(title=f"{result.algorithm}: frame contents at every step "
                            "(red = loaded on fault, green = hit, blue = unchanged)",
                      height=120 + 55 * n,
                      **{**_LAYOUT, "margin": dict(l=10, r=10, t=110, b=10)})
    return fig


def cumulative_faults(result: PageReplacementResult) -> go.Figure:
    total, xs, ys = 0, [], []
    for s in result.steps:
        total += 0 if s.hit else 1
        xs.append(s.step)
        ys.append(total)
    fig = go.Figure(go.Scatter(x=xs, y=ys, mode="lines+markers", line=dict(color=FAULT),
                               name="Cumulative faults"))
    fig.update_layout(title="Cumulative page faults", xaxis_title="Step",
                      yaxis_title="Faults so far", height=300, **_LAYOUT)
    return fig


def comparison_bars(results: Sequence[PageReplacementResult]) -> go.Figure:
    names = [r.algorithm for r in results]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=names, y=[r.faults for r in results], name="Page faults",
                         marker_color=FAULT, text=[r.faults for r in results], textposition="outside"))
    fig.add_trace(go.Bar(x=names, y=[r.hits for r in results], name="Page hits",
                         marker_color=HIT, text=[r.hits for r in results], textposition="outside"))
    fig.update_layout(barmode="group", title="Page faults vs page hits", yaxis_title="Count",
                      height=380, **_LAYOUT)
    return fig


def hit_ratio_bars(results: Sequence[PageReplacementResult]) -> go.Figure:
    fig = go.Figure(go.Bar(
        x=[r.algorithm for r in results], y=[r.hit_ratio * 100 for r in results],
        marker_color=[ALGO_COLORS[r.algorithm] for r in results],
        text=[f"{r.hit_ratio * 100:.1f}%" for r in results], textposition="outside"))
    fig.update_layout(title="Hit ratio (%)", yaxis=dict(range=[0, 110], title="%"),
                      height=380, **_LAYOUT)
    return fig


def frames_sweep(sweep: dict, selected_frames: Optional[int] = None) -> go.Figure:
    fig = go.Figure()
    for name, faults in sweep.items():
        fig.add_trace(go.Scatter(x=list(range(1, len(faults) + 1)), y=faults, mode="lines+markers",
                                 name=name, line=dict(color=ALGO_COLORS[name])))
    if selected_frames:
        fig.add_vline(x=selected_frames, line_dash="dot", annotation_text="your choice")
    fig.update_layout(title="Page faults as the number of frames grows", xaxis_title="Number of frames",
                      yaxis_title="Page faults", height=380, **_LAYOUT)
    return fig
