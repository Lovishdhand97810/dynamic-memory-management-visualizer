# 🧠 Dynamic Memory Management Visualizer

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Interactive_App-FF4B4B?logo=streamlit&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data_Analysis-150458?logo=pandas&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-Visualizations-3F4F75?logo=plotly&logoColor=white)

An interactive Operating Systems simulator built with **Python, Streamlit, Pandas, and Plotly**. Designed for students, educators, and viva demonstrations, it visualizes **Paging, Segmentation, Virtual Memory, and Page Replacement algorithms (FIFO & LRU)** with step-by-step tracing and side-by-side performance comparisons.

> **100% Local & Open:** Runs completely offline on your machine with zero paid APIs or external dependencies.

---

## ✨ Key Features

| Module | Capabilities & Visualizations |
| :--- | :--- |
| **📄 Paging Simulator** | Calculates total pages/frames, builds page tables, measures internal fragmentation, renders contiguous vs. scattered frame-allocation grids, and performs logical-to-physical address translation. |
| **🧩 Segmentation Simulator** | Computes segment tables (`base`, `limit`, `end`) for Code, Data, Stack, and Heap segments; visualizes memory maps; validates memory overflow; and checks `(segment, offset)` bounds. |
| **💾 Virtual Memory Simulator** | Traces page-loading behavior across custom reference strings and frame counts, highlighting every page hit and page fault. |
| **🔄 FIFO & LRU Simulators** | Tracks frame contents at every step, displays queue/recency states, and includes a single-step inspector with fixed-slot frame tracking. |
| **📊 Algorithm Comparison** | Benchmarks **FIFO vs. LRU** on identical inputs with hit/fault ratios, side-by-side step traces, and interactive *Faults vs. Frames* graphs (including **Belady's Anomaly**). |

---

## 🚀 Quick Start

### 1. Prerequisites
Ensure you have **Python 3.9 or newer** installed on your system.

### 2. Installation
Clone the repository and install the required packages:

```bash
git clone [https://github.com/Lovishdhand97810/dynamic-memory-management-visualizer.git](https://github.com/Lovishdhand97810/dynamic-memory-management-visualizer.git)
cd dynamic-memory-management-visualizer

# Optional: Create and activate a virtual environment
python -m venv venv
source venv/bin/activate          # macOS / Linux
venv\Scripts\activate             # Windows

# Install dependencies
pip install -r requirements.txt
