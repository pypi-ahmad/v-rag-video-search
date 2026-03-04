# V-RAG — Feature Ideas

> Ordered by value-to-effort ratio. Each idea includes affected files.

---

## Tier 1 — High Value, Moderate Effort

### 1. Video Timeline Scrubber

Show a clickable mini-timeline highlighting where matches cluster in the video. Use `st.video(…, start_time=ts)` for playback.

**Affected:** `app.py` (new section in `perform_search()`).
**Effort:** M (3–4h)

### 2. Multi-Video Index

Store `video_name` in metadata. Prefix IDs: `f"{video_name}__frame_{ts}.jpg"`. Add `where={"video_name": …}` filter.

**Affected:** `src/video_processor.py`, `src/vector_db.py`, `app.py`.
**Effort:** L (4–6h)

### 3. Batch Upload & Queue

`st.file_uploader(accept_multiple_files=True)` + session-state queue with per-video status.

**Affected:** `app.py`.
**Effort:** M (2–3h)

---

## Tier 2 — Valuable, Larger Effort

### 4. Temporal / Action Search

Sliding window of N=5 frames → averaged CLIP embedding → "scene" collection. Or VideoMAE / X-CLIP model.

**Affected:** `src/embedder.py` (new method), `src/video_processor.py`, `src/vector_db.py`.
**Effort:** XL (8–16h)

### 5. Object Detection + CLIP Hybrid (YOLO)

Run YOLOv8/YOLO-World per frame, CLIP-embed each crop. Enables "red truck" matching the specific object.

**Affected:** `src/detector.py` (new), `app.py`, `src/vector_db.py`.
**Effort:** XL (10–20h)

### 6. Live RTSP Stream Ingestion

`cv2.VideoCapture("rtsp://…")` in a background thread with ring buffer.

**Affected:** `src/video_processor.py` (new generator), `app.py`.
**Effort:** L (6–10h)

---

## Tier 3 — Nice to Have

### 7. Export / Report Generation

Export search results as PDF/CSV with timestamps, images, scores.

**Affected:** `app.py`.
**Effort:** M (2–3h)

### 8. LLM-Powered Frame Description

Use LLaVA/Florence-2 to generate captions for top-K results on demand.

**Affected:** `src/describer.py` (new), `app.py`.
**Effort:** L (4–8h)

### 9. User Authentication + Multi-Tenant

`streamlit-authenticator` or OAuth proxy. Per-user ChromaDB collections.

**Affected:** `app.py`, `src/vector_db.py`.
**Effort:** L (4–6h)

### 10. Dark Mode / Theme Toggle

`.streamlit/config.toml` with `[theme]` + sidebar toggle + custom CSS.

**Affected:** `app.py`, `.streamlit/config.toml` (new).
**Effort:** S (1h)
