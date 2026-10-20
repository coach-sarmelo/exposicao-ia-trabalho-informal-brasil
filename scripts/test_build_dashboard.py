#!/usr/bin/env python3
"""Unit tests for scripts/build_dashboard.py."""
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

import build_dashboard


class TestBuildDashboard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data_dir = build_dashboard.resolve_data_dir()
        cls.repo_root = build_dashboard.REPO_ROOT
        cls.html_path = build_dashboard.DEFAULT_HTML_PATH

    def test_load_reference_data(self):
        uf_codes, scores = build_dashboard.load_reference_data(self.data_dir)
        self.assertIsInstance(uf_codes, dict)
        self.assertIsInstance(scores, dict)
        self.assertEqual(len(uf_codes), 27)
        self.assertGreater(len(scores), 100)

    def test_load_reference_data_missing_raises(self):
        with self.assertRaises(FileNotFoundError):
            build_dashboard.load_reference_data("nonexistent_dir")

    def test_build_geo_metadata(self):
        uf_codes, _ = build_dashboard.load_reference_data(self.data_dir)
        ufs, regions, uf_region = build_dashboard.build_geo_metadata(uf_codes)
        self.assertEqual(len(ufs), 27)
        self.assertEqual(len(regions), 5)
        self.assertEqual(len(uf_region), 27)
        self.assertTrue(all(0 <= r < 5 for r in uf_region))

    def test_build_occupation_metadata(self):
        csv_path = Path(self.data_dir) / "analysis" / "individual_microdata.csv"
        _, scores = build_dashboard.load_reference_data(self.data_dir)
        occs, occ_map, no_score_occs, row_count = build_dashboard.build_occupation_metadata(csv_path, scores)

        self.assertEqual(row_count, 228325)
        self.assertEqual(len(occs), 127)
        self.assertEqual(len(occ_map), 127)
        self.assertEqual(no_score_occs, ["11", "21", "212", "223", "224"])

    def test_build_dash_data_structure(self):
        dash_data = build_dashboard.build_dash_data(self.data_dir)
        self.assertEqual(dash_data["n"], 228325)
        self.assertEqual(len(dash_data["ufs"]), 27)
        self.assertEqual(len(dash_data["regions"]), 5)
        self.assertEqual(len(dash_data["occs"]), 127)
        self.assertEqual(dash_data["sexLabels"], ["Homem", "Mulher"])
        self.assertEqual(dash_data["formLabels"], ["Formal", "Informal"])

        b64 = dash_data["b64"]
        for col in ["uf", "occ", "inc", "w", "demo", "age", "edu"]:
            self.assertIn(col, b64)
            self.assertIsInstance(b64[col], str)
            self.assertGreater(len(b64[col]), 0)

        meta = dash_data["meta"]
        self.assertEqual(meta["quarter"], "2026Q1")
        self.assertEqual(meta["noScoreRows"], 696)
        self.assertEqual(meta["zeroIncomeRows"], 4595)
        self.assertEqual(meta["minCellN"], 30)
        self.assertEqual(meta["scatterTarget"], 4000)

    def test_embed_dash_data_update_and_generate(self):
        temp_dir = tempfile.mkdtemp()
        try:
            # Test generate into clean HTML
            html_no_data = Path(temp_dir) / "test_no_data.html"
            html_no_data.write_text("<!DOCTYPE html><html><head><title>Test</title></head><body><!-- DASH_DATA --></body></html>", encoding="utf-8")

            dummy_data = {"n": 10, "test": True}
            bytes_written = build_dashboard.embed_dash_data_in_html(html_no_data, dummy_data)
            self.assertGreater(bytes_written, 0)
            content = html_no_data.read_text(encoding="utf-8")
            self.assertIn("<script>window.DASH_DATA = {\"n\":10,\"test\":true};</script>", content)

            # Test update existing
            dummy_data_v2 = {"n": 20, "test": False}
            build_dashboard.embed_dash_data_in_html(html_no_data, dummy_data_v2)
            content_v2 = html_no_data.read_text(encoding="utf-8")
            self.assertIn("<script>window.DASH_DATA = {\"n\":20,\"test\":false};</script>", content_v2)
            self.assertNotIn("\"n\":10", content_v2)
        finally:
            shutil.rmtree(temp_dir)

    def test_cli_check_and_dry_run(self):
        ret_check = build_dashboard.main(["--check"])
        self.assertEqual(ret_check, 0)

        ret_dry = build_dashboard.main(["--dry-run"])
        self.assertEqual(ret_dry, 0)

    def test_cli_json_out(self):
        temp_dir = tempfile.mkdtemp()
        json_file = Path(temp_dir) / "out.json"
        try:
            ret = build_dashboard.main(["--dry-run", "--json-out", str(json_file)])
            self.assertEqual(ret, 0)
            self.assertTrue(json_file.is_file())
            data = json.loads(json_file.read_text(encoding="utf-8"))
            self.assertEqual(data["n"], 228325)
        finally:
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    unittest.main()
