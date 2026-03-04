# V-RAG — Repo Audit Report

> **Audit date:** 2026-03-04 | **Auditor:** GitHub Copilot | **Commit:** HEAD (no VCS hash available)

---

## 1. Overview

**V-RAG** (Visual Retrieval Augmented Generation) is a local, single-user Streamlit application that lets users upload a video, extract frames, embed them with CLIP ViT-B-32 via `sentence-transformers`, store the vectors in ChromaDB, and then search for frames using natural-language text descriptions or webcam photos.

**Stack:** Python 3.13 · Streamlit · CLIP (sentence-transformers) · ChromaDB · OpenCV · PyTorch (CUDA 13.0)

---

## 2. File Tree & Inventory

```
Video Retrieval Augmented Generation/
├── .gitignore                    # 16 lines — excludes pycache, data, venv, IDE
├── app.py                        # 233 lines — PRIMARY ENTRYPOINT (Streamlit UI)
├── main.py                       # 77 lines  — CLI dev scaffold
├── requirements.txt              # 9 lines   — pip deps (extra-index for CUDA)
├── README.md                     # ~100 lines — project overview
├── data/
│   ├── videos/                   # Git-ignored; user video staging (1 MP4 in temp_uploads/)
│   └── frames/                   # Git-ignored; extracted JPEGs
│       ├── 15 minutes of heavy traffic…/    (901 JPEGs)
│       └── custom Youtube video…/           (31 JPEGs)
├── src/
│   ├── embedder.py               # 85 lines — CLIP wrapper (encode images + text)
│   ├── vector_db.py              # 58 lines — ChromaDB CRUD
│   ├── video_processor.py        # 91 lines — OpenCV frame extraction
│   └── __pycache__/              # bytecache (cpython-313)
├── temp_uploads/                 # Git-ignored; staging for uploaded videos
│   └── custom Youtube…Part1Trim.mp4
├── video_db_storage/             # Git-ignored; persistent ChromaDB
│   ├── chroma.sqlite3
│   └── 24280a94-…/              # HNSW segment (5 files)
└── docs/                         # Previous audit output + this audit
```

### File Inventory (source & config only)

| File | Type | Lines | Responsibility | Key Deps | Called By |
|---|---|---|---|---|---|
| `app.py` | Streamlit app | 233 | UI controller + pipeline orchestration | streamlit, torch, PIL, cv2, src.* | `streamlit run app.py` |
| `main.py` | CLI script | 77 | Dev-time pipeline runner + sanity check | src.*, glob | `python main.py` |
| `src/embedder.py` | Module | 90 | CLIP model: image & text → 512-d vectors | sentence_transformers, torch, PIL, numpy, tqdm | app.py, main.py |
| `src/vector_db.py` | Module | 72 | ChromaDB write (upsert) & read (search) | chromadb, numpy, pathlib | app.py, main.py |
| `src/video_processor.py` | Module | 88 | Video → JPEG frames (1 fps, resize 640px) | cv2, os, math | app.py, main.py |
| `src/__init__.py` | Package init | 0 | Makes `src` a proper Python package | — | Python import system |
| `requirements.txt` | Pip reqs | 9 | Dependency manifest | — | pip install |
| `README.md` | Docs | ~100 | Overview, quick-start, architecture prose | — | humans |
| `.gitignore` | Config | 16 | Exclusion rules | — | Git |

**Scanned & confirmed:** every non-binary file in the workspace.

---

## 3. Entrypoints & Boot

### Primary — `app.py` (Streamlit)

```
streamlit run app.py
```

Boot sequence:
1. `st.set_page_config(…)` — `app.py:L15–L20`
2. Custom CSS injection — `app.py:L23–L28`
3. `get_embedder()` / `get_db()` are `@st.cache_resource` singletons — `app.py:L31–L36`
4. `main()` called at `app.py:L233`

### Secondary — `main.py` (CLI)

```
python main.py
```

Calls `initialize_folders()` → scans `data/videos/` → runs extract → embed → index → hardcoded search `"traffic congestion"` (`main.py:L62`).

---

