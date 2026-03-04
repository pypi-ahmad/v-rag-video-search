# V-RAG: Runtime Flows

> All steps backed by `file:line` evidence.

---

## 1. Ingestion (Upload → Index)

```mermaid
sequenceDiagram
    actor User
    participant UI as Streamlit (app.py)
    participant VP as VideoProcessor
    participant FE as FrameEmbedder
    participant DB as VideoSearchDB
    participant FS as Filesystem

    User->>UI: Upload video + click Process
    UI->>FS: save_uploaded_file() → temp_uploads/<name> [L56–L73]
    UI->>VP: extract_frames(video, output, interval=1) [L97]
    VP->>FS: cv2.imwrite → data/frames/<name>/*.jpg
    VP-->>UI: metadata list
    UI->>FE: encode_images(paths, batch_size) [L109]
    FE-->>UI: (ndarray, valid_paths) [embedder.py:L85]
    UI->>UI: rebuild metadata from valid_paths [L112–L118]
    UI->>DB: add_frames(embeddings, metadata) [L124]
    DB->>DB: upsert to ChromaDB [vector_db.py:L50]
    UI-->>User: ✅ Ready
    UI->>FS: os.remove(video_path) [L145–L148]
```

---

## 2. Text Search

```mermaid
sequenceDiagram
    actor User
    participant UI as Streamlit (app.py)
    participant FE as FrameEmbedder
    participant DB as VideoSearchDB

    User->>UI: Type query + click Search [L160]
    UI->>FE: encode_text(query) [L176]
    FE-->>UI: ndarray (512,)
    UI->>DB: search(emb, k) [L196]
    DB-->>UI: List[{path, timestamp, score}]
    UI->>UI: filter score ≤ threshold [L200]
    UI-->>User: Frame grid + timestamps + confidence
```

---

## 3. Camera Search

```mermaid
sequenceDiagram
    actor User
    participant UI as Streamlit (app.py)
    participant FE as FrameEmbedder
    participant DB as VideoSearchDB

    User->>UI: Take photo [L164]
    UI->>UI: save temp_query.jpg (__file__-relative) [L182]
    UI->>FE: encode_images(["temp_query.jpg"]) [L184]
    FE-->>UI: ndarray (1,512)
    UI->>UI: os.remove(temp_query.jpg) [L190–L193]
    UI->>DB: search(emb, k) [L196]
    DB-->>UI: results
    UI-->>User: Frame grid
```

---

## 4. Score Interpretation

`interpret_score()` — `app.py:L49–L51`:

| Score (L2) | Label | Color |
|---|---|---|
| < 135 | 🔥 High Confidence | green |
| 135–144 | ✅ Medium Confidence | orange |
| ≥ 145 | ⚠️ Low Confidence | red |
