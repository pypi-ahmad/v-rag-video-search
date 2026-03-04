# V-RAG — Quick Wins (Patch Suggestions)

> These are concrete, copy-paste-ready code changes for the highest-priority issues. Each one is small, safe, and independently shippable.

---

## QW-1: Sanitize uploaded filename (P0 — Security) ✅ DONE

**Implemented in:** `app.py:L65` — `safe_name = pathlib.Path(uploaded_file.name).name`

---

## QW-2: Fix DB path to be `__file__`-relative (P0 — Reliability) ✅ DONE

**Implemented in:** `src/vector_db.py:L14,L22` — `_PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent`; `db_path = str(_PROJECT_ROOT / "video_db_storage")`

---

## QW-3: Use `upsert()` instead of `add()` (P1 — Correctness) ✅ DONE

**Implemented in:** `src/vector_db.py:L52` — `self.collection.upsert(...)`

---

## QW-4: Fix embedding/metadata alignment (P0 — Correctness) ✅ DONE

**Implemented in:**
- `src/embedder.py:L32–L85` — `encode_images()` returns `Tuple[np.ndarray, List[str]]`; empty return is `np.empty((0, 512), dtype=np.float32)`
- `app.py:L108–L113` — order-preserving `meta_by_path` dict rebuild
- `main.py:L68–L72` — same pattern
- `src/vector_db.py:L34–L41` — empty-embeddings guard + `ValueError` on mismatch

---

## QW-5: Clean up temp files (P1 — Resource Leak) ✅ DONE

**Implemented in:**
- **Uploaded video cleanup:** `app.py:L155–L160` — `try/finally` with `os.remove(video_path)` after pipeline
- **Query image cleanup:** `app.py:L199–L206` — `try/finally` with `os.remove(temp_query_path)` after embedding

---

## QW-6: Fix deprecated `st.image` parameter (P1 — Deprecation) ✅ DONE

**Implemented in:** `app.py:L224` — `st.image(res['path'], use_container_width=True)`

---

## QW-7: Remove unused imports + dead variables (P2 — Lint) ✅ DONE

**Implemented in:**
- `src/embedder.py:L5` — `Union` and `os` removed; imports are now `List, Tuple`
- `src/embedder.py` — dead `total_batches` variable removed
- `src/video_processor.py:L49` — dead `saved_count` variable removed

---

## QW-8: Delete commented-out code (P2 — Dead Code) ✅ DONE

**Implemented in:** `app.py` — commented-out DB reset lines and camera image display line removed.

---

## TODO Comments to Add

These should be inserted directly in the source as reminders for future work:

```python
# app.py:L76 — above process_video_pipeline's extract call:
# TODO: Run extraction + embedding in a background thread to avoid blocking Streamlit UI

# src/vector_db.py:L18 — above get_or_create_collection:
# TODO: Explicitly set distance metric: metadata={"hnsw:space": "cosine"} or "l2"

# src/embedder.py:L10 — in __init__:
# TODO: Add normalize_embeddings=True to encode() calls for consistent distance behavior

# requirements.txt:L1 — at top:
# TODO: Pin all dependency versions for reproducible builds
```
