# V-RAG: API Inventory

> V-RAG is a **local single-user Streamlit application**. It exposes no server-side REST, GraphQL, gRPC, or WebSocket APIs. All interaction is through the Streamlit web UI or the CLI.

---

## UI Operations Summary

| Operation | UI Component | Function | Inputs | Outputs | Side Effects | Auth |
|---|---|---|---|---|---|---|
| Upload & process video | `st.file_uploader` + button | `process_video_pipeline()` | MP4/MOV/AVI binary | Progress bar, success toast | Writes `temp_uploads/`, `data/frames/`, ChromaDB | None |
| Text semantic search | `st.text_input` + button | `perform_search(..., mode="text")` | Query string (free text) | Frame grid with timestamps/confidence | None | None |
| Image/camera search | `st.camera_input` + button | `perform_search(..., mode="image")` | Camera image (JPEG via browser) | Frame grid with timestamps/confidence | Writes `temp_query.jpg` to CWD | None |
| Set result count | `st.slider` (1–20) | Passed as `k` to `perform_search` | Integer | Changes number of DB results | None | None |
| Set score threshold | `st.slider` (100–200) | Filter in `perform_search` | Float | Changes result filtering | None | None |
| Select data source | `st.radio` | Controls upload vs existing data mode | "Use Existing Data" / "Upload New Video" | Shows/hides upload widget | None | None |

---

## Streamlit Route Structure

Streamlit apps have a single page by default. All UI state is managed via Streamlit session re-runs (no explicit routing).

| Tab | Purpose | Evidence |
|---|---|---|
| Tab 1: `📝 Text Search` | Text query input and results | `app.py:L146–L149` |
| Tab 2: `📸 Camera Search` | Webcam capture and image search | `app.py:L152–L160` |

---

## Python Module API (Internal)

### `FrameEmbedder` (`src/embedder.py`)

| Method | Signature | Returns | Raises | Notes |
|---|---|---|---|---|
| `__init__` | `(model_name='clip-ViT-B-32')` | — | `Exception` if model load fails | Downloads model from HuggingFace on first run |
| `encode_images` | `(image_paths: List[str], batch_size: int = 32) -> np.ndarray` | `ndarray (N, 512)` or `ndarray([])` | Silent on individual image load error | Batch loops over paths; skips unreadable images |
| `encode_text` | `(text: str) -> np.ndarray` | `ndarray (512,)` | — | Single string to vector |

**Evidence:** `embedder.py:L10–L85`

---

### `VideoSearchDB` (`src/vector_db.py`)

| Method | Signature | Returns | Raises | Notes |
|---|---|---|---|---|
| `__init__` | `(collection_name='video_frames')` | — | — | Creates `video_db_storage/` if missing |
| `add_frames` | `(embeddings: np.ndarray, metadata: List[Dict]) -> None` | `None` | `ValueError` if len mismatch | IDs = JPEG basenames |
| `search` | `(query_embedding: np.ndarray, k: int = 5) -> List[Dict]` | `List[{'path', 'timestamp', 'score'}]` | — | Returns empty list if no results |

**Evidence:** `vector_db.py:L1–L58`

---

### `VideoProcessor` (`src/video_processor.py`)

| Method | Signature | Returns | Raises | Notes |
|---|---|---|---|---|
| `__init__` | `()` | — | — | No-op |
| `extract_frames` | `(video_path: str, output_folder: str, interval: int = 1) -> List[Dict]` | `List[{'frame_path': str, 'timestamp': float}]` | `FileNotFoundError`, `IOError` | timestamp in seconds (float) |

**Evidence:** `video_processor.py:L9–L83`

---

## CLI Interface (`main.py`)

| Command | Description | Inputs | Outputs |
|---|---|---|---|
| `python main.py` | Runs full pipeline on first video found in `data/videos/` | Any video at `data/videos/*.{mp4,avi,mov,mkv}` | Stdout logs; extracted frames; populated ChromaDB |

**Hardcoded sanity check query:** `"traffic congestion"` — `main.py:L62`

---

## Error Responses

| Scenario | Where | User Sees | Logged |
|---|---|---|---|
| No video uploaded | `app.py` | Nothing (button disabled until upload) | No |
| Frame extraction fails | `app.py:L80` | `st.error("Frame extraction failed.")` | No |
| Search error | `app.py:L215` | `st.error(f"Search Error: {e}")` | No |
| File save error | `app.py:L57` | `st.error(f"Error saving file: {e}")` | No |
| No results after filtering | `app.py:L184` | `st.warning("No matches found. Try adjusting the threshold.")` | No |
| Image path missing at render | `app.py:L204` | `st.error("Frame missing")` | No |
