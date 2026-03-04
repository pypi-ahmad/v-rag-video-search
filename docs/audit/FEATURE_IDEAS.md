# V-RAG — Feature Ideas

> Ordered by estimated value-to-effort ratio. Each idea includes what code would need to change.

---

## Tier 1 — High Value, Moderate Effort

### 1. Video Timeline Scrubber

**What:** When search results are displayed, show a clickable mini-timeline bar (like YouTube's preview strip) highlighting where each match falls in the video. Clicking a match opens that timestamp in a video player widget.

**Why:** Users currently only see isolated frames with MM:SS labels. A timeline gives temporal context — "these matches cluster around minute 5" — which is far more useful for surveillance analysis.

**How:**
- Use `st.video(video_path, start_time=timestamp)` for in-app playback — Streamlit already supports this.
- Render a horizontal bar chart (`st.bar_chart` or Plotly) showing match density per time bucket.
- **Files affected:** `app.py` (new section in `perform_search()`).

**Effort:** M (3–4h)

---

### 2. Multi-Video Index

**What:** Support indexing multiple videos into the same ChromaDB collection, each with a `video_name` metadata field. Searches return results across all indexed videos with a filter/facet by video.

**Why:** Current system overwrites or mixes all frames into one flat namespace (ID = JPEG basename, which can collide across videos).

**How:**
- Add `video_name` to metadata dict in `video_processor.py:L80`.
- Prefix IDs with video name: `f"{video_name}__frame_{timestamp_ms}.jpg"` in `vector_db.py:L30`.
- Add `where={"video_name": selected}` filter to `collection.query()`.
- Add a video selector in the Streamlit sidebar.
- **Files affected:** `src/video_processor.py`, `src/vector_db.py`, `app.py`.

**Effort:** L (4–6h)

---

### 3. Batch Upload & Queue

**What:** Allow users to upload multiple videos at once. Show a processing queue with status per video (queued → processing → done).

**Why:** Currently only one video can be processed per session click. Real-world surveillance has dozens of clips.

**How:**
- Use `st.file_uploader(..., accept_multiple_files=True)`.
- Loop through files; track state in `st.session_state`.
- **Files affected:** `app.py` (upload section).

**Effort:** M (2–3h)

---

## Tier 2 — Valuable, Larger Effort

### 4. Temporal / Action Search

**What:** Instead of single-frame matching, analyze sequences of N consecutive frames to detect *actions* (e.g., "car crash", "person running", "u-turn"). Use an embedding over frame *windows* instead of individual frames.

**Why:** CLIP embeddings are per-image. They lose motion and temporal context. A crash looks like parked cars in a single frame.

**How:**
- During ingestion, generate a sliding window of N=5 frames and average their CLIP embeddings → store as "scene" embedding.
- Or, use a video-native model: VideoMAE, X-CLIP, InternVideo.
- **Files affected:** `src/embedder.py` (new `encode_video_window()`), `src/video_processor.py` (return frame groups), `src/vector_db.py` (new collection `video_scenes`).

**Effort:** XL (8–16h)

---

### 5. Object Detection + CLIP Hybrid

**What:** Run YOLOv8 (or YOLO-World) on each frame to detect and crop individual objects, then CLIP-embed each crop. This enables searches like "red truck" that match the specific truck, not the entire scene.

**Why:** CLIP embeds the whole frame — a "red truck" query might match any frame containing red or trucks vaguely. Object-level embeddings are far more precise.

**How:**
- Add `ultralytics` to deps.
- New `src/detector.py`: `ObjectDetector.detect(frame) → List[{'class', 'bbox', 'crop_path'}]`.
- Embed crops and store with extra metadata `{'object_class': 'truck', 'bbox': [x1,y1,x2,y2]}`.
- UI: add an "Object Search" tab with class filter dropdown.
- **Files affected:** `src/detector.py` (new), `app.py`, `src/vector_db.py`.

**Effort:** XL (10–20h)

---

### 6. Live RTSP Stream Ingestion

**What:** Accept an RTSP URL instead of a file upload. Continuously extract, embed, and index frames from a live camera feed.

**Why:** Traffic and surveillance cameras are live; having to record and upload is a friction point.

**How:**
- `cv2.VideoCapture("rtsp://...")` works natively — `video_processor.py:L29` already uses `VideoCapture`.
- Run extraction in a background thread with a ring buffer.
- Periodically batch-embed and index new frames.
- **Files affected:** `src/video_processor.py` (new `stream_frames()` generator), `app.py` (new input mode).

**Effort:** L (6–10h)

---

## Tier 3 — Nice to Have

### 7. Export / Report Generation

**What:** Allow users to export search results as a PDF or CSV report: timestamp, frame image, query, score.

**Why:** Surveillance analysis often requires evidence reports.

**How:**
- Use `reportlab` or `fpdf2` for PDF, or `pandas.DataFrame.to_csv()`.
- Add an "Export Results" button below the search grid.
- **Files affected:** `app.py` (new export section).

**Effort:** M (2–3h)

---

### 8. LLM-Powered Frame Description

**What:** For each search result, generate a natural-language description using a vision-language model (LLaVA, GPT-4V via API, or Florence-2 locally).

**Why:** This completes the "RAG" part — retrieved frames are *augmented* with generated text. Users see "A busy intersection with 3 motorcycles, a bus, and a pedestrian crossing" instead of just a raw JPEG.

**How:**
- Add a `src/describer.py` module wrapping a VLM.
- Call it on demand (not during indexing — too slow) for the top-K results.
- Display descriptions below each frame image.
- **Files affected:** `src/describer.py` (new), `app.py`.

**Effort:** L (4–8h depending on model choice)

---

### 9. User Authentication + Multi-Tenant

**What:** Add login and per-user video collections so the app can be shared.

**Why:** Currently a single-user local tool. Auth enables deployment.

**How:**
- Use `streamlit-authenticator` or integrate with an OAuth proxy.
- Prefix ChromaDB collection names with user ID.
- **Files affected:** `app.py`, `src/vector_db.py`.

**Effort:** L (4–6h)

---

### 10. Dark Mode / Theme Toggle

**What:** Add a Streamlit theme toggle for dark/light mode.

**Why:** Surveillance operators often work in dimly lit rooms.

**How:**
- Use Streamlit's `.streamlit/config.toml` with `[theme]` settings.
- Add a sidebar toggle that writes to `st.session_state` and applies custom CSS.
- **Files affected:** `app.py` (CSS section), `.streamlit/config.toml` (new).

**Effort:** S (1h)
