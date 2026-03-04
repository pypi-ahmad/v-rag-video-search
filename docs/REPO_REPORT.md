# V-RAG: Complete Engineering Report

> **Audit Date:** 2026-03-04 | **Branch:** `full-repo-upgrade`

---

## A. Repository Map

```
Video Retrieval Augmented Generation/
├── .gitignore              # 51 lines — Python, envs, OS, data, media, IDE
├── app.py                  # 252 lines — Streamlit UI (primary entrypoint)
├── main.py                 # 106 lines — CLI dev scaffold
├── requirements.txt        # 9 lines — pip deps (CUDA 13.0 extra-index)
├── README.md               # ~230 lines — professional overview + Mermaid diagrams
├── src/
│   ├── __init__.py         # Empty package marker
│   ├── embedder.py         # 90 lines — CLIP ViT-B-32 wrapper
│   ├── vector_db.py        # 76 lines — ChromaDB manager (upsert + search)
│   └── video_processor.py  # 93 lines — OpenCV frame extractor
├── data/
│   ├── videos/             # Git-ignored; raw videos
│   └── frames/             # Git-ignored; extracted JPEGs
├── temp_uploads/           # Git-ignored; auto-cleaned staging
├── video_db_storage/       # Git-ignored; ChromaDB persistence
└── docs/                   # Engineering documentation
```

---

## B. Entrypoints

**Primary:** `streamlit run app.py` — boots Streamlit UI, caches `FrameEmbedder` and `VideoSearchDB` via `@st.cache_resource` (`app.py:L37–L43`).

**Secondary:** `python main.py` — CLI scaffold for dev testing (`main.py:L24–L106`).

---

## C. Module Summary

| Module | Lines | Purpose | Logging |
|---|---|---|---|
| `app.py` | 252 | Streamlit UI + pipeline orchestration | ✅ `logging` |
| `main.py` | 106 | CLI dev runner | ✅ `logging` |
| `src/embedder.py` | 90 | CLIP encode (images + text) | ✅ `logging` |
| `src/vector_db.py` | 76 | ChromaDB CRUD | ✅ `logging` |
| `src/video_processor.py` | 93 | Frame extraction | ✅ `logging` |

Zero `print()` calls remain across all source files.

---

## D. Key Design Decisions

1. **DB path stability:** `pathlib.Path(__file__).resolve().parent.parent / "video_db_storage"` — `vector_db.py:L11,L21`
2. **Temp path stability:** `temp_uploads/` and `temp_query.jpg` anchored to `os.path.dirname(os.path.abspath(__file__))` — `app.py:L60–L62`, `app.py:L182`
3. **Upload sanitization:** `pathlib.Path(uploaded_file.name).name` — `app.py:L67`
4. **Embedding/metadata alignment:** `encode_images()` returns `Tuple[ndarray, List[str]]` — `embedder.py:L31–L87`; callers rebuild metadata via `meta_by_path` — `app.py:L112–L118`
5. **Idempotent writes:** `collection.upsert()` — `vector_db.py:L50`
6. **Temp cleanup:** `try/finally` for uploaded video (`app.py:L145–L148`) and query image (`app.py:L190–L193`)

---

## E. Issues Status

| Severity | Total | Fixed | Open |
|---|---|---|---|
| P0 | 3 | 3 | 0 |
| P1 | 8 | 6 | 2 (no version pins, no tests) |
| P2 | 7 | 5 | 2 (main.py dup, magic numbers) |
| **Total** | **18** | **14** | **4** |

See [audit/ISSUES.md](audit/ISSUES.md) for the full table.

---

## F. Dependencies

From `requirements.txt` (no version pins):

| Package | Purpose |
|---|---|
| `torch` (cu130) | GPU inference |
| `torchvision` | Vision utilities |
| `opencv-python` | Video decode |
| `pillow` | Image loading |
| `sentence-transformers` | CLIP ViT-B-32 |
| `chromadb` | Vector DB |
| `streamlit` | Web UI |
| `tqdm` | Progress bars |

---

## G. Security & Quality

- **Path traversal:** ✅ Fixed
- **Temp file leaks:** ✅ Fixed
- **CWD-dependent paths:** ✅ Fixed (DB, temp_uploads, temp_query)
- **Tests:** ❌ None (recommended: PR 8 in roadmap)
- **CI:** ❌ None
- **Auth:** N/A — local single-user tool

---

## H. Related Docs

- [ARCHITECTURE.md](ARCHITECTURE.md) — component diagrams
- [FLOWS.md](FLOWS.md) — runtime sequence diagrams
- [API.md](API.md) — module API inventory
- [DATA.md](DATA.md) — schemas + storage
- [OPS.md](OPS.md) — operations runbook
- [CLEANUP_PLAN.md](CLEANUP_PLAN.md) — legacy cleanup
- [audit/REPO_AUDIT.md](audit/REPO_AUDIT.md) — full audit report
- [audit/ISSUES.md](audit/ISSUES.md) — issues register
- [audit/ROADMAP.md](audit/ROADMAP.md) — phased PR plan
- [audit/QUICK_WINS.md](audit/QUICK_WINS.md) — patch suggestions
- [audit/FEATURE_IDEAS.md](audit/FEATURE_IDEAS.md) — future features
