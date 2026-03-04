# 🚦 V-RAG: Semantic Video Search Engine
> **Visual Retrieval Augmented Generation** for Traffic & Surveillance Analysis.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![AI](https://img.shields.io/badge/AI-CLIP%20%2B%20Vector%20Search-orange)
![Stack](https://img.shields.io/badge/Stack-Streamlit%20%7C%20ChromaDB%20%7C%20OpenCV-green)

## 📖 Overview
**V-RAG** is a multimodal AI system that allows users to search inside video files using natural language. Unlike traditional object detection (which just finds "car"), V-RAG understands semantic context (e.g., *"aggressive driving"*, *"red car turning left"*, or *"empty road at night"*).

It uses **OpenAI's CLIP model** to map video frames and text queries into a shared vector space, storing them in **ChromaDB** for millisecond-scale retrieval.

### 🌟 Key Features
* **🧠 Semantic Search:** Search for concepts, actions, and objects using plain English.
* **📸 Visual Query:** Use your webcam or an upload to find "similar looking frames" (Reverse Image Search).
* **⚡ RAG Pipeline:** Automated ingestion pipeline (Extract → Embed → Index).
* **🏎️ High Performance:** Optimized for GPU acceleration but runs smoothly on CPU.
* **🎛️ Interactive Dashboard:** Built with Streamlit for real-time analysis.

---

## 🛠️ Tech Stack
| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Embeddings** | `sentence-transformers` (CLIP ViT-B-32) | Converts images/text to 512-dim vectors. |
| **Vector DB** | `ChromaDB` | Stores vectors and enables similarity search. |
| **Vision** | `OpenCV` | Efficient video frame extraction and processing. |
| **Frontend** | `Streamlit` | Interactive UI for upload, search, and visualization. |
| **Backend** | `Python` | Core logic and orchestration. |

---

## ⚙️ Architecture
The system follows a standard **RAG (Retrieval Augmented Generation)** pattern adapted for Video:

1.  **Ingestion:**
    * Video is sliced into frames (e.g., 1 frame/sec).
    * Frames are resized to 640px for efficiency.
2.  **Indexing:**
    * **CLIP** encodes every frame into a vector.
    * Vectors + Metadata (Timestamp) are stored in **ChromaDB**.
3.  **Retrieval:**
    * User inputs Text or Image.
    * Input is converted to a vector.
    * DB calculates **Cosine Similarity** (or L2 Distance) to find the nearest frames.

---

## 🚀 Quick Start

### 1. Clone & Install
```bash
git clone https://github.com/pypi-ahmad/v-rag-video-search.git
cd v-rag-video-search

# Create virtual environment
python -m venv .venv
# Activate:
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the App

```bash
streamlit run app.py
```

### 3. Usage

1. Open the app in your browser (`http://localhost:8501`).
2. **Upload a Video** (Side Panel) or use the default data.
3. Click **"Process & Index"** to build the database.
4. Type a query (e.g., *"traffic jam"*) or take a photo to search!

---

## 📂 Project Structure

```text
V-RAG/
├── data/
│   ├── videos/          # Raw video files
│   └── frames/          # Extracted frames (auto-generated)
├── src/
│   ├── embedder.py      # CLIP model wrapper
│   ├── video_processor.py # OpenCV frame extraction
│   └── vector_db.py     # ChromaDB manager
├── video_db_storage/    # Persistent Vector Database
├── app.py               # Main Streamlit Dashboard
├── main.py              # CLI Driver (Optional)
└── requirements.txt     # Dependencies
```

## 🔮 Future Improvements

* **Temporal Search:** analyzing sequences of frames (using LSTMs or VideoMAE) to detect actions like "crash" or "u-turn".
* **Object Tracking:** Integrating YOLOv8 to track specific object IDs across frames.
* **Live Stream:** Adapting the pipeline for real-time RTSP streams.

---

**Author:** Ahmad Mujtaba
*Built as a Portfolio Project demonstrating Multimodal AI & Vector Search.*
