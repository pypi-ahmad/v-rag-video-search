"""Smoke tests for V-RAG modules.

These tests verify imports, helper functions, and basic module contracts
without requiring GPU, large models, or video files.
"""

import importlib
import math

import pytest


# ── Import tests ────────────────────────────────────────


class TestImports:
    """Verify that all project modules can be imported."""

    @pytest.mark.parametrize(
        "module",
        [
            "src",
            "src.embedder",
            "src.vector_db",
            "src.video_processor",
        ],
    )
    def test_import_module(self, module: str):
        importlib.import_module(module)


# ── Helper function tests (app.py) ─────────────────────


class TestFormatTimestamp:
    """Test the format_timestamp helper from app.py."""

    @staticmethod
    def _fn(seconds: float) -> str:
        """Inline replica — avoids importing Streamlit at test time."""
        return f"{int(seconds // 60):02d}m {int(seconds % 60):02d}s"

    def test_zero(self):
        assert self._fn(0) == "00m 00s"

    def test_sub_minute(self):
        assert self._fn(45) == "00m 45s"

    def test_exact_minute(self):
        assert self._fn(60) == "01m 00s"

    def test_multi_minute(self):
        assert self._fn(125) == "02m 05s"


class TestInterpretScore:
    """Test the interpret_score helper from app.py."""

    @staticmethod
    def _fn(score: float):
        if score < 135:
            return "🔥 High Confidence", "green"
        elif score < 145:
            return "✅ Medium Confidence", "orange"
        else:
            return "⚠️ Low Confidence", "red"

    def test_high_confidence(self):
        label, color = self._fn(100)
        assert color == "green"

    def test_medium_confidence(self):
        label, color = self._fn(140)
        assert color == "orange"

    def test_low_confidence(self):
        label, color = self._fn(200)
        assert color == "red"

    def test_boundary_135(self):
        _, color = self._fn(135)
        assert color == "orange"

    def test_boundary_145(self):
        _, color = self._fn(145)
        assert color == "red"


# ── VideoProcessor contract ─────────────────────────────


class TestVideoProcessor:
    """Basic contract tests for VideoProcessor (no real video needed)."""

    def test_init(self):
        from src.video_processor import VideoProcessor

        vp = VideoProcessor()
        assert vp is not None

    def test_missing_file_raises(self):
        from src.video_processor import VideoProcessor

        vp = VideoProcessor()
        with pytest.raises(FileNotFoundError):
            vp.extract_frames("nonexistent_video.mp4", "/tmp/frames")


# ── VectorDB contract ──────────────────────────────────


class TestVideoSearchDB:
    """Basic contract tests for VideoSearchDB."""

    def test_init(self, tmp_path, monkeypatch):
        """DB should initialize without error when given a temp path."""
        import src.vector_db as vdb_mod

        # Patch _PROJECT_ROOT so DB is created in tmp_path
        monkeypatch.setattr(vdb_mod, "_PROJECT_ROOT", tmp_path)

        from src.vector_db import VideoSearchDB

        db = VideoSearchDB()
        assert db.collection is not None

    def test_add_frames_empty(self, tmp_path, monkeypatch):
        """add_frames with 0 embeddings should no-op."""
        import numpy as np
        import src.vector_db as vdb_mod

        monkeypatch.setattr(vdb_mod, "_PROJECT_ROOT", tmp_path)

        from src.vector_db import VideoSearchDB

        db = VideoSearchDB()
        db.add_frames(np.empty((0, 512), dtype=np.float32), [])  # no error

    def test_add_frames_mismatch_raises(self, tmp_path, monkeypatch):
        """add_frames should raise ValueError on length mismatch."""
        import numpy as np
        import src.vector_db as vdb_mod

        monkeypatch.setattr(vdb_mod, "_PROJECT_ROOT", tmp_path)

        from src.vector_db import VideoSearchDB

        db = VideoSearchDB()
        emb = np.random.rand(3, 512).astype(np.float32)
        meta = [{"frame_path": "a.jpg", "timestamp": 0.0}]  # only 1
        with pytest.raises(ValueError):
            db.add_frames(emb, meta)

    def test_roundtrip(self, tmp_path, monkeypatch):
        """add_frames + search should return stored results."""
        import numpy as np
        import src.vector_db as vdb_mod

        monkeypatch.setattr(vdb_mod, "_PROJECT_ROOT", tmp_path)

        from src.vector_db import VideoSearchDB

        db = VideoSearchDB()
        emb = np.random.rand(2, 512).astype(np.float32)
        meta = [
            {"frame_path": "frame_0.jpg", "timestamp": 0.0},
            {"frame_path": "frame_1.jpg", "timestamp": 1.0},
        ]
        db.add_frames(emb, meta)

        results = db.search(emb[0], k=2)
        assert len(results) == 2
        assert "path" in results[0]
        assert "timestamp" in results[0]
        assert "score" in results[0]
