import logging
import os
import glob
from src.video_processor import VideoProcessor
from src.embedder import FrameEmbedder
from src.vector_db import VideoSearchDB

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger(__name__)

def initialize_folders():
    """Creates the necessary folder structure."""
    folders = [
        os.path.join("data", "videos"),
        os.path.join("data", "frames"),
        "src"
    ]
    
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        logger.info("Verified folder: %s", folder)

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
        logger.warning("No videos found in %s. Please add a video file to test the processor.", video_folder)
        return

    video_path = video_files[0]
    logger.info("Processing video: %s", video_path)
    
    output_folder = os.path.join("data", "frames", os.path.splitext(os.path.basename(video_path))[0])
    
    # 3. Run Processor
    processor = VideoProcessor()
    
    logger.info("Extracting frames...")
    try:
        metadata = processor.extract_frames(video_path, output_folder, interval=1)
        
        # 4. Log results
        logger.info("Successfully extracted %d frames.", len(metadata))
        logger.info("Frames saved to: %s", output_folder)
        if metadata:
            logger.info("Sample metadata: %s", metadata[0])
        
        # 5. Generate Embeddings (Phase 2)
        logger.info("--- Phase 2: Generating Embeddings ---")
        
        # Use metadata to get paths to ensure alignment between embeddings and metadata
        if not metadata:
            logger.warning("No frames found to embed.")
            return

        image_paths = [m['frame_path'] for m in metadata]

        embedder = FrameEmbedder()
        embeddings, valid_paths = embedder.encode_images(image_paths)
        
        if embeddings.shape[0] == 0:
            logger.error("No frames could be embedded. Aborting.")
            return

        # Rebuild metadata aligned to valid_paths (preserves row order)
        meta_by_path = {m['frame_path']: m for m in metadata}
        metadata = [meta_by_path[p] for p in valid_paths if p in meta_by_path]
        assert len(embeddings) == len(metadata), (
            f"Alignment check failed: {len(embeddings)} embeddings vs {len(metadata)} metadata"
        )
        
        logger.info("Generated embeddings with shape: %s", embeddings.shape)
        
        # 6. Store in Vector DB (Phase 3)
        logger.info("--- Phase 3: Storing in Vector DB ---")
        db = VideoSearchDB()
        db.add_frames(embeddings, metadata)
        
        # 7. Sanity Check Search
        logger.info("--- Sanity Check Search ---")
        query_text = "traffic congestion"  # Change this to something relevant to your video
        logger.info("Query: '%s'", query_text)
        
        query_embedding = embedder.encode_text(query_text)
        results = db.search(query_embedding, k=3)
        
        for i, res in enumerate(results):
            logger.info(
                "Result %d: Timestamp=%.2fs, Score=%.4f, Path=%s",
                i + 1, res['timestamp'], res['score'], res['path'],
            )

    except Exception as e:
        logger.error("An error occurred: %s", e, exc_info=True)

if __name__ == "__main__":
    main()
