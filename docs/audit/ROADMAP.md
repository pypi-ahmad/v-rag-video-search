# V-RAG — Phased Upgrade Roadmap

> Each "PR" is an independent, shippable unit of work that can be reviewed and merged on its own. Ordered by risk (safe first) and value.

---

## PR 1 — Housekeeping & Lint (zero risk) ✅ DONE

**Issues addressed:** #13, #14, #16, #17, #18, #19, #20, #10

| Task | File(s) | Status |
|---|---|---|
| Add `src/__init__.py` (empty) | `src/__init__.py` | ✅ Done |
| Remove unused imports (`Union`, `os`) from `embedder.py` | `src/embedder.py` | ✅ Done (PR2) |
| Remove dead `total_batches` variable | `src/embedder.py` | ✅ Done (PR2) |
| Remove dead `saved_count` variable | `src/video_processor.py:L49` | ✅ Done |
| Delete commented-out code | `app.py` | ✅ Done |
| Fix 5-space indentation | `main.py:L92` | ✅ Done |
| Update README author + URL | `README.md:L110` | ✅ Done |

**Committed as:** `"Housekeeping: lint, dead code cleanup, README fixes"`

---

## PR 2 — P0 Security + Correctness Fixes ✅ DONE

**Issues addressed:** #1, #2, #3, #4

| Task | File(s) | Status |
|---|---|---|
| Sanitize uploaded filename | `app.py:L65` | ✅ Done |
| Fix DB path from `os.getcwd()` to `__file__`-relative | `src/vector_db.py:L14,L22` | ✅ Done |
| Change `collection.add()` → `collection.upsert()` | `src/vector_db.py:L52` | ✅ Done |
| Fix embedding/metadata alignment: return valid paths from `encode_images()` | `src/embedder.py:L32–L85`, `app.py:L108–L113`, `main.py:L68–L72` | ✅ Done |
| Empty-embeddings guard in `add_frames()` | `src/vector_db.py:L34–L36` | ✅ Done |
| `ValueError` on length mismatch in `add_frames()` | `src/vector_db.py:L38–L41` | ✅ Done |

**Committed as:** `"Fix P0 upload safety, DB path stability, and embedding alignment"`

---

## PR 3 — Resource Cleanup + Deprecation Fix ✅ DONE

**Issues addressed:** #5, #9

| Task | File(s) | Status |
|---|---|---|
| Delete uploaded video after pipeline completes | `app.py:L155–L160` | ✅ Done |
| Delete `temp_query.jpg` after image search | `app.py:L199–L206` | ✅ Done |
| Replace `width='stretch'` → `use_container_width=True` | `app.py:L224` | ✅ Done |

**Committed as:** `"Cleanup temp files and fix Streamlit image param"`

---

## PR 4 — Pin Dependencies

**Issues addressed:** #6

| Task | File(s) | Effort |
|---|---|---|
| Run `pip freeze` and pin all versions in `requirements.txt` | `requirements.txt` | S |
| Optionally add `requirements-dev.txt` for test deps | `requirements-dev.txt` (new) | S |

**Estimated effort:** 15 minutes  
**Risk:** Zero

---

## PR 5 — Structured Logging

**Issues addressed:** #12

| Task | File(s) | Effort |
|---|---|---|
| Replace all `print()` with `logging.info/warning/error` | All `.py` files | M |
| Add `logging.basicConfig(level=…, format=…)` in `app.py` and `main.py` | `app.py:L1`, `main.py:L1` | S |
| Use `logger = logging.getLogger(__name__)` per module | `src/embedder.py`, `src/vector_db.py`, `src/video_processor.py` | S |

**Estimated effort:** 1–2 hours  
**Risk:** Low — changes output from stdout to stderr (logging default)

---

## PR 6 — Config Externalization

**Issues addressed:** #15

| Task | File(s) | Effort |
|---|---|---|
| Create `config.py` with all constants | `src/config.py` (new) | S |
| Extract: `FRAME_INTERVAL`, `RESIZE_HEIGHT`, `BATCH_SIZE_GPU`, `BATCH_SIZE_CPU`, `SCORE_HIGH`, `SCORE_MED`, `DEFAULT_THRESHOLD`, `DB_PATH`, `COLLECTION_NAME` | `app.py`, `src/*.py` | M |
| Optionally read from env vars with defaults | `src/config.py` | S |

**Estimated effort:** 1–2 hours  
**Risk:** Low — replaces magic numbers with named imports

---

## PR 7 — Add Tests + CI

**Issues addressed:** #7

| Task | File(s) | Effort |
|---|---|---|
| Add `pytest` + `pytest-cov` to `requirements-dev.txt` | `requirements-dev.txt` | S |
| `tests/test_video_processor.py`: extract frames from a 3-second synthetic video | `tests/` (new) | M |
| `tests/test_embedder.py`: `encode_text()` returns (512,), `encode_images()` with 1 JPEG returns (1, 512) | `tests/` (new) | M |
| `tests/test_vector_db.py`: roundtrip `add_frames()` + `search()` on temp collection | `tests/` (new) | M |
| `tests/test_app.py`: smoke test `format_timestamp`, `interpret_score` | `tests/` (new) | S |
| `.github/workflows/ci.yml`: install deps, run `pytest`, lint with `ruff` | `.github/workflows/` (new) | M |

**Estimated effort:** 4–6 hours  
**Risk:** Zero to existing code — additive only

---

## PR 8 — Delete Dead Code

**Issues addressed:** #11

| Task | File(s) | Effort |
|---|---|---|
| Delete `main.py` or move to `scripts/dev_test.py` | `main.py` | S |
| Update README to remove `main.py` CLI mention | `README.md` | S |

**Estimated effort:** 15 minutes  
**Risk:** Low — must confirm nothing imports it (confirmed: nothing does)

---

## Timeline Summary

| PR | Contents | Priority | Status | Depends On |
|---|---|---|---|---|
| PR 1 | Housekeeping | P2 | ✅ **Done** | — |
| PR 2 | P0 security + correctness | P0 | ✅ **Done** | — |
| PR 3 | Temp file cleanup | P1 | ✅ **Done** | — |
| PR 4 | Pin deps | P1 | Open | — |
| PR 5 | Logging | P2 | Partial (app.py, embedder, vector_db done) | — |
| PR 6 | Config system | P2 | Open | — |
| PR 7 | Tests + CI | P1 | Open | PR 2 ✅ |
| PR 8 | Remove dead code | P2 | Open | PR 7 |

**Recommended merge order:** PR 1 → PR 2 → PR 3 → PR 4 → PR 5 → PR 6 → PR 7 → PR 8