## 4. App Flow (Text Diagram)

### A. Ingestion (Upload + Process)

```
User ──[upload MP4]──▸ st.file_uploader [app.py:L115]
       │
       ▼
 save_uploaded_file()     →  temp_uploads/<name>            [app.py:L49–L58]
       │
       ▼
 process_video_pipeline() →  VideoProcessor.extract_frames() [video_processor.py:L10–L88]
       │                         └─▸ data/frames/<name>/*.jpg
       ▼
 FrameEmbedder.encode_images()  →  np.ndarray (N, 512)     [embedder.py:L28–L78]
       │
       ▼
 VideoSearchDB.add_frames()     →  ChromaDB                 [vector_db.py:L21–L40]
```

### B. Search — Text

```
User ──[type query]──▸ st.text_input [app.py:L146]
       │
       ▼
 FrameEmbedder.encode_text(query)  →  (512,) vector         [embedder.py:L80–L85]
       │
       ▼
 VideoSearchDB.search(emb, k)     →  top-k results          [vector_db.py:L42–L62]
       │
       ▼
 Filter score ≤ threshold  →  st.image() grid               [app.py:L181–L205]
```

### C. Search — Image/Camera

```
User ──[camera photo]──▸ st.camera_input [app.py:L153]
       │
       ▼
 PIL.Image → save("temp_query.jpg")                          [app.py:L171]
       │
       ▼
 FrameEmbedder.encode_images(["temp_query.jpg"])              [app.py:L177]
       │
       ▼
 VideoSearchDB.search(emb, k)  →  display                   [same as text path]
```

---

## 5. Data Flow

| Stage | Input | Output | Storage |
|---|---|---|---|
| Upload | Binary video from browser | Saved .mp4 at `temp_uploads/` | Filesystem |
| Extract | .mp4 | JPEGs `data/frames/<name>/frame_<ms>.jpg` | Filesystem |
| Embed | JPEG paths | `np.ndarray (N, 512)` | In-memory |
| Index | Embeddings + metadata dicts | ChromaDB records (id, embedding, metadata) | `video_db_storage/` |
| Query | Text string / PIL Image | `np.ndarray (512,)` | In-memory |
| Search | Query vector + k | `List[{'path', 'timestamp', 'score'}]` | Read from ChromaDB |

---

## 6. Dependency Notes

From `requirements.txt`:

| Package | Purpose | Pin | Risk |
|---|---|---|---|
| `torch` | GPU tensor ops | ❌ unpinned (cu130 index) | Breaking changes between major versions |
| `torchvision` | Vision utils for torch | ❌ unpinned | Must match torch version |
| `opencv-python` | Video decode | ❌ unpinned | Generally stable |
| `pillow` | Image loading | ❌ unpinned | Stable |
| `sentence-transformers` | CLIP wrapper | ❌ unpinned | API changes across 2.x/3.x |
| `chromadb` | Vector DB | ❌ unpinned | Major API changes 0.3→0.4→0.5 |
| `streamlit` | UI | ❌ unpinned | Deprecations in widget API |
| `tqdm` | Progress bars | ❌ unpinned | Stable |

**No versions are pinned.** This is a reliability risk — a fresh `pip install` may pull incompatible versions.

---

## 7. Issues Summary

> Detailed table in [ISSUES.md](ISSUES.md).

### P0 (Critical)

1. **~~Embedding/metadata alignment bug~~** ✅ FIXED (PR2) — `encode_images()` now returns `Tuple[np.ndarray, List[str]]` (`embedder.py:L32–33`); callers use order-preserving `meta_by_path` dict (`app.py:L111–113`, `main.py:L70–72`); `add_frames()` raises `ValueError` on mismatch (`vector_db.py:L38–41`).
2. **~~Path traversal in file upload~~** ✅ FIXED (PR2) — sanitized with `pathlib.Path(uploaded_file.name).name` (`app.py:L65`).
3. **~~CWD-dependent DB path~~** ✅ FIXED (PR2) — now `pathlib.Path(__file__).resolve().parent.parent / "video_db_storage"` (`vector_db.py:L14,L22`).

