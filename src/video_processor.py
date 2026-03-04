import cv2
import logging
import math
import os
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class VideoProcessor:
    def __init__(self):
        pass

    def extract_frames(self, video_path: str, output_folder: str, interval: int = 1) -> List[Dict[str, Any]]:
        """
        Extracts frames from a video at a specified interval.
        
        Args:
            video_path (str): Path to the input video file.
            output_folder (str): Directory where frames will be saved.
            interval (int): Interval in seconds to extract frames. Default is 1 second.
            
        Returns:
            List[Dict[str, Any]]: A list of metadata dictionaries containing 'frame_path' and 'timestamp'.
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        if not os.path.exists(output_folder):
            os.makedirs(output_folder, exist_ok=True)

        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise IOError(f"Cannot open video file: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            # Fallback if FPS is not correctly detected
            fps = 30.0
            
        frame_interval = math.ceil(fps * interval)
        if frame_interval < 1:
            frame_interval = 1

        metadata = []
        frame_count = 0

        try:
            while True:
                success, frame = cap.read()
                
                if not success:
                    break

                if frame_count % frame_interval == 0:
                    # Get timestamp in milliseconds
                    timestamp_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
                    
                    # If timestamp is 0 and we are further in, calculate it manually (some codecs fail)
                    if timestamp_ms == 0 and frame_count > 0:
                        timestamp_ms = (frame_count / fps) * 1000

                    # Resize frame
                    height, width = frame.shape[:2]
                    target_height = 640
                    
                    if height > target_height:
                        aspect_ratio = width / height
                        new_width = int(target_height * aspect_ratio)
                        frame_resized = cv2.resize(frame, (new_width, target_height), interpolation=cv2.INTER_AREA)
                    else:
                        frame_resized = frame

                    # Save frame
                    filename = f"frame_{int(timestamp_ms)}.jpg"
                    file_path = os.path.join(output_folder, filename)
                    cv2.imwrite(file_path, frame_resized)

                    metadata.append({
                        'frame_path': file_path,
                        'timestamp': timestamp_ms / 1000.0  # Convert to seconds for easier reading usually
                    })

                frame_count += 1

        except Exception as e:
            logger.error("Error processing video: %s", e, exc_info=True)
        finally:
            cap.release()
            
        return metadata
