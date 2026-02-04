import streamlit as st
import os
import torch
from PIL import Image
import cv2
import time
import shutil

# Import our backend modules
from src.embedder import FrameEmbedder
from src.vector_db import VideoSearchDB
from src.video_processor import VideoProcessor

# --- Page Config ---
st.set_page_config(
    page_title="V-RAG Pro | Semantic Video Search", 
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS ---
st.markdown("""
<style>
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; }
    .stProgress .st-bo { background-color: #FF4B4B; }
</style>
""", unsafe_allow_html=True)

# --- Resource Caching ---
@st.cache_resource
def get_embedder():
    return FrameEmbedder()

@st.cache_resource
def get_db():
    return VideoSearchDB()

# --- Helper Functions ---
def format_timestamp(seconds):
    return f"{int(seconds // 60):02d}m {int(seconds % 60):02d}s"

def interpret_score(score):
    if score < 135: return "🔥 High Confidence", "green"
    elif score < 145: return "✅ Medium Confidence", "orange"
    else: return "⚠️ Low Confidence", "red"

def save_uploaded_file(uploaded_file):
    """Saves uploaded video to a temp path."""
    try:
        # Create temp dir
        if not os.path.exists("temp_uploads"):
            os.makedirs("temp_uploads")
        
        file_path = os.path.join("temp_uploads", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    except Exception as e:
        st.error(f"Error saving file: {e}")
        return None

def process_video_pipeline(video_path):
    """Runs the full Extraction -> Embedding -> Indexing pipeline."""
    
    # 1. Setup
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    output_folder = os.path.join("data", "frames", video_name)
    
    # Progress Containers
    status_text = st.empty()
    progress_bar = st.progress(0)
    
    # 2. Extract Frames
    status_text.text(f"🎬 Extracting frames from {video_name}...")
    processor = VideoProcessor()
    # We clear the output folder first to avoid mixing old data
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
        
    metadata = processor.extract_frames(video_path, output_folder, interval=1)
    progress_bar.progress(30)
    
    if not metadata:
        st.error("Frame extraction failed.")
        return False

    # 3. Generate Embeddings
    status_text.text(f"🧠 Generating AI Embeddings for {len(metadata)} frames...")
    embedder = get_embedder()
    
    # Get paths
    image_paths = [m['frame_path'] for m in metadata]
    
    # Determine batch size based on GPU/CPU
    batch_size = 32 if torch.cuda.is_available() else 4
    
    # Embed
    embeddings = embedder.encode_images(image_paths, batch_size=batch_size)
    progress_bar.progress(70)

    # 4. Index in DB
    status_text.text("💾 Saving to Vector Database...")
    db = get_db()
    # Optional: We could reset the DB here if we wanted a fresh start
    # db.client.delete_collection("video_frames") 
    # db.collection = db.client.create_collection("video_frames")
    
    db.add_frames(embeddings, metadata)
    progress_bar.progress(100)
    
    status_text.success(f"✅ Ready! Processed {len(metadata)} frames.")
    time.sleep(2)
    status_text.empty()
    progress_bar.empty()
    return True

# --- Main App ---
def main():
    # Sidebar: Data Management
    with st.sidebar:
        st.title("🎛️ Control Panel")
        
        st.subheader("1. Video Source")
        upload_option = st.radio("Choose Input:", ["Use Existing Data", "Upload New Video"])
        
        if upload_option == "Upload New Video":
            uploaded_file = st.file_uploader("Upload MP4/MOV", type=['mp4', 'mov', 'avi'])
            if uploaded_file is not None:
                if st.button("🚀 Process & Index Video", type="primary"):
                    with st.spinner("Initializing Pipeline..."):
                        video_path = save_uploaded_file(uploaded_file)
                        if video_path:
                            success = process_video_pipeline(video_path)
                            if success:
                                st.balloons()
        
        st.divider()
        st.subheader("2. Search Settings")
        num_results = st.slider("Max Results", 1, 20, 6)
        threshold = st.slider("Sensitivity Threshold", 100.0, 200.0, 160.0)

    # Main Area
    st.title("👁️ V-RAG Pro")
    st.caption(f"Visual Retrieval Augmented Generation • Device: {'GPU' if torch.cuda.is_available() else 'CPU'}")

    # Tabs for Text vs Visual Search
    tab1, tab2 = st.tabs(["📝 Text Search", "📸 Camera Search"])

    # --- TAB 1: TEXT SEARCH ---
    with tab1:
        query = st.text_input("Describe scene:", placeholder="e.g., 'red car turning left'")
        if query and st.button("Search Text"):
            perform_search(query, num_results, threshold, mode="text")

    # --- TAB 2: CAMERA SEARCH ---
    with tab2:
        st.info("Take a photo of an object (e.g., a car, a person) to find similar frames in the video.")
        img_file_buffer = st.camera_input("Take a picture")
        
        if img_file_buffer is not None:
            # Display the query image
            # st.image(img_file_buffer, caption="Your Query", width=200)
            if st.button("Search Image"):
                # Convert buffer to PIL Image
                image = Image.open(img_file_buffer)
                perform_search(image, num_results, threshold, mode="image")

def perform_search(query_input, k, threshold, mode="text"):
    """Handles search logic for both text and image queries."""
    try:
        embedder = get_embedder()
        db = get_db()
        
        with st.spinner(f"Searching by {mode}..."):
            # 1. Embed Query
            if mode == "text":
                query_emb = embedder.encode_text(query_input)
            else:
                # Image embedding (wrap in list because encode_images expects list)
                # Save temp image because our embedder expects paths (or we can modify embedder, 
                # but saving is safer for your current code structure)
                temp_query_path = "temp_query.jpg"
                query_input.save(temp_query_path)
                # We need to adapt embedder slightly or just load it here.
                # Since your `embedder.py` expects paths, let's use the path.
                # Actually, `sentence-transformers` handles PIL images directly mostly, 
                # but your wrapper `encode_images` expects paths. 
                # Let's rely on the path method you built.
                query_emb = embedder.encode_images([temp_query_path], batch_size=1)[0] # Take 1st item

            # 2. Search DB
            raw_results = db.search(query_emb, k=k)
            
            # 3. Filter & Display
            results = [res for res in raw_results if res['score'] <= threshold]
            
            if not results:
                st.warning("No matches found. Try adjusting the threshold.")
                return

            st.success(f"Found {len(results)} matches!")
            
            cols_per_row = 3
            for i in range(0, len(results), cols_per_row):
                batch = results[i:i+cols_per_row]
                cols = st.columns(len(batch))
                for idx, res in enumerate(batch):
                    with cols[idx]:
                        if os.path.exists(res['path']):
                            st.image(res['path'], width='stretch')
                            
                            # Info
                            time_str = format_timestamp(res['timestamp'])
                            conf, color = interpret_score(res['score'])
                            st.markdown(f"**{time_str}** | :{color}[{conf}]")
                            st.caption(f"Score: {res['score']:.2f}")
                        else:
                            st.error("Frame missing")

    except Exception as e:
        st.error(f"Search Error: {e}")

if __name__ == "__main__":
    main()