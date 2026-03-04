# V-RAG — Issues Register

> Every finding has a `file:line` citation. Effort: **S** (<1h), **M** (1–4h), **L** (4h+).

---

## P0 — Critical

| # | File:Line | Category | Status | Symptom | Fix | Effort |
|---|---|---|---|---|---|---|
| 1 | `src/embedder.py:L31–L87` | Correctness | ✅ **FIXED** | `encode_images()` silently skipped bad images → embedding array shorter than metadata. | Returns `Tuple[np.ndarray, List[str]]`. Callers rebuild metadata via `meta_by_path` dict (`app.py:L112–L118`, `main.py:L76–L80`). `add_frames()` raises `ValueError` on mismatch (`vector_db.py:L38–L41`). | M |
| 2 | `app.py:L67` | Security | ✅ **FIXED** | `uploaded_file.name` used unsanitized in file path. | `pathlib.Path(uploaded_file.name).name` strips directory components. | S |
| 3 | `src/vector_db.py:L11,L21` | Reliability | ✅ **FIXED** | DB path was `os.path.join(os.getcwd(), …)` — CWD-dependent. | Now `pathlib.Path(__file__).resolve().parent.parent / "video_db_storage"`. | S |

---

## P1 — Important

| # | File:Line | Category | Status | Symptom | Fix | Effort |
|---|---|---|---|---|---|---|
| 4 | `src/vector_db.py:L50` | Correctness | ✅ **FIXED** | `collection.add()` errors on duplicate IDs in ChromaDB ≥0.4. | Changed to `collection.upsert()`. | S |
| 5 | `app.py:L145–L148`, `app.py:L190–L193` | Resource Leak | ✅ **FIXED** | Temp uploads and query images accumulated indefinitely. | `try/finally` with `os.remove()`. | S |
| 6 | `requirements.txt:L1–L9` | Reliability | **Open** | Zero version pins; fresh install may pull incompatible versions. | Run `pip freeze > requirements.txt` or use `pip-tools`. | S |
| 7 | *(entire repo)* | Quality | **Open** | No tests, no CI, no lint config. | Add `pytest`, `tests/`, GitHub Actions workflow. | L |
| 8 | `app.py:L75–L128` | Performance | **Open** | Frame extraction + CLIP embedding run synchronously, blocking Streamlit. | Background thread or async worker. | L |
| 9 | `app.py:L224` | Deprecation | ✅ **FIXED** | `st.image(width='stretch')` deprecated. | `use_container_width=True`. | S |
| 10 | `embedder.py:L19–L27`, `video_processor.py:L87`, `main.py` | Observability | ✅ **FIXED** | `print()` used instead of `logging` throughout. | All modules now use `logger = logging.getLogger(__name__)`. | S |
| 11 | `app.py:L60–L62`, `app.py:L182` | Reliability | ✅ **FIXED** | `temp_uploads/` and `temp_query.jpg` were CWD-relative. | Now `__file__`-relative via `os.path.dirname(os.path.abspath(__file__))`. | S |

---

## P2 — Improvement

| # | File:Line | Category | Status | Symptom | Fix | Effort |
|---|---|---|---|---|---|---|
| 12 | `main.py` (entire) | Dead Code | **Open** | CLI scaffold duplicates `app.py` pipeline; hardcoded query. | Delete or move to `scripts/`. | S |
| 13 | `app.py:L52–L54` | Maintainability | **Open** | Magic numbers `135`, `145` for score thresholds. | Extract to named constants or config. | S |
| 14 | `src/__init__.py` | Packaging | ✅ **FIXED** | `src/` had no `__init__.py`. | Added empty file. | S |
| 15 | Removed | Dead Code | ✅ **FIXED** | Commented-out code in `app.py`. | Deleted. | S |
| 16 | `README.md` | Docs | ✅ **FIXED** | Placeholder author, no Mermaid diagrams. | Professional README with architecture diagrams. | S |
| 17 | Removed | Unused Import | ✅ **FIXED** | `Union`, `os` imported but not used in `embedder.py`. | Removed. | S |
| 18 | Removed | Dead Variable | ✅ **FIXED** | `saved_count` incremented but never read in `video_processor.py`. | Removed. | S |
