import os
import glob
from src.video_processor import VideoProcessor
from src.embedder import FrameEmbedder
from src.vector_db import VideoSearchDB

def initialize_folders():
    """Creates the necessary folder structure."""
    folders = [
        os.path.join("data", "videos"),
        os.path.join("data", "frames"),
        "src"
    ]
    
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"Verified folder: {folder}")

def main():
    # 1. Initialize project structure
    initialize_folders()
    
    # 2. Look for sample video
    video_folder = os.path.join("data", "videos")
    video_files = glob.glob(os.path.join(video_folder, "*.mp4")) + \
                  glob.glob(os.path.join(video_folder, "*.avi")) + \
                  glob.glob(os.path.join(video_folder, "*.mov")) + \
                  glob.glob(os.path.join(video_folder, "*.mkv"))
    
    if not video_files:
        print(f"No videos found in {video_folder}. Please add a video file to test the processor.")
        # Create a dummy file to ensure folder exists in git/view if empty, strictly not needed but good for structure
        return

    video_path = video_files[0]
    print(f"Processing video: {video_path}")
    
    output_folder = os.path.join("data", "frames", os.path.splitext(os.path.basename(video_path))[0])
    
    # 3. Run Processor
    processor = VideoProcessor()
    
    print("Extracting frames...")
    try:
        metadata = processor.extract_frames(video_path, output_folder, interval=1)
        
        # 4. Print results
        print(f"Successfully extracted {len(metadata)} frames.")
        print(f"Frames saved to: {output_folder}")
        if metadata:
            print(f"Sample metadata: {metadata[0]}")
        
        # 5. Generate Embeddings (Phase 2)
        print("\n--- Phase 2: Generating Embeddings ---")
        
        # Use metadata to get paths to ensure alignment between embeddings and metadata
        if not metadata:
            print("No frames found to embed.")
            return

        image_paths = [m['frame_path'] for m in metadata]

        embedder = FrameEmbedder()
        embeddings, valid_paths = embedder.encode_images(image_paths)
        
        if embeddings.shape[0] == 0:
            print("ERROR: No frames could be embedded. Aborting.")
            return

        # Rebuild metadata aligned to valid_paths (preserves row order)
        meta_by_path = {m['frame_path']: m for m in metadata}
        metadata = [meta_by_path[p] for p in valid_paths if p in meta_by_path]
        assert len(embeddings) == len(metadata), (
            f"Alignment check failed: {len(embeddings)} embeddings vs {len(metadata)} metadata"
        )
        
        print(f"Generated embeddings with shape: {embeddings.shape}")
        
        # 6. Store in Vector DB (Phase 3)
        print("\n--- Phase 3: Storing in Vector DB ---")
        db = VideoSearchDB()
        db.add_frames(embeddings, metadata)
        
        # 7. Sanity Check Search
        print("\n--- Sanity Check Search ---")
        query_text = "traffic congestion"  # Change this to something relevant to your video
        print(f"Query: '{query_text}'")
        
        query_embedding = embedder.encode_text(query_text)
        results = db.search(query_embedding, k=3)
        
        for i, res in enumerate(results):
             print(f"Result {i+1}: Timestamp={res['timestamp']:.2f}s, Score={res['score']:.4f}, Path={res['path']}")
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
