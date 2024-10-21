from . import QdrantConnection  # Import the QdrantConnection class from the __init__.py file
from qdrant_client import models


class QdrantVectorDB:
    """
    This class provides vector search and collection management functions for Qdrant.
    """

    def __init__(self, qdrant_connection: QdrantConnection):
        # Get the Qdrant client instance from the provided QdrantConnection
        self._client = qdrant_connection.get_client()

    def create_collection(self, collection_name: str, vector_size: int = 512):
        """
        Creates a new collection in the Qdrant vector database with the specified name and vector size.
        If the collection already exists, it will print an error message.
        """
        try:
            self._client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=vector_size,  # Size of the vectors (e.g., 512 dimensions for Facenet512)
                    distance=models.Distance.COSINE,  # Use cosine distance for vector similarity
                ),
            )
            print(f"Collection '{collection_name}' created successfully.")
        except ValueError:
            print(f"Collection '{collection_name}' already exists.")

    def search_vector(self, collection_name: str, query_embedding: list, limit: int = 1):
        """
        Searches for the closest vectors in the specified collection based on the provided query embedding.
        """
        try:
            result = self._client.search(
                collection_name=collection_name,
                query_vector=query_embedding,
                limit=limit  # Return the top 'limit' results (default is 1)
            )
            return result
        except Exception as e:
            raise RuntimeError(f"Error during vector search: {e}")

    def delete_collection(self, collection_name: str):
        """
        Deletes the specified collection from the Qdrant vector database.
        """
        try:
            self._client.delete_collection(collection_name)
            print(f"Collection '{collection_name}' deleted successfully.")
        except Exception as e:
            raise RuntimeError(f"Error while deleting collection: {e}")
