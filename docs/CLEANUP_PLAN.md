# V-RAG: Legacy & Cleanup Report

---

## 1. Legacy / Dead Code

| Candidate | Status | Notes |
|---|---|---|
| `main.py` | **Open** | Duplicates pipeline in `app.py`; hardcoded search query (`main.py:L92`). Keep as dev scaffold or move to `scripts/`. |
| `src/__pycache__/` | ✅ Git-ignored | `.gitignore` covers `__pycache__/` and `*.py[cod]` |
| Commented-out code in `app.py` | ✅ Deleted | PR1 |
| Dead `saved_count` in `video_processor.py` | ✅ Deleted | PR1 |
| Unused imports in `embedder.py` | ✅ Deleted | PR2 |

---

## 2. Completed Fixes

| Fix | Evidence | PR |
|---|---|---|
| Embedding/metadata alignment | `embedder.py:L31–L87`, `app.py:L112–L118` | PR2 |
| Path traversal sanitization | `app.py:L67` | PR2 |
| DB path stability (`__file__`-relative) | `vector_db.py:L11,L21` | PR2 |
| Dedup guard (`upsert`) | `vector_db.py:L50` | PR2 |
| Temp file cleanup | `app.py:L145–L148`, `app.py:L190–L193` | PR3 |
| Deprecated `st.image` param | `app.py:L224` | PR3 |
| Structured logging (all modules) | `app.py:L11`, `main.py:L8`, all `src/*.py` | PR4 |
| Stable temp paths (`__file__`-relative) | `app.py:L60–L62`, `app.py:L182` | PR5 |

---

## 3. Remaining Work

| Task | Priority | Effort |
|---|---|---|
| Pin dependency versions | P1 | S |
| Add tests + CI | P1 | L |
| Extract magic numbers to config | P2 | S |
| Delete/move `main.py` | P2 | S |

See [audit/ROADMAP.md](audit/ROADMAP.md) for the full phased plan.
