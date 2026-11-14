"""Unit tests for the core algorithms. Run from the project root with:

    python -m unittest discover -s tests -v
"""
import os
import random
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithms.paging import simulate_paging, translate_logical_address
from algorithms.segmentation import build_segment_table, translate_segment_address
from algorithms.page_replacement import fifo, lru, run_algorithm, faults_by_frame_count
from utils.validation import (parse_reference_string, validate_paging_inputs,
                              validate_frame_count, validate_segment_inputs)

TEXTBOOK = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]
BELADY = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]


class TestPaging(unittest.TestCase):
    def test_basic_numbers(self):
        r = simulate_paging(10500, 1024, 16384)
        self.assertEqual(r.total_pages, 11)
        self.assertEqual(r.total_frames, 16)
        self.assertEqual(r.internal_fragmentation, 764)   # 11*1024 - 10500
        self.assertTrue(r.fits)
        self.assertEqual(r.page_table[-1].bytes_used, 10500 - 10 * 1024)
        self.assertEqual(r.free_frames, 5)

    def test_exact_multiple_has_no_fragmentation(self):
        r = simulate_paging(4096, 1024, 8192)
        self.assertEqual(r.total_pages, 4)
        self.assertEqual(r.internal_fragmentation, 0)

    def test_process_too_large(self):
        r = simulate_paging(5000, 1000, 3000)
        self.assertFalse(r.fits)
        self.assertEqual(r.page_table, [])

    def test_scattered_uses_unique_frames(self):
        r = simulate_paging(8000, 1000, 20000, allocation="scattered", seed=1)
        frames = [e.frame for e in r.page_table]
        self.assertEqual(len(set(frames)), 8)
        self.assertTrue(all(0 <= f < 20 for f in frames))

    def test_leftover_memory(self):
        self.assertEqual(simulate_paging(100, 30, 100).leftover_memory, 10)

    def test_address_translation(self):
        r = simulate_paging(10500, 1024, 16384)
        t = translate_logical_address(2500, r)       # page 2, offset 452
        self.assertEqual((t.page, t.offset, t.frame), (2, 452, 2))
        self.assertEqual(t.physical_address, 2 * 1024 + 452)
        self.assertFalse(translate_logical_address(10500, r).valid)

    def test_invalid_args(self):
        with self.assertRaises(ValueError):
            simulate_paging(0, 1024, 4096)


class TestSegmentation(unittest.TestCase):
    SIZES = {"Code": 1000, "Data": 500, "Stack": 300, "Heap": 700}

    def test_bases_and_limits(self):
        r = build_segment_table(self.SIZES, 4096)
        self.assertEqual([s.base for s in r.segments], [0, 1000, 1500, 1800])
        self.assertEqual([s.limit for s in r.segments], [1000, 500, 300, 700])
        self.assertEqual([s.end for s in r.segments], [999, 1499, 1799, 2499])
        self.assertEqual((r.total_used, r.free), (2500, 1596))
        self.assertTrue(r.fits)

    def test_overflow_detected(self):
        r = build_segment_table(self.SIZES, 2000)
        self.assertFalse(r.fits)
        self.assertEqual(r.overflow, 500)
        self.assertTrue(r.within_memory(r.segments[0]))
        self.assertFalse(r.within_memory(r.segments[3]))

    def test_translation(self):
        r = build_segment_table(self.SIZES, 4096)
        ok = translate_segment_address(r, "Stack", 299)
        self.assertTrue(ok.valid)
        self.assertEqual(ok.physical_address, 1500 + 299)
        self.assertFalse(translate_segment_address(r, "Stack", 300).valid)
        self.assertFalse(translate_segment_address(r, "Data", -1).valid)


