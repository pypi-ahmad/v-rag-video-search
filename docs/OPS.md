# V-RAG: Operations Runbook

---

## 1. Prerequisites

| Requirement | Minimum | Notes |
|---|---|---|
| Python | 3.10+ | Bytecache suggests 3.13 is in use (`src/__pycache__/`) |
| pip | Latest | For `--extra-index-url` support |
| GPU (optional) | CUDA 13.0-compatible NVIDIA GPU | Falls back to CPU automatically |
| Disk space | ~1 GB | For video frames, mode weights (~350MB for CLIP ViT-B-32), and ChromaDB |
| RAM | ~4 GB | Minimum for CPU-only inference |

---

## 2. Installation

### Step 1: Clone

```bash
git clone <repo-url>
cd "Video Retrieval Augmented Generation"
```

### Step 2: Create Virtual Environment

```bash
python -m venv .venv

# Activate — Windows (PowerShell):
.venv\Scripts\Activate.ps1

# Activate — Windows (CMD):
.venv\Scripts\activate.bat

# Activate — Mac/Linux:
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**What this installs** (`requirements.txt`):

| Package | Purpose |
|---|---|
| `torch` (cu130 wheel) | GPU tensor operations for CLIP inference |
| `torchvision` | Vision utilities used by PyTorch |
| `opencv-python` | Video decoding and frame extraction |
| `pillow` | PIL image loading for embedding |
| `sentence-transformers` | CLIP ViT-B-32 model wrapper |
| `chromadb` | Embedded vector database |
| `streamlit` | Web UI framework |
| `tqdm` | Progress bars in CLI/embedding loop |

**CUDA note:** `requirements.txt:L1` includes `--extra-index-url https://download.pytorch.org/whl/cu130`. If CUDA 13.0 is not available, pip will fall back to the CPU wheel from PyPI. No manual action needed.

**Model download:** `clip-ViT-B-32` (~350 MB) is automatically downloaded from HuggingFace Hub on first run of `FrameEmbedder.__init__()` — `embedder.py:L20`. Requires internet access on first run only.

---

## 3. Running the Application

### Primary: Streamlit UI

```bash
streamlit run app.py
```

Opens at `http://localhost:8501` by default.

**To change port:**
```bash
streamlit run app.py --server.port 8080
```

### Secondary: CLI Driver (Dev/Test)

```bash
# Requires at least one video in data/videos/
python main.py
```

Hardcoded sanity search query: `"traffic congestion"` — `main.py:L62`

---

## 4. Using the Application

### Ingest a New Video

1. Launch `streamlit run app.py`
2. In the sidebar, select **"Upload New Video"**
3. Upload an MP4/MOV/AVI file
4. Click **"🚀 Process & Index Video"**
5. Wait for the pipeline to complete (progress bar)

### Search with Text

1. In the **"📝 Text Search"** tab, type a description (e.g., `"red car at intersection"`)
2. Click **"Search Text"**
3. Adjust **"Max Results"** (1–20) and **"Sensitivity Threshold"** (100–200) sliders in the sidebar to tune results

### Search with Camera

1. In the **"📸 Camera Search"** tab, allow browser camera access
2. Take a photo of a reference object
3. Click **"Search Image"**

---

## 5. Directory Setup

The app auto-creates these on first run:

| Directory | Created By | Evidence |
|---|---|---|
| `data/videos/` | `main.py:initialize_folders()` | `main.py:L11` |
| `data/frames/` | `main.py:initialize_folders()` | `main.py:L11` |
| `temp_uploads/` | `app.py:save_uploaded_file()` | `app.py:L63` |
| `video_db_storage/` | `VideoSearchDB.__init__()` | `vector_db.py:L22–L23` (path derived from `__file__`, not CWD) |

---

## 6. Environment Variables

**None are used.** All paths are hardcoded.

**CWD note:** The `video_db_storage/` path is now **`__file__`-relative** (`vector_db.py:L14,L22`), so ChromaDB works regardless of where you launch the app from. However, several other paths are still CWD-relative:
- Frame paths stored in ChromaDB metadata are CWD-relative strings (e.g. `data\frames\...`) — `video_processor.py:L78`
- `temp_uploads/` is CWD-relative — `app.py:L63`
- `temp_query.jpg` is written to CWD — `app.py:L198`

**Recommendation:** Run from the repository root to ensure frame paths resolve correctly when displayed in search results.

---

## 7. Resetting the Database

To clear all indexed frames and start fresh:

```bash
# From repo root:
rm -rf video_db_storage/
# Then restart the app — it will recreate the DB automatically
```

Alternatively, to remove extracted frames too:

```bash
rm -rf video_db_storage/ data/frames/ temp_uploads/ temp_query.jpg
```

---

## 8. Testing

**No automated tests exist in this repository.**

### Manual Test Checklist

- [ ] Upload a short video (< 30 seconds) — pipeline completes without error
- [ ] Text search with a relevant query — returns results
- [ ] Text search with an irrelevant query — returns no results (adjust threshold)
- [ ] Camera search — takes photo, returns results
- [ ] Threshold slider — lowering threshold reduces results; raising increases
- [ ] Re-uploading same video — no crash (ChromaDB upserts)
- [ ] App restart — existing indexed data is preserved (ChromaDB is persistent)

---

## 9. CI/CD

**Not configured.** No Dockerfile, no `.github/workflows/`, no `Makefile`, no `tox.ini`, no `pyproject.toml`.

---

## 10. Performance Tuning

| Parameter | Default | Tuning Guidance |
|---|---|---|
| Frame interval | 1 second | Increase to 2–5s for long videos to reduce frame count |
| Batch size (GPU) | 32 | Reduce if CUDA OOM errors occur |
| Batch size (CPU) | 4 | Increase to 8–16 if RAM permits |
| Max results (`k`) | 6 | Increase for broader search recall |
| Threshold | 160.0 | Decrease for stricter matches; increase for more results |

**Evidence:** `app.py:L88`, `app.py:L76 (interval=1)`, `app.py:L128–L129`

---

## 11. Known Issues / Gotchas

1. **CWD affects frame display:** Frame paths in ChromaDB metadata are stored as CWD-relative strings. If you launch from a different directory, the DB will work fine (path is `__file__`-relative) but search result images may not display because `os.path.exists(res['path'])` will fail. Run from the repo root.
2. **Re-indexing same video:** Uses `upsert()` so duplicate IDs are safely overwritten. Old frames from a previous extraction with different timestamps will remain as orphans in the DB. To clean up: delete `video_db_storage/` and re-process.
3. **No version pins:** `requirements.txt` has no `==` constraints — a fresh install may pull breaking changes.
4. **No tests / CI:** All validation is manual.
5. **Pre-existing frame data:** Two frame sets exist in `data/frames/` but may not be indexed in `video_db_storage/` — search results will be empty until re-indexed.
6. **First run download:** CLIP model (~350 MB) downloads on first `FrameEmbedder` instantiation. Plan for network access.
