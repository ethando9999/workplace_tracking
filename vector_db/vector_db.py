from qdrant_client import QdrantClient, models

class QdrantVectorDB(QdrantClient):
    def __init__(self, path="./vector_db", vector_size= 512):
        """
        Initialize the Qdrant client with the given path to the database.
        """
        self.vector_size = vector_size
        super().__init__(path=path)

    def create_vector_collection(self, collection_name, distance_metric=models.Distance.COSINE):
        """
        Creates a collection for storing vectors if it doesn't already exist.
        
        :param collection_name: Name of the collection to be created.
        :param vector_size: Size of the vector (typically 128 for FaceNet embeddings).
        :param distance_metric: The distance metric to use (default: COSINE).
        """
        try:
            super().create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=self.vector_size,
                    distance=distance_metric,
                ),
            )
            print(f"Collection '{collection_name}' created successfully.")
        except ValueError as e:
            print(f"Collection '{collection_name}' already exists.")

    def insert_vectors(self, collection_name, vectors, payload=None):
        """
        Inserts vectors into a specific collection.

        :param collection_name: Name of the collection where vectors will be inserted.
        :param vectors: List of vectors to insert.
        :param payload: Optional additional metadata associated with the vectors.
        """
        return super().upload_collection(
            collection_name=collection_name,
            vectors=vectors,
            payload=payload
        )
    
    def upsert_vector(self, collection_name, point_id, vector):
        """
        Update or insert a new point into the collection.

        If point with given ID already exists - it will be overwritten.

        :param collection_name: Name of the collection where vectors will be inserted.
        :param vectors: List of vectors to insert.
        :param payload: Optional additional metadata associated with the vectors.
        """
        return super().upsert(
            collection_name=collection_name,
            points=[
                models.PointStruct(
                    id=point_id,
                    vector=vector,  
                )
            ]
        )

    def search_vectors(self, collection_name, query_vector, top_k=5):
        """
        Search for the most similar vectors in the collection.
        
        :param collection_name: Name of the collection to search.
        :param query_vector: The query vector to search for.
        :param top_k: Number of top results to return.
        :return: List of search results.
        """
        search_result = super().search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=top_k,
        )
        return search_result
    
    def delete_vector(self, collection_name, point_id):
        """
        Delete a specific vector from a collection by point ID.
        
        :param collection_name: Name of the collection where the vector is stored.
        :param point_id: The ID of the vector to delete.
        """
        try:
            super().delete(
                collection_name=collection_name,
                points_selector=models.PointIdsList(points=[point_id])
            )
            print(f"Vector with point ID '{point_id}' deleted successfully from collection '{collection_name}'.")
        except Exception as e:
            print(f"Error deleting vector with point ID '{point_id}' from collection '{collection_name}': {e}")

    def delete_collection(self, collection_name):
        """
        Delete a specific collection.
        
        :param collection_name: Name of the collection to delete.
        """
        try:
            super().delete_collection(collection_name)
            print(f"Collection '{collection_name}' deleted successfully.")
        except ValueError as e:
            print(f"Collection '{collection_name}' does not exist.")


