from vector_db import qdrant_vectordb
from .face_processing import FaceTracker
from .realtime_tracking import RT_Tracking
import os
from dotenv import load_dotenv

load_dotenv()

embedding_model = os.getenv('EMBEDDING_MODEL')
# Init face_tracker
face_tracker = FaceTracker(qdrant_vectordb, embedding_model, threshold=0.7)
