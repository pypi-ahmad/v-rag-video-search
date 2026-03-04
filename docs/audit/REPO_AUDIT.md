# V-RAG — Full Repo Audit Report

> **Audit date:** 2026-03-04 | **Branch:** `full-repo-upgrade` | **Auditor:** GitHub Copilot

---

## 1. Overview

**V-RAG** (Visual Retrieval Augmented Generation) is a local, single-user Streamlit application.
Upload a video → extract frames → embed with CLIP ViT-B-32 → store in ChromaDB → search by text or camera image.

**Stack:** Python 3.13 · Streamlit · CLIP (`sentence-transformers`) · ChromaDB · OpenCV · PyTorch (CUDA 13.0)

---

## 2. File Tree & Inventory

```
Video Retrieval Augmented Generation/
├── .gitignore                   # 51 lines — comprehensive exclusion rules
├── app.py                       # 252 lines — PRIMARY ENTRYPOINT (Streamlit UI)
├── main.py                      # 106 lines — CLI dev scaffold
├── requirements.txt             # 9 lines  — pip deps (extra-index for CUDA)
├── README.md                    # ~230 lines — professional overview + Mermaid diagrams
├── data/
│   ├── videos/                  # Git-ignored; user video staging
│   └── frames/                  # Git-ignored; extracted JPEGs
├── src/
│   ├── __init__.py              # Empty — makes src a proper Python package
│   ├── embedder.py              # 90 lines — CLIP wrapper (encode images + text)
│   ├── vector_db.py             # 76 lines — ChromaDB CRUD (upsert + search)
│   ├── video_processor.py       # 93 lines — OpenCV frame extraction
│   └── __pycache__/             # Bytecache (cpython-313, git-ignored)
├── temp_uploads/                # Git-ignored; staged uploads (auto-cleaned after pipeline)
├── video_db_storage/            # Git-ignored; persistent ChromaDB
│   ├── chroma.sqlite3
│   └── <segment-uuid>/
└── docs/
    ├── API.md, ARCHITECTURE.md, CLEANUP_PLAN.md
    ├── DATA.md, FLOWS.md, OPS.md, REPO_REPORT.md
    └── audit/
        ├── FEATURE_IDEAS.md, ISSUES.md, QUICK_WINS.md
        ├── REPO_AUDIT.md (this file)
        └── ROADMAP.md
```

### Source File Inventory

| File | Lines | Responsibility | Key Deps | Called By |
|---|---|---|---|---|
| `app.py` | 252 | Streamlit UI + pipeline orchestration | streamlit, torch, PIL, cv2, src.* | `streamlit run app.py` |
| `main.py` | 106 | CLI dev runner + sanity check | src.*, glob, logging | `python main.py` |
| `src/embedder.py` | 90 | CLIP model: image & text → 512-d vectors | sentence_transformers, torch, PIL, numpy, tqdm, logging | app.py, main.py |
| `src/vector_db.py` | 76 | ChromaDB upsert & ANN search | chromadb, numpy, pathlib, logging | app.py, main.py |
| `src/video_processor.py` | 93 | Video → JPEG frames (1 fps, resize 640px) | cv2, logging, math, os | app.py, main.py |
| `src/__init__.py` | 0 | Package marker | — | Python import system |
| `requirements.txt` | 9 | Dependency manifest | — | pip install |
| `README.md` | ~230 | Overview, quick-start, Mermaid architecture | — | humans |
| `.gitignore` | 51 | Rules: Python, envs, OS, data, media | — | Git |

---

## 3. Entrypoints

### Primary — `app.py` (Streamlit)

```bash
streamlit run app.py
```

Boot: `st.set_page_config(…)` (`app.py:L20–L26`) → CSS injection (`app.py:L29–L34`) → `@st.cache_resource` singletons (`app.py:L37–L43`) → `main()` at `app.py:L245`.

### Secondary — `main.py` (CLI)

```bash
python main.py
```

`initialize_folders()` → scan `data/videos/` → extract → embed → index → sanity search `"traffic congestion"` (`main.py:L92`).

---

## 4. Pipeline Flows

### A. Ingestion

