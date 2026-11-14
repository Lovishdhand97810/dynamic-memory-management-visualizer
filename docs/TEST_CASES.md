# Sample Test Cases and Expected Outputs

All values below were produced by the code and are also asserted in `tests/test_algorithms.py`.
Sizes are in bytes.

## 1. Paging Simulator

| # | Process | Page size | Memory | Expected result |
|---|---|---|---|---|
| P1 | 10500 | 1024 | 16384 | 11 pages, 16 frames, internal fragmentation **764**, 5 free frames. Page 10 uses 260 bytes. Success message. |
| P2 | 4096 | 1024 | 8192 | 4 pages, 8 frames, fragmentation **0** |
| P3 | 5000 | 1000 | 3000 | 5 pages, 3 frames → red error "Process does NOT fit" |
| P4 | 1000 | 300 | 2000 | 4 pages, 6 frames, fragmentation **200**, warning (page size not a power of two), note about 200 leftover bytes |
| P5 | 0 | 1024 | 4096 | Input rejected (inputs have a minimum of 1; the validator also rejects 0) |
| P6 | 100000 | 1 | 100000 | Error: too many pages/frames to display (limit 1024) |

**Address translation (P1, sequential allocation):** logical address `2500` → page 2, offset 452 → frame 2 → physical address **2500**.
Address `10500` → error (valid range 0–10499).

## 2. Segmentation Simulator

Segments: Code 1000, Data 500, Stack 300, Heap 700.

**S1 – memory 4096**

| Segment | Base | Limit | End |
|---|---|---|---|
| Code | 0 | 1000 | 999 |
| Data | 1000 | 500 | 1499 |
| Stack | 1500 | 300 | 1799 |
| Heap | 1800 | 700 | 2499 |

Used 2500, free 1596, utilisation 61.0%. Success: "All segments fit".

**S2 – memory 2000** (same segments): overflow of **500** bytes → red error. Heap (end 2499) shows "Exceeds memory"; Code, Data, Stack are within memory.

**Boundary checks (S1):**
- Stack, offset 299 → allowed, physical address 1799
- Stack, offset 300 → segmentation fault (offset ≥ limit 300)
- Heap, offset 0 → allowed, physical address 1800

## 3. Page Replacement (reference string and frames)

### R1 – Textbook string, 3 frames
`7 0 1 2 0 3 0 4 2 3 0 3 2 1 2 0 1 7 0 1`

| Algorithm | Faults | Hits | Hit ratio |
|---|---|---|---|
| FIFO | 15 | 5 | 25.0% |
| LRU | 12 | 8 | 40.0% |

**FIFO trace** (frames after each step; `-` = empty)

| Step | Page | Frames | Result | Evicted |
|---|---|---|---|---|
| 1 | 7 | 7 - - | FAULT | – |
| 2 | 0 | 7 0 - | FAULT | – |
| 3 | 1 | 7 0 1 | FAULT | – |
| 4 | 2 | 2 0 1 | FAULT | 7 |
| 5 | 0 | 2 0 1 | HIT | – |
| 6 | 3 | 2 3 1 | FAULT | 0 |
| 7 | 0 | 2 3 0 | FAULT | 1 |
| 8 | 4 | 4 3 0 | FAULT | 2 |
| 9 | 2 | 4 2 0 | FAULT | 3 |
| 10 | 3 | 4 2 3 | FAULT | 0 |
| 11 | 0 | 0 2 3 | FAULT | 4 |
| 12 | 3 | 0 2 3 | HIT | – |
| 13 | 2 | 0 2 3 | HIT | – |
| 14 | 1 | 0 1 3 | FAULT | 2 |
| 15 | 2 | 0 1 2 | FAULT | 3 |
| 16 | 0 | 0 1 2 | HIT | – |
| 17 | 1 | 0 1 2 | HIT | – |
| 18 | 7 | 7 1 2 | FAULT | 0 |
| 19 | 0 | 7 0 2 | FAULT | 1 |
| 20 | 1 | 7 0 1 | FAULT | 2 |

**LRU trace**

| Step | Page | Frames | Result | Evicted |
|---|---|---|---|---|
| 1 | 7 | 7 - - | FAULT | – |
| 2 | 0 | 7 0 - | FAULT | – |
| 3 | 1 | 7 0 1 | FAULT | – |
| 4 | 2 | 2 0 1 | FAULT | 7 |
| 5 | 0 | 2 0 1 | HIT | – |
| 6 | 3 | 2 0 3 | FAULT | 1 |
| 7 | 0 | 2 0 3 | HIT | – |
| 8 | 4 | 4 0 3 | FAULT | 2 |
| 9 | 2 | 4 0 2 | FAULT | 3 |
| 10 | 3 | 4 3 2 | FAULT | 0 |
| 11 | 0 | 0 3 2 | FAULT | 4 |
| 12 | 3 | 0 3 2 | HIT | – |
| 13 | 2 | 0 3 2 | HIT | – |
| 14 | 1 | 1 3 2 | FAULT | 0 |
| 15 | 2 | 1 3 2 | HIT | – |
| 16 | 0 | 1 0 2 | FAULT | 3 |
| 17 | 1 | 1 0 2 | HIT | – |
| 18 | 7 | 1 0 7 | FAULT | 2 |
| 19 | 0 | 1 0 7 | HIT | – |
| 20 | 1 | 1 0 7 | HIT | – |

*Why step 6 differs:* FIFO evicts page 0 (arrived first of the pages still in memory), but page 0 was just used at step 5, so LRU evicts page 1 instead.

### R2 – Belady's anomaly: `1 2 3 4 1 2 5 1 2 3 4 5`

| Frames | FIFO faults | LRU faults |
|---|---|---|
| 3 | 9 | 10 |
| 4 | **10** | 8 |

FIFO gets *worse* with more frames; LRU improves. (On this string with 3 frames FIFO happens to beat LRU, so the comparison page shows an orange "FIFO wins" message.)

### R3 – Strong locality: `1 2 1 3 1 2 1 4 1 2 1 3 1 2`, 3 frames
FIFO 7 faults (hit ratio 50.0%), LRU 5 faults (hit ratio 64.3%).

### R4 – Small hand-checkable example: `1 2 3 1 4`, 3 frames
- FIFO: steps → FAULT, FAULT, FAULT, HIT, FAULT; final frames `4 2 3` (page 1 evicted, it arrived first)
- LRU: final frames `1 4 3` (page 2 evicted, it was least recently used)

### R5 – Edge cases (any algorithm)
| Reference string | Frames | Faults |
|---|---|---|
| `5 5 5 5` | 1 | 1 |
| `1 2 3 4` | 1 | 4 |
| `1 2 3` | 10 | 3 (a warning says frames ≥ distinct pages) |
| `1 2 1 2` | 2 | 2 |

### R6 – Invalid input (all replacement pages)
| Input | Expected |
|---|---|
| *(empty)* | Error: enter at least one page number |
| `1 2 abc` | Error: 'abc' is not a valid page number |
| `1 -2 3` | Error: '-2' is not a valid page number |
| `1 1000` | Error: page numbers must be at most 999 |
| 201 numbers | Error: reference string too long |
