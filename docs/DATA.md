# V-RAG: Data Schemas & Stores

---

## 1. Domain Entities

### Frame Metadata (Dict)

Produced by `VideoProcessor.extract_frames()` — `video_processor.py:L83–L86`

```python
{'frame_path': str, 'timestamp': float}  # path to JPEG, seconds from video start
```

### Embedding Vector

Produced by `FrameEmbedder.encode_images()` — `embedder.py:L85`

```
np.ndarray, dtype=float32, shape=(N, 512)
```

### Search Result (Dict)

Produced by `VideoSearchDB.search()` — `vector_db.py:L70–L73`

```python
{'path': str, 'timestamp': float, 'score': float}  # score = L2 distance (lower = better)
```

---

## 2. ChromaDB

| Property | Value | Evidence |
|---|---|---|
| Client | `PersistentClient` | `vector_db.py:L24` |
| Location | `video_db_storage/` (`__file__`-relative) | `vector_db.py:L11,L21` |
| Collection | `video_frames` | `vector_db.py:L25` |
| ID format | JPEG basename (`frame_14000.jpg`) | `vector_db.py:L44` |
| Embedding dim | 512 | `embedder.py:L12` |
| Distance | Default (L2) | Not explicitly configured |
| Write | `collection.upsert()` | `vector_db.py:L50` |
| Read | `collection.query()` | `vector_db.py:L62` |

---

## 3. Frame Store

| Property | Value |
|---|---|
| Location | `data/frames/<video_name>/frame_<ms>.jpg` |
| Format | JPEG (OpenCV default) |
| Max height | 640px (aspect-preserving) |
| Resize | `cv2.INTER_AREA` — `video_processor.py:L76` |

---

## 4. Temp Files

| File | Purpose | Cleanup |
|---|---|---|
| `temp_uploads/<name>` | Staged upload | `try/finally` in `app.py:L145–L148` |
| `temp_query.jpg` | Camera query image | `try/finally` in `app.py:L190–L193` |

Both paths are `__file__`-relative (not CWD-dependent).

---

## 5. Migrations

None. Schema created implicitly via `get_or_create_collection()` — `vector_db.py:L25`.