### P1 (Important)

4. **~~No dedup guard on re-index~~** ✅ FIXED (PR2) — `collection.upsert()` (`vector_db.py:L52`).
5. **~~Temp files never cleaned~~** ✅ FIXED (PR2+PR3) — uploaded video deleted in `try/finally` (`app.py:L155–160`); `temp_query.jpg` deleted in `try/finally` (`app.py:L199–206`).
6. **No dependency version pins** — `requirements.txt` still has zero `==` constraints.
7. **Zero tests / zero CI** — no test files, no GitHub Actions, no linting.
8. **Blocking I/O in Streamlit main thread** — still synchronous.
9. **~~`st.image(width='stretch')` deprecated~~** ✅ FIXED (PR3) — `use_container_width=True` (`app.py:L224`).

### P2 (Improvement)

10. **~~5-space indent in main.py~~** ✅ FIXED (PR1).
11. **`main.py` duplicates `app.py` pipeline** — still present.
12. **`print()` in some modules** — partially fixed; `app.py`, `embedder.py`, `vector_db.py` now use `logging`; `video_processor.py` and `main.py` still use `print()`.
13. **~~No `__init__.py` in `src/`~~** ✅ FIXED (PR1).
14. **~~Commented-out code~~** ✅ FIXED (PR1).
15. **Magic numbers for score thresholds** — still hardcoded (`app.py:L52–54`).
16. **~~`README.md` placeholder author~~** ✅ FIXED (PR1) — set to `Ahmad Mujtaba`.

---

## 8. Confirmed From Code vs Hypothesis

### Confirmed From Code

| Finding | Evidence | Status |
|---|---|---|
| ChromaDB path = `__file__`-relative `video_db_storage` | `vector_db.py:L14,L22` | ✅ Fixed (was `os.getcwd()`) |
| `encode_images` returns `Tuple[np.ndarray, List[str]]` with valid paths | `embedder.py:L32–33` | ✅ Fixed |
| Upload file name sanitized with `pathlib.Path().name` | `app.py:L65` | ✅ Fixed |
| `temp_query.jpg` deleted in `try/finally` | `app.py:L199–206` | ✅ Fixed |
| `collection.upsert()` used (not `add`) | `vector_db.py:L52` | ✅ Fixed |
| `logging` module used in `app.py`, `embedder.py`, `vector_db.py` | `app.py:L2,L11`, `embedder.py:L1,L9`, `vector_db.py:L1,L8` | ✅ Partially fixed |
| No test files anywhere in workspace | Searched `test_*.py`, `*_test.py`, `tests/` — 0 results | Still true |
| `.gitignore` exists and covers `__pycache__`, data, venv | `.gitignore:L1–16` | Still true |
| Uploaded video cleaned up in `try/finally` after pipeline | `app.py:L155–160` | ✅ Fixed |

### Hypothesis (Needs Verification)

| Hypothesis | What to check |
|---|---|
| ChromaDB default metric is L2 (not cosine) | Query `chroma.sqlite3` → `collections` table, or add explicit `metadata={"hnsw:space":"l2"}` |
| CLIP `sentence-transformers` auto-normalizes vectors | Check `model.encode()` source; if so, L2 ≡ cosine is equivalent |


---

## 9. Coverage Proof

| Category | Count | Action |
|---|---|---|
| Source `.py` files | 5 (`app.py`, `main.py`, `src/embedder.py`, `src/vector_db.py`, `src/video_processor.py`) | ✅ All read in full |
| Config files | 2 (`requirements.txt`, `.gitignore`) | ✅ All read in full |
| Docs `.md` files | 1 (source) `README.md` + 7 (audit output from prior pass) | ✅ README read; audit outputs are ours |
| Binary/assets | 932 JPEGs + 1 MP4 + 1 SQLite + 5 HNSW files + 3 `.pyc` | ❌ Excluded (binary; not useful for code audit) |
| Hidden/CI files | 0 (no `.github/`, no `Dockerfile`, no `.env`) | ✅ Confirmed absent via file search |

**Total source files: 8 / 8 = 100% read.**