class TestPageReplacement(unittest.TestCase):
    def test_small_hand_trace_fifo(self):
        res = fifo([1, 2, 3, 1, 4], 3)
        self.assertEqual([s.hit for s in res.steps], [False, False, False, True, False])
        self.assertEqual(res.steps[-1].frames, (4, 2, 3))   # page 1 (oldest) evicted
        self.assertEqual(res.steps[-1].evicted, 1)

    def test_small_hand_trace_lru(self):
        res = lru([1, 2, 3, 1, 4], 3)
        self.assertEqual(res.steps[-1].frames, (1, 4, 3))   # page 2 (least recent) evicted
        self.assertEqual(res.steps[-1].evicted, 2)

    def test_textbook_fifo_3_frames(self):
        res = fifo(TEXTBOOK, 3)
        self.assertEqual((res.faults, res.hits), (15, 5))

    def test_textbook_lru_3_frames(self):
        res = lru(TEXTBOOK, 3)
        self.assertEqual((res.faults, res.hits), (12, 8))

    def test_beladys_anomaly_fifo(self):
        self.assertEqual(fifo(BELADY, 3).faults, 9)
        self.assertEqual(fifo(BELADY, 4).faults, 10)       # MORE frames, MORE faults

    def test_lru_belady_reference(self):
        self.assertEqual(lru(BELADY, 3).faults, 10)
        self.assertEqual(lru(BELADY, 4).faults, 8)

    def test_edge_cases(self):
        for fn in (fifo, lru):
            self.assertEqual(fn([5, 5, 5, 5], 1).faults, 1)       # repeated page
            self.assertEqual(fn([1, 2, 3, 4], 1).faults, 4)       # one frame
            self.assertEqual(fn([1, 2, 3], 10).faults, 3)         # frames > distinct pages
            self.assertEqual(fn([1, 2, 1, 2], 2).faults, 2)       # only compulsory faults

    def test_hits_plus_faults_equals_length(self):
        for fn in (fifo, lru):
            res = fn(TEXTBOOK, 4)
            self.assertEqual(res.hits + res.faults, len(TEXTBOOK))
            self.assertAlmostEqual(res.hit_ratio + res.fault_ratio, 1.0)

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            fifo([], 3)
        with self.assertRaises(ValueError):
            lru([1], 0)
        with self.assertRaises(ValueError):
            run_algorithm("OPT", [1], 1)

    def test_cross_check_with_independent_implementations(self):
        """Compare against deliberately simple, separate versions on random data."""
        def ref_fifo(refs, n):
            mem, faults = [], 0
            for p in refs:
                if p not in mem:
                    faults += 1
                    if len(mem) == n:
                        mem.pop(0)
                    mem.append(p)
            return faults

        def ref_lru(refs, n):
            mem, faults = [], 0          # mem[0] = least recently used
            for p in refs:
                if p in mem:
                    mem.remove(p)
                else:
                    faults += 1
                    if len(mem) == n:
                        mem.pop(0)
                mem.append(p)
            return faults

        rng = random.Random(2024)
        for _ in range(500):
            refs = [rng.randint(0, 9) for _ in range(rng.randint(1, 60))]
            n = rng.randint(1, 8)
            self.assertEqual(fifo(refs, n).faults, ref_fifo(refs, n))
            self.assertEqual(lru(refs, n).faults, ref_lru(refs, n))

    def test_frames_never_exceed_capacity_or_duplicate(self):
        res = lru(TEXTBOOK, 3)
        for s in res.steps:
            loaded = [p for p in s.frames if p is not None]
            self.assertEqual(len(loaded), len(set(loaded)))
            self.assertIn(s.page, loaded)                        # requested page is resident

    def test_sweep(self):
        sweep = faults_by_frame_count(BELADY, 5)
        self.assertEqual(sweep["FIFO"][2:4], [9, 10])
        self.assertEqual(sweep["LRU"][2:4], [10, 8])


class TestValidation(unittest.TestCase):
    def test_parse_ok(self):
        self.assertEqual(parse_reference_string("7, 0 1,2"), ([7, 0, 1, 2], []))

    def test_parse_errors(self):
        for bad in ("", "   ", "1 2 x", "1 -2", "1.5", "1000", "٣"):
            pages, errs = parse_reference_string(bad)
            self.assertIsNone(pages, bad)
            self.assertTrue(errs, bad)
        self.assertIsNone(parse_reference_string(" ".join(["1"] * 201))[0])

    def test_paging_validation(self):
        self.assertEqual(validate_paging_inputs(10500, 1024, 16384), [])
        self.assertTrue(validate_paging_inputs(0, 1024, 16384))
        self.assertTrue(validate_paging_inputs(100, 2048, 1024))
        self.assertTrue(validate_paging_inputs(10 ** 7, 1, 10 ** 7))

    def test_other_validation(self):
        self.assertEqual(validate_frame_count(3), [])
        self.assertTrue(validate_frame_count(0))
        self.assertTrue(validate_frame_count(31))
        self.assertTrue(validate_segment_inputs({"Code": 0}, 100))


if __name__ == "__main__":
    unittest.main()
