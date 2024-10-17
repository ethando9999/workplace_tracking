from qdrant_client import QdrantClient, models

# Create Qdrant Client (in-memory database for this example)
qdrant_client = QdrantClient(path="./vector_db")

# Create collections for Staff and Zone tables in Qdrant
try:
    qdrant_client.create_collection(
        collection_name="staff_collection",
        vectors_config=models.VectorParams(
            size=512,  # Facenet512 typically outputs 512-dimensional vectors
            distance=models.Distance.COSINE,
        ),
    )
except ValueError as e:
    print("Collection staff_collection already exists")
