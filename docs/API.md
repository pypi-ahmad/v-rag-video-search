# V-RAG: API Inventory

> Local single-user Streamlit app — no REST/GraphQL endpoints. All interaction through UI or CLI.

---

## UI Operations

| Operation | UI Element | Handler | Side Effects |
|---|---|---|---|
| Upload & process | `st.file_uploader` + button (`app.py:L137–L148`) | `save_uploaded_file()` + `process_video_pipeline()` | Writes frames, ChromaDB; cleans temp upload |
| Text search | `st.text_input` + button (`app.py:L160–L161`) | `perform_search(mode="text")` | None |
| Camera search | `st.camera_input` + button (`app.py:L164–L166`) | `perform_search(mode="image")` | Writes+deletes `temp_query.jpg` |
| Max results | `st.slider` (`app.py:L150`) | Passed as `k` | None |
| Threshold | `st.slider` (`app.py:L151`) | Filter in search | None |

---

## Python Module API

### `FrameEmbedder` (`src/embedder.py`)

| Method | Signature | Returns | Notes |
|---|---|---|---|
| `__init__` | `(model_name='clip-ViT-B-32')` | — | Auto-downloads from HuggingFace |
| `encode_images` | `(image_paths, batch_size=32)` | `Tuple[ndarray(N,512), List[str]]` | Skips bad images; returns aligned pair |
| `encode_text` | `(text: str)` | `ndarray(512,)` | Single query embedding |

### `VideoSearchDB` (`src/vector_db.py`)

| Method | Signature | Returns | Notes |
|---|---|---|---|
| `__init__` | `(collection_name='video_frames')` | — | DB path is `__file__`-relative |
| `add_frames` | `(embeddings, metadata)` | None | Upsert; raises `ValueError` on mismatch |
| `search` | `(query_embedding, k=5)` | `List[Dict]` | Keys: `path`, `timestamp`, `score` |

### `VideoProcessor` (`src/video_processor.py`)

| Method | Signature | Returns | Notes |
|---|---|---|---|
| `__init__` | `()` | — | No-op |
| `extract_frames` | `(video_path, output_folder, interval=1)` | `List[Dict]` | Keys: `frame_path`, `timestamp` |

---

## CLI (`main.py`)

| Command | Description |
|---|---|
| `python main.py` | Full pipeline on first video in `data/videos/` + sanity search |
