# V-RAG — Quick Wins

> All items below are either completed or copy-paste-ready for remaining work.

---

## QW-1: Sanitize uploaded filename ✅ DONE

`app.py:L67` — `safe_name = pathlib.Path(uploaded_file.name).name`

## QW-2: Fix DB path to `__file__`-relative ✅ DONE

`src/vector_db.py:L11,L21` — `_PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent`

## QW-3: Use `upsert()` instead of `add()` ✅ DONE

`src/vector_db.py:L50` — `self.collection.upsert(…)`

## QW-4: Fix embedding/metadata alignment ✅ DONE

`src/embedder.py:L31–L87` returns `Tuple[np.ndarray, List[str]]`. Callers use `meta_by_path` dict (`app.py:L112–L118`, `main.py:L76–L80`).

## QW-5: Clean up temp files ✅ DONE

`app.py:L145–L148` — uploaded video deleted in `try/finally`.
`app.py:L190–L193` — query image deleted in `try/finally`.

## QW-6: Fix deprecated `st.image` parameter ✅ DONE

`app.py:L224` — `use_container_width=True`

## QW-7: Remove unused imports + dead variables ✅ DONE

`src/embedder.py:L5` — `Union` and `os` removed. Dead `total_batches` removed.
`src/video_processor.py` — Dead `saved_count` removed.

## QW-8: Delete commented-out code ✅ DONE

Dead comment blocks removed from `app.py`.

## QW-9: Replace all `print()` with `logging` ✅ DONE

`src/embedder.py:L19–L27`, `src/video_processor.py:L87`, `main.py` — all converted.

## QW-10: Stable temp paths ✅ DONE

`app.py:L60–L62` — `temp_uploads/` now `__file__`-relative.
`app.py:L182` — `temp_query.jpg` now `__file__`-relative.

---

## Remaining TODOs

```python
# requirements.txt — Pin all dependency versions
# TODO: pip freeze > requirements.txt

# app.py:L52–L54 — Extract magic numbers to constants or config
# SCORE_HIGH, SCORE_MED = 135, 145

# src/vector_db.py:L25 — Explicitly set distance metric
# metadata={"hnsw:space": "cosine"}

# src/embedder.py:L73 — Consider normalize_embeddings=True
# model.encode(…, normalize_embeddings=True)
```