```
User upload → save_uploaded_file() [app.py:L56–L73]
  → temp_uploads/<sanitized_name> (__file__-relative)
  → process_video_pipeline() [app.py:L75–L128]
    → VideoProcessor.extract_frames() [video_processor.py:L13–L93]
    → FrameEmbedder.encode_images() → (ndarray, valid_paths) [embedder.py:L31–L87]
    → Rebuild metadata aligned to valid_paths [app.py:L112–L118]
    → VideoSearchDB.add_frames() via upsert [vector_db.py:L29–L55]
  → finally: os.remove(video_path) [app.py:L145–L148]
```

### B. Text Search

```
st.text_input [app.py:L160] → perform_search(mode="text") [app.py:L168–L240]
  → encode_text() [embedder.py:L89–L93]
  → search(emb, k) [vector_db.py:L57–L76]
  → filter score ≤ threshold → render grid [app.py:L207–L230]
```

### C. Image/Camera Search

```
st.camera_input [app.py:L164] → perform_search(mode="image") [app.py:L168–L240]
  → save temp_query.jpg (__file__-relative) [app.py:L182]
  → encode_images() [app.py:L184]
  → finally: os.remove() [app.py:L190–L193]
  → search + display
```

---

## 5. Issues Summary

> Full table: [ISSUES.md](ISSUES.md)

### P0 (Critical) — ALL FIXED

1. Embedding/metadata alignment mismatch — ✅
2. Path traversal in upload — ✅
3. CWD-dependent DB path — ✅

### P1 (Important)

4. No dedup guard (add→upsert) — ✅ FIXED
5. Temp files never cleaned — ✅ FIXED
6. No dependency version pins — **Open**
7. Zero tests / zero CI — **Open**
8. Blocking I/O in Streamlit thread — **Open**
9. Deprecated `st.image(width=…)` — ✅ FIXED
10. `print()` in modules — ✅ FIXED (all use `logging` now)
11. CWD-relative temp paths — ✅ FIXED (`__file__`-relative)

### P2 (Improvement)

12. `main.py` duplicates pipeline — Open (keep as dev scaffold)
13. Magic numbers in score thresholds — Open
14. No `src/__init__.py` — ✅ FIXED

---

## 6. Dependency Notes

| Package | Pinned? | Risk |
|---|---|---|
| torch (cu130) | ❌ | Breaking changes between majors |
| torchvision | ❌ | Must match torch version |
| sentence-transformers | ❌ | API changes 2.x→3.x |
| chromadb | ❌ | Major API changes 0.3→0.5 |
| streamlit | ❌ | Widget deprecations |
| opencv-python, pillow, tqdm | ❌ | Generally stable |

---

## 7. Logging

All modules now use Python `logging` (zero `print()` calls remain):

| Module | Evidence |
|---|---|
| `app.py:L11–L12` | `logging.basicConfig(…)` + `logger = logging.getLogger(__name__)` |
| `main.py:L8–L9` | Same |
| `src/embedder.py:L9` | `logger = logging.getLogger(__name__)` |
| `src/vector_db.py:L8` | Same |
| `src/video_processor.py:L7` | Same |

---

## 8. Security

| Risk | Severity | Status |
|---|---|---|
| Path traversal (upload) | P0 | ✅ FIXED (`pathlib.name` sanitization — `app.py:L67`) |
| Temp file leak | P1 | ✅ FIXED (`try/finally` in `app.py:L145–L148`, `app.py:L190–L193`) |
| CWD-dependent paths | P1 | ✅ FIXED (DB: `vector_db.py:L11,L21`; uploads: `app.py:L60–L62`; temp query: `app.py:L182`) |
| No auth | Info | Expected — local single-user tool |
| Model auto-download | Info | CLIP downloads from HuggingFace on first run |

---

## 9. Coverage Proof

| Category | Count |
|---|---|
| Source/config/doc files opened and read in full | 21 |
| Python bytecache `.pyc` skipped (binary) | 3 |
| ChromaDB segments skipped (binary) | 6 |
| JPEG frames skipped (binary) | ~932 |
| Video files skipped (binary) | 1 |

**Source code coverage: 21/21 = 100%**
