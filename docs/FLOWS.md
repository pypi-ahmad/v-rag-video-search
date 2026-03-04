# V-RAG: Runtime Flows

> All flow steps are backed by evidence (file:line).

---

## 1. Ingestion Pipeline Flow

**Triggered by:** User clicks "🚀 Process & Index Video" after uploading a file.

**Evidence:** `app.py:L115–L120` (button), `app.py:L60–L104` (pipeline function)

### Sequence Diagram

```mermaid
sequenceDiagram
    actor User
    participant UI as Streamlit UI (app.py)
    participant VP as VideoProcessor (video_processor.py)
    participant FE as FrameEmbedder (embedder.py)
    participant DB as VideoSearchDB (vector_db.py)
    participant FS as Filesystem (data/frames/)
    participant CDB as ChromaDB (video_db_storage/)

    User->>UI: Upload video file (MP4/MOV/AVI)
    UI->>FS: save_uploaded_file() → temp_uploads/<name> [app.py:L49]
    UI->>UI: process_video_pipeline(video_path) [app.py:L62]

    Note over UI,FS: Step 1 — Frame Extraction
    UI->>FS: shutil.rmtree(output_folder) [app.py:L74]
    UI->>VP: extract_frames(video_path, output_folder, interval=1) [app.py:L76]
    VP->>VP: cv2.VideoCapture(video_path) [video_processor.py:L22]
    loop Every fps*interval frames
        VP->>FS: cv2.imwrite(frame_<ts_ms>.jpg) [video_processor.py:L62]
    end
    VP-->>UI: metadata List[{'frame_path', 'timestamp'}] [video_processor.py:L66]
    UI->>UI: progress_bar.progress(30) [app.py:L78]

    Note over UI,FE: Step 2 — Embedding Generation
    UI->>FE: encode_images(image_paths, batch_size=32|4) [app.py:L90]
    loop Per batch of 32 (GPU) or 4 (CPU) images
        FE->>FS: Image.open(path) [embedder.py:L44]
        FE->>FE: model.encode(batch_images) [embedder.py:L54]
    end
    FE-->>UI: np.ndarray shape (N, 512) [embedder.py:L72]
    UI->>UI: progress_bar.progress(70) [app.py:L92]

    Note over UI,DB: Step 3 — Indexing
    UI->>DB: add_frames(embeddings, metadata) [app.py:L96]
    DB->>CDB: collection.add(embeddings, metadatas, ids) [vector_db.py:L32]
    DB-->>UI: (void)
    UI->>UI: progress_bar.progress(100) [app.py:L98]
    UI-->>User: ✅ "Ready! Processed N frames."
```

---

## 2. Text Search Flow

**Triggered by:** User types a query and clicks "Search Text".

**Evidence:** `app.py:L146–L148`, `app.py:L163–L217`

### Sequence Diagram

```mermaid
sequenceDiagram
    actor User
    participant UI as Streamlit UI (app.py)
    participant FE as FrameEmbedder (embedder.py)
    participant DB as VideoSearchDB (vector_db.py)
    participant CDB as ChromaDB (video_db_storage/)
    participant FS as Filesystem (data/frames/)

    User->>UI: Type query text, click "Search Text" [app.py:L146]
    UI->>UI: perform_search(query, k, threshold, mode="text") [app.py:L148]

    Note over UI,FE: Step 1 — Embed Query
    UI->>FE: encode_text(query_text) [app.py:L168]
    FE->>FE: model.encode(text, convert_to_numpy=True) [embedder.py:L82]
    FE-->>UI: np.ndarray shape (512,)

    Note over UI,CDB: Step 2 — ANN Search
    UI->>DB: search(query_emb, k=num_results) [app.py:L171]
    DB->>CDB: collection.query(query_embeddings=[...], n_results=k) [vector_db.py:L43]
    CDB-->>DB: {metadatas, distances}
    DB-->>UI: List[{'path', 'timestamp', 'score'}] [vector_db.py:L52]

    Note over UI,FS: Step 3 — Filter + Display
    UI->>UI: Filter scores <= threshold [app.py:L181]
    loop Per result (3 cols/row)
        UI->>FS: os.path.exists(res['path']) [app.py:L191]
        UI-->>User: st.image() + timestamp + confidence [app.py:L192]
    end
```

