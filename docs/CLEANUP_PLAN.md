# V-RAG: Legacy / Cleanup Report & Refactor Roadmap

---

## 1. Legacy & Dead Code Inventory

| Candidate | Why Legacy/Dead | Evidence | Status |
|---|---|---|---|
| `main.py` | CLI scaffold from dev phase; fully duplicates pipeline in `app.py`; not imported by anything; hardcoded search query | `main.py:L1–L96`, `main.py:L88` | Open — still present |
| `src/__pycache__/` | Python bytecache; should be in `.gitignore`; committed to repo accidentally | `src/__pycache__/embedder.cpython-313.pyc` etc. | Open — should `git rm --cached` |
| ~~Commented-out DB reset code~~ | ~~Dead comment lines~~ | — | ✅ **FIXED** (PR1) — deleted |
| ~~Commented-out query image display~~ | ~~`# st.image(img_file_buffer, ...)`~~ | — | ✅ **FIXED** (PR1) — deleted |
| ~~`temp_uploads/` never cleaned up~~ | ~~Stale uploaded videos~~ | `app.py:L155–160` | ✅ **FIXED** (PR2) — deleted in `try/finally` |
| ~~`temp_query.jpg` never deleted~~ | ~~Stale file after camera search~~ | `app.py:L199–206` | ✅ **FIXED** (PR2) — deleted in `try/finally` |
| ~~`README.md` placeholder~~ | ~~Author says "Your Name"~~ | `README.md:L110` | ✅ **FIXED** (PR1) — set to Ahmad Mujtaba |

---

## 2. Bug / Risk Fixes (High Priority)

These are not dead code, but code quality risks that were identified in the initial audit.

### Fix 1: Embedding/Metadata Index Mismatch ✅ DONE (PR2)

**Problem:** When `encode_images()` silently skipped a failed image, the returned embeddings array had fewer entries than the metadata list.

**Resolution:** `encode_images()` now returns `Tuple[np.ndarray, List[str]]` — `embedder.py:L32–33`. Callers rebuild metadata with an order-preserving `meta_by_path` dict — `app.py:L111–113`, `main.py:L70–72`. `add_frames()` raises `ValueError` on mismatch — `vector_db.py:L38–41`.

---

### Fix 2: CWD-Relative DB Path ✅ DONE (PR2)

**Problem:** `os.getcwd()` in `VideoSearchDB.__init__()` made the DB path dependent on the working directory at startup.

**Resolution:** Now uses `pathlib.Path(__file__).resolve().parent.parent / "video_db_storage"` — `vector_db.py:L14,L22`.

---

### Fix 3: Path Traversal in File Upload ✅ DONE (PR2)

**Problem:** `uploaded_file.name` was used directly in `os.path.join()` without sanitization.

**Resolution:** Sanitized with `pathlib.Path(uploaded_file.name).name` — `app.py:L65`.

---

## 3. Refactor Roadmap

Staged as separate PRs for safe incremental improvement.

### PR 1 — Housekeeping (Zero Risk) ✅ DONE

- [x] Add `.gitignore` with `__pycache__/`, `*.pyc`, `*.pyo`, `temp_uploads/`, `temp_query.jpg`, `video_db_storage/`, `.venv/`
- [x] Run `git rm -r --cached src/__pycache__/` to remove bytecache from git history
- [x] Delete commented-out lines in `app.py`
- [x] Update `README.md` author name and repo URL
- [x] Add `src/__init__.py`
- [x] Remove dead variables and unused imports in `embedder.py` and `video_processor.py`
- [x] Fix 5-space indentation in `main.py`

**Committed as:** `"Housekeeping: lint, dead code cleanup, README fixes"`

---

### PR 2 — Bug Fixes (Low Risk) ✅ DONE

- [x] Fix path traversal: sanitize `uploaded_file.name` with `pathlib.Path(...).name` — `app.py:L65`
- [x] Fix `temp_query.jpg` leak: delete after use in `perform_search()` — `app.py:L199–206`
- [x] Add temp uploads cleanup: delete video after pipeline — `app.py:L155–160`
- [x] Fix CWD-relative DB path: use `pathlib.Path(__file__).parent.parent` — `vector_db.py:L14,L22`
- [x] Change `collection.add()` → `collection.upsert()` — `vector_db.py:L52`
- [x] Fix embedding/metadata alignment: return `(embeddings, valid_paths)` from `encode_images()` — `embedder.py:L32–85`

**Committed as:** `"Fix P0 upload safety, DB path stability, and embedding alignment"`

---

### PR 3 — Fix Embedding/Metadata Alignment (Medium) ✅ DONE (merged into PR2)

- [x] Refactor `encode_images()` to return `(embeddings, valid_paths)` tuple
- [x] Update `app.py:process_video_pipeline()` to filter metadata with order-preserving dict
- [x] Update `main.py` with same pattern

---

### PR 4 — Remove Dead Code (Low Risk)

- [ ] Delete `main.py` (or convert to proper `tests/` or `scripts/` module)
- [ ] Confirm nothing depends on it (it is not imported anywhere — verified)

**Risk:** Low

---

### PR 5 — Add Tests (No Risk to Existing Code)

- [ ] Add `pytest` to `requirements.txt` (or `requirements-dev.txt`)
- [ ] `tests/test_video_processor.py`: test `extract_frames()` with a small synthetic video
- [ ] `tests/test_embedder.py`: test `encode_text()` returns shape `(512,)`, test `encode_images()` with a single test JPEG
- [ ] `tests/test_vector_db.py`: test `add_frames()` + `search()` roundtrip in a temp collection

**Risk:** Zero to existing functionality

---

### PR 6 — Observability & Config (Enhancement)

- [ ] Replace `print()` with `logging` module throughout `src/`
- [ ] Add a `config.py` or `settings.py` module for: frame interval, batch sizes, DB path, collection name, threshold defaults
- [ ] Read config from env vars with sensible defaults (e.g., `VRAG_DB_PATH`, `VRAG_FRAME_INTERVAL`)

**Risk:** Low — additive only

---

## 4. .gitignore File (Missing — Must Add)

Create `.gitignore` in repo root:

```gitignore
# Python
__pycache__/
*.py[cod]
*.pyo
.venv/
*.egg-info/

# App artifacts
temp_uploads/
temp_query.jpg
video_db_storage/

# Data (large files — use Git LFS or exclude)
data/videos/
# Keep data/frames/ in .gitignore or use Git LFS if needed
# data/frames/        # uncomment if frames should not be committed

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
```

**Note:** `data/frames/` currently has two pre-existing frame sets committed to the repo. Decide whether to keep them (for demo purposes) or exclude them.
