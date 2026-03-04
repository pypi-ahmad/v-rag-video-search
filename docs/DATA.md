# V-RAG: Data Schemas, Stores, and Migrations

---

## 1. Domain Entities

### Frame Metadata (Python Dict)

Produced by `VideoProcessor.extract_frames()` — `video_processor.py:L57–L63`

```python
{
    'frame_path': str,   # Absolute path to JPEG on disk
                         # e.g. "data/frames/<video_name>/frame_14000.jpg"
    'timestamp': float   # Position in video, in seconds
                         # e.g. 14.0 (= 14000ms / 1000)
}
```

### Embedding Vector

Produced by `FrameEmbedder.encode_images()` — `embedder.py:L72`

```
np.ndarray, dtype=float32, shape=(N, 512)
```

- N = number of successfully loaded frames
- 512 = CLIP ViT-B-32 embedding dimension
- Values are L2-normalized (CLIP model output via sentence-transformers)

### Search Result (Python Dict)

Produced by `VideoSearchDB.search()` — `vector_db.py:L52–L56`

```python
{
    'path': str,        # Same as frame_path from metadata
    'timestamp': float, # Seconds from video start
    'score': float      # L2 distance — lower = more similar
                        # Typical range: 80–220 for CLIP ViT-B-32
}
```

---

## 2. Storage Systems

### ChromaDB (Primary Vector Store)

| Property | Value | Evidence |
|---|---|---|
| Type | Embedded vector database (SQLite-backed) | `vector_db.py:L8` |
| Location | `video_db_storage/` (CWD-relative) | `vector_db.py:L6` |
| Client mode | `PersistentClient` | `vector_db.py:L8` |
| Collection name | `video_frames` | `vector_db.py:L14` |
| ID format | JPEG basename, e.g. `frame_14000.jpg` | `vector_db.py:L24` |
| Embedding dimension | 512 (CLIP ViT-B-32) | `embedder.py:L12` |
| Distance metric | Default (L2 / Euclidean) — not explicitly configured | `vector_db.py:L14` |
| Persistence | Survives process restart | `vector_db.py:L8` |

**Physical files:**
```
video_db_storage/
├── chroma.sqlite3                              # SQLite metadata + index
└── 24280a94-2546-40c4-af7f-dfd388bdb332/      # Vector segment binary files
```

**Write path:** `VideoSearchDB.add_frames()` → `collection.add()` — `vector_db.py:L32`  
**Read path:** `VideoSearchDB.search()` → `collection.query()` — `vector_db.py:L43`

#### ChromaDB Record Schema

```
Collection: video_frames
├── id         TEXT     — JPEG basename (e.g. "frame_14000.jpg")
├── embedding  FLOAT[]  — 512-dim vector
└── metadata   JSON     — {'frame_path': str, 'timestamp': float}
```

---

### Filesystem Frame Store

| Property | Value | Evidence |
|---|---|---|
| Location | `data/frames/<video_name>/` | `app.py:L64`, `video_processor.py:L62` |
| Format | JPEG | `video_processor.py:L62` |
| Naming | `frame_<timestamp_ms>.jpg` | `video_processor.py:L61` |
| Max height | 640px (width scaled proportionally) | `video_processor.py:L52–L60` |
| Resize interpolation | `cv2.INTER_AREA` | `video_processor.py:L58` |
| Populated by | `VideoProcessor.extract_frames()` | `video_processor.py:L9` |
| Read by | `FrameEmbedder.encode_images()` (during indexing) | `app.py:L86` |
| Served by | `st.image(res['path'])` (during search display) | `app.py:L192` |

**Pre-existing frame sets (in repo):**
```
data/frames/
├── 15 minutes of heavy traffic noise in India - 14-08-2022/
└── custom Youtube video file by Mujtaba1_Part1Trim/
```

---

### Temp Upload Directory

| Property | Value | Evidence |
|---|---|---|
| Location | `temp_uploads/` | `app.py:L51` |
| Purpose | Staging area for uploaded videos before pipeline | `app.py:L49–L58` |
| Cleanup | **Never cleaned up** (manual deletion required) | `app.py:L49–L58` (no cleanup code) |

---

### Temp Query Image

| Property | Value | Evidence |
|---|---|---|
| Location | `temp_query.jpg` (CWD root) | `app.py:L171` |
| Purpose | Intermediate storage for camera-captured query image | `app.py:L171` |
| Cleanup | **Never cleaned up** | `app.py:L171` (no os.remove call) |

---

## 3. Data Reads and Writes Summary

| Operation | Reads | Writes | Transaction? |
|---|---|---|---|
| Frame extraction | Raw video file | JPEG files in `data/frames/` | No |
| Embedding generation | JPEG files from `data/frames/` | In-memory numpy array | No |
| DB indexing | In-memory embeddings + metadata | ChromaDB `video_frames` collection | No (ChromaDB auto-commit) |
| Text search | ChromaDB collection | Nothing | No |
| Image search | ChromaDB collection, `temp_query.jpg` | `temp_query.jpg` | No |

---

## 4. Migrations

**None exist.** No Alembic, no Django migrations, no custom migration scripts.

The schema is created implicitly via `get_or_create_collection()` on first boot — `vector_db.py:L14`.

**Risk:** If ChromaDB schema changes between versions (e.g., embedding dimension change, collection config change), the existing `video_db_storage/` data may be incompatible. Manual deletion of `video_db_storage/` and re-indexing is the only recovery path.

---

## 5. Data Volume Estimates

| Dataset | Frame rate | Duration | Approx frames | Approx storage (JPEG) | Approx ChromaDB size |
|---|---|---|---|---|---|
| 1-hour video | 1 fps | 60 min | ~3,600 | ~360 MB (100KB/frame) | ~7.2 MB (2KB/vector) |
| 15-min video | 1 fps | 15 min | ~900 | ~90 MB | ~1.8 MB |

> CLIP 512-dim float32 vector = 2048 bytes = ~2 KB per frame in ChromaDB storage.