---

## 3. Image/Camera Search Flow

**Triggered by:** User takes a photo via webcam and clicks "Search Image".

**Evidence:** `app.py:L152–L160`, `app.py:L163–L217`

### Sequence Diagram

```mermaid
sequenceDiagram
    actor User
    participant UI as Streamlit UI (app.py)
    participant FE as FrameEmbedder (embedder.py)
    participant DB as VideoSearchDB (vector_db.py)
    participant FS as Filesystem

    User->>UI: Take photo via st.camera_input [app.py:L153]
    User->>UI: Click "Search Image" [app.py:L156]
    UI->>UI: PIL.Image.open(img_file_buffer) [app.py:L159]
    UI->>UI: perform_search(image, k, threshold, mode="image") [app.py:L160]

    Note over UI,FS: Step 1 — Save Temp Image
    UI->>FS: image.save("temp_query.jpg") [app.py:L171]

    Note over UI,FE: Step 2 — Embed Query Image
    UI->>FE: encode_images(["temp_query.jpg"], batch_size=1) [app.py:L174]
    FE->>FS: Image.open("temp_query.jpg") [embedder.py:L44]
    FE->>FE: model.encode([image]) [embedder.py:L54]
    FE-->>UI: np.ndarray[0] shape (512,) [app.py:L174]

    Note over UI,DB: Step 3 — ANN Search + Display
    UI->>DB: search(query_emb, k) [app.py:L177 via raw_results]
    DB-->>UI: List[{'path', 'timestamp', 'score'}]
    UI->>UI: Filter + render grid (same as text search)
    UI-->>User: Frame results with timestamps/scores
```

---

## 4. Data Flow Diagram (Ingest → Transform → Persist → Serve)

```mermaid
flowchart TD
    RAW["Raw Video\n(temp_uploads/ or data/videos/)"]
    
    subgraph EXTRACT["Extract Phase"]
        E1["cv2.VideoCapture\nDecode video stream"]
        E2["Sample frame every fps×interval\nbased on CAP_PROP_POS_MSEC"]
        E3["Resize to max 640px height\nInterpolation: INTER_AREA"]
        E4["cv2.imwrite → data/frames/<name>/frame_<ms>.jpg"]
    end

    subgraph EMBED["Embed Phase"]
        EM1["Batch image paths (32 GPU / 4 CPU)"]
        EM2["PIL.Image.open per path"]
        EM3["SentenceTransformer CLIP ViT-B-32\nmodel.encode(batch)"]
        EM4["np.ndarray (N, 512) float32"]
    end

    subgraph INDEX["Index Phase"]
        I1["IDs = [basename(frame_path)]"]
        I2["chromadb.collection.add(\n  embeddings, metadatas, ids\n)"]
        I3["Persisted to video_db_storage/\nchroma.sqlite3 + segment files"]
    end

    subgraph SERVE["Serve Phase (Query)"]
        S1["Text or Image query"]
        S2["encode_text() or encode_images()\n→ (512,) vector"]
        S3["collection.query(query_embeddings, n_results=k)"]
        S4["Filter: score <= threshold"]
        S5["Render: st.image + timestamp + confidence"]
    end

    RAW --> E1
    E1 --> E2
    E2 --> E3
    E3 --> E4
    E4 --> EM1
    EM1 --> EM2
    EM2 --> EM3
    EM3 --> EM4
    EM4 --> I1
    I1 --> I2
    I2 --> I3
    I3 --> S3
    S1 --> S2
    S2 --> S3
    S3 --> S4
    S4 --> S5
```

---

## 5. Score / Confidence Interpretation

The `interpret_score()` function (`app.py:L41–L44`) maps L2 distance to confidence labels:

| Score (L2 Distance) | Label | Color |
|---|---|---|
| < 135 | 🔥 High Confidence | green |
| 135–144 | ✅ Medium Confidence | orange |
| ≥ 145 | ⚠️ Low Confidence | red |

**Default threshold slider:** 160.0 — results with score > 160 are filtered out — `app.py:L129`

> **Note:** These thresholds are empirically tuned for CLIP ViT-B-32 L2 distance. They are not mathematically derived and should be re-calibrated per domain.
