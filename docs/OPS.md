# V-RAG: Operations Runbook

---

## 1. Prerequisites

| Requirement | Minimum | Notes |
|---|---|---|
| Python | 3.10+ | Bytecache confirms 3.13 in use |
| pip | Latest | For `--extra-index-url` support |
| GPU (optional) | CUDA 13.0-compatible NVIDIA GPU | Falls back to CPU automatically |
| Disk | ~1 GB | Frames + model (~350 MB) + ChromaDB |
| RAM | ~4 GB | Minimum for CPU-only inference |

---

## 2. Installation

```bash
git clone https://github.com/pypi-ahmad/v-rag-video-search.git
cd v-rag-video-search
python -m venv .venv

# Windows:
.venv\Scripts\Activate.ps1
# Mac/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

**CUDA note:** `requirements.txt:L1` specifies `--extra-index-url https://download.pytorch.org/whl/cu130`. Falls back to CPU if no compatible GPU.

**Model download:** `clip-ViT-B-32` (~350 MB) auto-downloads from HuggingFace on first `FrameEmbedder.__init__()` — `embedder.py:L23`.

---

## 3. Running

### Streamlit UI (Primary)

```bash
streamlit run app.py
# Opens http://localhost:8501

# Custom port:
streamlit run app.py --server.port 8080
```

### CLI (Dev/Test)

```bash
# Requires at least one video in data/videos/
python main.py
```

---

## 4. Usage

### Ingest a Video

1. Launch `streamlit run app.py`
2. Sidebar → **"Upload New Video"** → select MP4/MOV/AVI
3. Click **"🚀 Process & Index Video"**
4. Wait for pipeline (progress bar)

### Text Search

Tab **"📝 Text Search"** → type query → click **"Search Text"**.
Adjust **Max Results** (1–20) and **Threshold** (100–200) in sidebar.

### Camera Search

Tab **"📸 Camera Search"** → take photo → click **"Search Image"**.

---

## 5. Paths & Storage

| Path | Created By | Stable? | Notes |
|---|---|---|---|
| `video_db_storage/` | `VideoSearchDB.__init__()` | ✅ `__file__`-relative (`vector_db.py:L11,L21`) | Works from any CWD |
| `temp_uploads/` | `save_uploaded_file()` | ✅ `__file__`-relative (`app.py:L60–L62`) | Auto-cleaned after pipeline |
| `temp_query.jpg` | `perform_search(mode="image")` | ✅ `__file__`-relative (`app.py:L182`) | Auto-cleaned in `finally` |
| `data/frames/<name>/` | `process_video_pipeline()` | ⚠️ CWD-relative | Run from repo root |

> **Do not commit** `data/frames/`, `video_db_storage/`, or `temp_uploads/` — all are in `.gitignore`.

---

## 6. Reset / Cleanup

```bash
# Remove everything:
rm -rf video_db_storage/ data/frames/ temp_uploads/ temp_query.jpg

# Windows PowerShell:
Remove-Item -Recurse -Force video_db_storage, data\frames, temp_uploads -ErrorAction SilentlyContinue
```

Restart the app — DB is recreated automatically.

---

## 7. Testing (Manual)

No automated tests exist yet. Manual checklist:

- [ ] Upload a short video → pipeline completes
- [ ] Text search with relevant query → returns results
- [ ] Camera search → returns results
- [ ] Re-upload same video → no crash (upsert)
- [ ] Restart app → indexed data persists

---

## 8. Performance Tuning

| Parameter | Default | Evidence | Guidance |
|---|---|---|---|
| Frame interval | 1 sec | `app.py:L97` | Increase for long videos |
| Batch size (GPU) | 32 | `app.py:L107` | Reduce if CUDA OOM |
| Batch size (CPU) | 4 | `app.py:L107` | Increase if RAM permits |
| Max results (k) | 6 | `app.py:L150` | Increase for broader recall |
| Threshold | 160.0 | `app.py:L151` | Decrease for stricter matches |

---

## 9. Logging

All modules use Python `logging` at INFO level:

```
INFO | src.embedder | Initializing FrameEmbedder...
INFO | src.vector_db | Connected to ChromaDB at …
INFO | src.video_processor | (errors only)
```

Configure via `logging.basicConfig()` in `app.py:L11` or `main.py:L8`.

---

## 10. Known Gotchas

1. **Frame paths are CWD-relative** in ChromaDB metadata. Run from the repo root.
2. **Orphan frames** remain in DB after re-extraction with different timestamps. Delete `video_db_storage/` to reset.
3. **No version pins** — fresh install may pull incompatible packages.
4. **First-run download** — CLIP model (~350 MB) needs internet on first launch.
