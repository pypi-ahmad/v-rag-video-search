import logging
import pathlib

import chromadb
import numpy as np
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# Stable project root — two levels up from src/vector_db.py
_PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent

class VideoSearchDB:
    def __init__(self, collection_name: str = "video_frames"):
        """
        Initializes a persistent ChromaDB client.
        """
        # Stable path anchored to the project root (not CWD)
        db_path = str(_PROJECT_ROOT / "video_db_storage")
        pathlib.Path(db_path).mkdir(parents=True, exist_ok=True)
            
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(name=collection_name)
        logger.info("Connected to ChromaDB at %s, collection: '%s'", db_path, collection_name)

    def add_frames(self, embeddings: np.ndarray, metadata: List[Dict[str, Any]]):
        """
        Adds (or updates) embeddings and metadata in the ChromaDB collection.
        """
        if len(embeddings) == 0:
            logger.warning("add_frames called with 0 embeddings — skipping.")
            return

        if len(embeddings) != len(metadata):
            raise ValueError(
                f"embedding/metadata length mismatch: "
                f"{len(embeddings)} embeddings vs {len(metadata)} metadata items."
            )
        
        # Use filename as unique ID
        ids = [pathlib.Path(m['frame_path']).name for m in metadata]
        
        # Convert numpy array to list for ChromaDB
        embeddings_list = embeddings.tolist()
        
        self.collection.upsert(
            embeddings=embeddings_list,
            metadatas=metadata,
            ids=ids
        )
        logger.info("Upserted %d frames to the database.", len(embeddings))

    def search(self, query_embedding: np.ndarray, k: int = 5) -> List[Dict[str, Any]]:
        """
        Searches the database for the closest embeddings.
        """
        # Convert numpy array to list and wrap in list for query (batch of 1)
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=k
        )
        
        parsed_results = []
        if results['metadatas'] and results['distances']:
             # We only sent one query, so take the first list of results
             metas = results['metadatas'][0]
             dists = results['distances'][0]
             
             for meta, dist in zip(metas, dists):
                 parsed_results.append({
                     'path': meta['frame_path'],
                     'timestamp': meta['timestamp'],
                     'score': dist
                 })
                 
        return parsed_results
