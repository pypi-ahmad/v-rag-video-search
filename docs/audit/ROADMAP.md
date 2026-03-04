# V-RAG — Phased Upgrade Roadmap

> Each PR is an independent, shippable unit. Ordered by risk (safe first) and value.

---

## PR 1 — Housekeeping & Lint ✅ DONE

**Issues:** #14, #15, #16, #17, #18

| Task | Status |
|---|---|
| Add `src/__init__.py` | ✅ |
| Remove unused imports (`Union`, `os`) + dead variables | ✅ |
| Delete commented-out code in `app.py` | ✅ |
| Fix 5-space indent in `main.py` | ✅ |
| Update README author + repo URL | ✅ |

---

## PR 2 — P0 Security + Correctness ✅ DONE

**Issues:** #1, #2, #3, #4

| Task | Status |
|---|---|
| Sanitize uploaded filename (`app.py:L67`) | ✅ |
| Fix DB path to `__file__`-relative (`vector_db.py:L11,L21`) | ✅ |
| `collection.add()` → `collection.upsert()` (`vector_db.py:L50`) | ✅ |
| Fix embedding/metadata alignment (`embedder.py:L31–L87`, `app.py:L112–L118`) | ✅ |
| Empty-embeddings guard + `ValueError` in `add_frames()` (`vector_db.py:L34–L41`) | ✅ |

---

## PR 3 — Resource Cleanup + Deprecation ✅ DONE

**Issues:** #5, #9

| Task | Status |
|---|---|
| Delete uploaded video in `try/finally` (`app.py:L145–L148`) | ✅ |
| Delete `temp_query.jpg` in `try/finally` (`app.py:L190–L193`) | ✅ |
| `use_container_width=True` (`app.py:L224`) | ✅ |

---

## PR 4 — Structured Logging ✅ DONE

**Issues:** #10

| Task | Status |
|---|---|
| Replace all `print()` with `logging` in `embedder.py`, `video_processor.py`, `main.py` | ✅ |
| `logging.basicConfig()` in `app.py:L11` and `main.py:L8` | ✅ |
| `logger = logging.getLogger(__name__)` per module | ✅ |

---

## PR 5 — Stable Paths ✅ DONE

**Issues:** #11

| Task | Status |
|---|---|
| `temp_uploads/` path anchored to `__file__` (`app.py:L60–L62`) | ✅ |
| `temp_query.jpg` path anchored to `__file__` (`app.py:L182`) | ✅ |

---

## PR 6 — Pin Dependencies

**Issues:** #6

| Task | Effort | Status |
|---|---|---|
| `pip freeze > requirements.txt` or use `pip-tools` | S | **Open** |
| Optionally add `requirements-dev.txt` for test deps | S | **Open** |

---

## PR 7 — Config Externalization

**Issues:** #13

| Task | Effort | Status |
|---|---|---|
| Extract magic numbers to `src/config.py` | M | **Open** |
| Read from env vars with defaults | S | **Open** |

---

## PR 8 — Add Tests + CI

**Issues:** #7

| Task | Effort | Status |
|---|---|---|
| `tests/test_embedder.py` (encode_text shape, encode_images roundtrip) | M | **Open** |
| `tests/test_vector_db.py` (add_frames + search roundtrip) | M | **Open** |
| `tests/test_video_processor.py` (extract from synthetic video) | M | **Open** |
| `tests/test_app.py` (smoke: format_timestamp, interpret_score) | S | **Open** |
| `.github/workflows/ci.yml` (lint, compile, import check) | M | **Open** |

---

## PR 9 — Delete Dead Code

**Issues:** #12

| Task | Effort | Status |
|---|---|---|
| Delete `main.py` or move to `scripts/dev_test.py` | S | **Open** |

---

## Timeline

| PR | Priority | Status |
|---|---|---|
| PR 1 Housekeeping | P2 | ✅ Done |
| PR 2 P0 Fixes | P0 | ✅ Done |
| PR 3 Cleanup | P1 | ✅ Done |
| PR 4 Logging | P1 | ✅ Done |
| PR 5 Stable Paths | P1 | ✅ Done |
| PR 6 Pin Deps | P1 | Open |
| PR 7 Config | P2 | Open |
| PR 8 Tests + CI | P1 | Open |
| PR 9 Dead Code | P2 | Open |
