# utils/face_recognition.py
from deepface import DeepFace
import numpy as np
import base64
import cv2

# Generate embedding from an image file or numpy array
def generate_face_embedding(image):
    """
    Takes an image (numpy array or path) and returns a serialized embedding string.
    """
    try:
        embedding_result = DeepFace.represent(image, model_name="Facenet")[0]["embedding"]
        embedding_array = np.array(embedding_result, dtype=np.float32)
        return base64.b64encode(embedding_array.tobytes()).decode("utf-8")
    except Exception as e:
        raise ValueError(f"Embedding generation failed: {e}")

# Compare face embedding with stored embedding
def verify_face(image, stored_embedding_str, threshold=0.4):
    """
    Compares an image against stored embedding.
    Returns True if match score is within threshold.
    """
    try:
        stored_embedding = np.frombuffer(base64.b64decode(stored_embedding_str), dtype=np.float32)
        current_embedding_result = DeepFace.represent(image, model_name="Facenet")[0]["embedding"]
        current_embedding = np.array(current_embedding_result, dtype=np.float32)

        # Cosine similarity
        similarity = np.dot(stored_embedding, current_embedding) / (
            np.linalg.norm(stored_embedding) * np.linalg.norm(current_embedding)
        )

        # DeepFace returns cosine similarity; higher is more similar
        return similarity > (1 - threshold), similarity
    except Exception as e:
        raise ValueError(f"Face verification failed: {e}")