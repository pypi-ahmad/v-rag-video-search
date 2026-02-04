import chromadb
import os
import numpy as np
from typing import List, Dict, Any

class VideoSearchDB:
    def __init__(self, collection_name: str = "video_frames"):
        """
        Initializes a persistent ChromaDB client.
        """
        # Create storage folder in the current working directory
        db_path = os.path.join(os.getcwd(), "video_db_storage")
        if not os.path.exists(db_path):
            os.makedirs(db_path, exist_ok=True)
            
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(name=collection_name)
        print(f"Connected to ChromaDB at {db_path}, collection: '{collection_name}'")

    def add_frames(self, embeddings: np.ndarray, metadata: List[Dict[str, Any]]):
        """
        Adds embeddings and metadata to the ChromaDB collection.
        """
        if len(embeddings) != len(metadata):
            raise ValueError(f"Mismatch: {len(embeddings)} embeddings vs {len(metadata)} metadata items.")
        
        # Use filename as unique ID
        ids = [os.path.basename(m['frame_path']) for m in metadata]
        
        # Convert numpy array to list for ChromaDB
        embeddings_list = embeddings.tolist()
        
        self.collection.add(
            embeddings=embeddings_list,
            metadatas=metadata,
            ids=ids
        )
        print(f"Added {len(embeddings)} frames to the database.")

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
