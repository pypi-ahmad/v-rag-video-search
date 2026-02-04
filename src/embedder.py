import torch
from sentence_transformers import SentenceTransformer
from PIL import Image
from typing import List, Union
import numpy as np
from tqdm import tqdm
import os

class FrameEmbedder:
    def __init__(self, model_name: str = 'clip-ViT-B-32'):
        """
        Initializes the FrameEmbedder with a specific CLIP model.
        Detects if GPU is available and moves the model to the appropriate device.
        """
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"Initializing FrameEmbedder...")
        print(f"Device detected: {self.device}")
        
        try:
            self.model = SentenceTransformer(model_name, device=self.device)
            print(f"Model '{model_name}' loaded successfully.")
        except Exception as e:
            print(f"Error loading model '{model_name}': {e}")
            raise

    def encode_images(self, image_paths: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Encodes a list of images into embeddings.
        Processes images in batches to avoid memory issues.
        """
        all_embeddings = []
        
        # Calculate total batches for progress bar
        total_batches = (len(image_paths) + batch_size - 1) // batch_size
        
        print(f"Starting embedding generation for {len(image_paths)} images...")
        
        for i in tqdm(range(0, len(image_paths), batch_size), desc="Encoding Batches", unit="batch"):
            batch_paths = image_paths[i : i + batch_size]
            batch_images = []
            valid_indices = []
            
            # Load images for the current batch
            for idx, path in enumerate(batch_paths):
                try:
                    # Open image and force loading to ensure file handle is managed
                    img = Image.open(path)
                    img.load() 
                    batch_images.append(img)
                    valid_indices.append(idx)
                except Exception as e:
                    print(f"\nError loading image {path}: {e}")

            if batch_images:
                try:
                    # Encode the batch
                    batch_emb = self.model.encode(
                        batch_images, 
                        batch_size=len(batch_images), 
                        show_progress_bar=False, 
                        convert_to_numpy=True
                    )
                    all_embeddings.append(batch_emb)
                except Exception as e:
                    print(f"\nError encoding batch starting at index {i}: {e}")
                finally:
                    # Explicitly close images
                    for img in batch_images:
                        img.close()
        
        if all_embeddings:
            return np.vstack(all_embeddings)
        else:
            return np.array([])

    def encode_text(self, text: str) -> np.ndarray:
        """
        Encodes a text query into an embedding.
        """
        return self.model.encode(text, convert_to_numpy=True)
