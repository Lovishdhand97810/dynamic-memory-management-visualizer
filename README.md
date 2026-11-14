# Dynamic Memory Management Visualizer

An interactive Operating Systems project built with **Python, Streamlit, Pandas and Plotly**.
It simulates **paging, segmentation, virtual memory, FIFO and LRU page replacement**, and
compares the two algorithms. Everything runs locally; no paid APIs or services are used.

## Features

| Page | What it does |
|---|---|
| Paging Simulator | Process size / page size / memory → total pages and frames, page table, internal fragmentation, frame-allocation grid, logical→physical address translation |
| Segmentation Simulator | Code / Data / Stack / Heap sizes → segment table (base, limit, end), memory map, usage, boundary validation, (segment, offset) access check |
| Virtual Memory Simulator | Reference string + number of frames + algorithm → page-loading trace with hits and faults |
| FIFO Page Replacement | Frame contents at every step, queue state, single-step inspector |
| LRU Page Replacement | Same, with recency order |
| Algorithm Comparison | FIFO vs LRU on identical input: faults, hits, hit ratio, charts, side-by-side steps, faults-vs-frames graph |

## Installation

Requires **Python 3.9 or newer**.

```bash
cd memory_visualizer

# optional but recommended: virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

## Run the app

```bash
streamlit run app.py
```

Streamlit prints a local address (normally <http://localhost:8501>) and opens it in your browser.

## Run the tests

```bash
python -m unittest discover -s tests -v
```

* `tests/test_algorithms.py` – 26 tests for paging, segmentation, FIFO, LRU and validation.
  It includes textbook results, Belady's anomaly, and a cross-check of FIFO/LRU against
  separate, deliberately simple implementations on 500 random inputs.
* `tests/test_ui_smoke.py` – opens every page headlessly and checks that results and error messages appear.

Sample inputs and expected outputs for manual demonstration are in **`docs/TEST_CASES.md`**.

## Project structure

```
memory_visualizer/
├── app.py                      # entry point: sidebar navigation only
├── requirements.txt
├── README.md
├── algorithms/                 # PURE LOGIC - no Streamlit imports
│   ├── paging.py               #   pages, frames, page table, fragmentation, translation
│   ├── segmentation.py         #   segment table, limits, boundary check
│   └── page_replacement.py     #   FIFO, LRU, step descriptions, frame sweep
├── utils/
│   └── validation.py           # input validation (returns lists of error messages)
├── ui/
│   ├── styles.py               # shared colours + CSS
│   └── charts.py               # Plotly figures (drawing only)
├── views/                      # one file per page of the dashboard
│   ├── home.py, paging_page.py, segmentation_page.py, virtual_memory_page.py
│   ├── fifo_page.py, lru_page.py, comparison_page.py
│   ├── replacement_common.py   # shared layout for the FIFO and LRU pages
│   └── components.py           # shared inputs and tables
├── tests/
└── docs/TEST_CASES.md
```

**Design rule:** `algorithms/` never imports Streamlit, so it can be tested and explained on its own.
The UI only calls these functions and draws the results.

## How the algorithms work (for your viva / presentation)

**Paging**
- pages = ⌈process size ÷ page size⌉, frames = ⌊memory ÷ page size⌋
- internal fragmentation = pages × page size − process size (always inside the last page)
- logical address → `page = address ÷ page size`, `offset = address mod page size`;
  physical address = `frame × page size + offset`

**Segmentation**
- Segments are placed one after another starting at address 0: `base(n) = base(n−1) + limit(n−1)`
- An access `(segment, offset)` is allowed only if `offset < limit`; otherwise a *segmentation fault* is reported.
- If total segment size is larger than memory, the table is still shown but segments beyond the end of memory are flagged.

**FIFO** – a queue records the order pages arrived. On a fault with full frames, the page at the
front of the queue (the oldest) is replaced. Hits do not change the queue.
It can suffer from *Belady's anomaly* (more frames → more faults); try the "Belady's anomaly" example.

**LRU** – each page remembers when it was last used (hit *or* fault). On a fault with full frames, the page
with the oldest last-use time is replaced. LRU does not suffer from Belady's anomaly.

Frames are shown as fixed slots: a new page takes the slot of the page it replaces, so you can see
exactly which frame changed at each step.

## Suggested demonstration (5 minutes)

1. **Paging** – keep the defaults; point out 11 pages, 16 frames, 764 bytes wasted. Switch to *Scattered* to show non-contiguous allocation. Translate address 2500.
2. **Segmentation** – defaults fit; then reduce memory to 2000 and show the overflow error. Test `Stack` offset 300 for a segmentation fault.
3. **FIFO** and **LRU** – use the textbook example with 3 frames and walk through steps 4–6 with the step slider.
4. **Comparison** – FIFO 15 faults vs LRU 12. Select "Belady's anomaly" and use the faults-vs-frames graph.

## Limits (by design, to keep the visualisation readable)

Up to 1024 pages/frames in the paging simulator, up to 200 page references, page numbers 0–999 and up to 30 frames in the replacement simulators.
All memory sizes are in bytes.
