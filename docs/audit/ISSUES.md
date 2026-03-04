# V-RAG — Issues Register

> Every finding has a file:line citation. "Effort" is T-shirt sized: **S** (<1h), **M** (1–4h), **L** (4h+).

---

## P0 — Critical (fix before any release)

| # | Severity | File:Line | Category | Status | Symptom | Fix | Effort |
|---|---|---|---|---|---|---|---|
| 1 | **P0** | `src/embedder.py:L32–L85` | **Correctness** | ✅ **FIXED** (PR2) | When a single image fails to load, it is silently skipped. The returned embedding array has fewer rows than the metadata list passed to `add_frames()`. | `encode_images()` now returns `Tuple[np.ndarray, List[str]]` — `embedder.py:L32–L33`. Callers rebuild metadata with order-preserving dict lookup — `app.py:L111–L113`, `main.py:L70–L72`. Empty return is `np.empty((0, 512), dtype=np.float32)` — `embedder.py:L84`. `add_frames()` raises `ValueError` on mismatch — `vector_db.py:L38–L41`. | **M** |
| 2 | **P0** | `app.py:L65` | **Security** | ✅ **FIXED** (PR2) | `uploaded_file.name` was used directly in `os.path.join("temp_uploads", ...)`. | Sanitized with `pathlib.Path(uploaded_file.name).name` — `app.py:L65`. | **S** |
| 3 | **P0** | `src/vector_db.py:L14,L22` | **Reliability** | ✅ **FIXED** (PR2) | DB path was `os.path.join(os.getcwd(), "video_db_storage")`. | Now uses `pathlib.Path(__file__).resolve().parent.parent / "video_db_storage"` — `vector_db.py:L14,L22`. | **S** |

---

## P1 — Important (fix in next sprint)

| # | Severity | File:Line | Category | Status | Symptom | Fix | Effort |
|---|---|---|---|---|---|---|---|
| 4 | **P1** | `src/vector_db.py:L52` | **Correctness** | ✅ **FIXED** (PR2) | `collection.add()` will error on duplicate IDs in newer ChromaDB (≥0.4). | Changed to `collection.upsert()` — `vector_db.py:L52`. | **S** |
| 5 | **P1** | `app.py:L155–L160`, `app.py:L199–L206` | **Resource Leak** | ✅ **FIXED** (PR2+PR3) | `temp_uploads/` accumulated every uploaded video forever. `temp_query.jpg` was written at CWD root and never deleted. | Uploaded video is deleted in `try/finally` — `app.py:L155–L160`. `temp_query.jpg` is deleted in `try/finally` — `app.py:L199–L206`. | **S** |
| 6 | **P1** | `requirements.txt:L1–L9` | **Reliability** | Open | Zero version pins. A fresh install may pull incompatible versions (especially `chromadb`, `sentence-transformers`, `torch`). | Pin versions: `pip freeze > requirements.txt` or use a lockfile (`pip-tools`, `poetry`). | **S** |
| 7 | **P1** | *(entire repo)* | **Quality** | Open | No tests, no CI, no lint config. Any regression is invisible until runtime. | Add `pytest`, a basic `tests/` folder, and a GitHub Actions workflow (see ROADMAP). | **L** |
| 8 | **P1** | `app.py:L76–L92` | **Performance** | Open | Frame extraction and CLIP embedding run synchronously in the Streamlit main thread, blocking the UI for minutes on long videos. | Use `st.status()` with a background thread, or offload to a Celery/RQ worker. Short-term: add Streamlit progress updates per batch (already partially done). | **L** |
| 9 | **P1** | `app.py:L224` | **Deprecation** | ✅ **FIXED** (PR3) | `st.image(res['path'], width='stretch')` — deprecated parameter. | Replaced with `use_container_width=True` — `app.py:L224`. | **S** |
| 10 | **P1** | `main.py:L92` | **Style** | ✅ **FIXED** (PR1) | Indentation was 5 spaces instead of 4. | Re-indented to 4 spaces — `main.py:L92`. | **S** |

---

## P2 — Improvement (backlog)

| # | Severity | File:Line | Category | Status | Symptom | Fix | Effort |
|---|---|---|---|---|---|---|---|
| 11 | **P2** | `main.py` (entire file) | **Dead Code** | Open | CLI scaffold fully duplicates `app.py` pipeline. Not imported by anyone. Hardcoded query `"traffic congestion"`. | Delete or move to `scripts/dev_test.py`. | **S** |
| 12 | **P2** | `src/*.py`, `app.py`, `main.py` | **Observability** | Partial | Was all `print()`. Now `app.py`, `embedder.py`, and `vector_db.py` use the `logging` module — `app.py:L11`, `embedder.py:L9`, `vector_db.py:L8`. `video_processor.py` and `main.py` still use `print()`. | Replace remaining `print()` calls with `logging`. | **S** |
| 13 | **P2** | `src/__init__.py` | **Packaging** | ✅ **FIXED** (PR1) | `src/` had no `__init__.py`. | Added empty `src/__init__.py`. | **S** |
| 14 | **P2** | *(removed)* | **Dead Code** | ✅ **FIXED** (PR1) | Commented-out lines (DB reset, image display) in `app.py`. | Deleted the comments. | **S** |
| 15 | **P2** | `app.py:L52–L54` | **Maintainability** | Open | Magic numbers `135`, `145` for score confidence thresholds with no documentation of how they were derived. | Extract to named constants or a config file. | **S** |
| 16 | **P2** | `README.md:L110` | **Docs** | ✅ **FIXED** (PR1) | Placeholder author `[Your Name]`. | Updated to `Ahmad Mujtaba` — `README.md:L110`. Repo URL was already correct. | **S** |
| 17 | **P2** | *(removed)* | **Unused Import** | ✅ **FIXED** (PR2) | `Union` was imported in `embedder.py` but never used. | Removed. Current imports: `List, Tuple` — `embedder.py:L5`. | **S** |
| 18 | **P2** | *(removed)* | **Unused Import** | ✅ **FIXED** (PR2) | `os` was imported in `embedder.py` but never used. | Removed. | **S** |
| 19 | **P2** | *(removed)* | **Dead Code** | ✅ **FIXED** (PR2) | `total_batches` was computed but never referenced in `embedder.py`. | Removed. | **S** |
| 20 | **P2** | *(removed)* | **Dead Variable** | ✅ **FIXED** (PR1) | `saved_count` was incremented but never read in `video_processor.py`. | Removed — `video_processor.py:L49`. | **S** |
