from .vector_db import QdrantVectorDB
import os
from dotenv import load_dotenv

load_dotenv()

vector_size = os.getenv('VECTOR_SIZE')
print(vector_size)
qdrant_vectordb = QdrantVectorDB(path="./vector_db", vector_size=vector_size)
qdrant_vectordb.create_vector_collection("staff_collection")