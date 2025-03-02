from qdrant_client import QdrantClient

def query_collection(collection_name: str, query_text: str, limit: int = 3):
    """
    Search a Qdrant collection by text query
    
    Args:
        collection_name: Name of collection to search
        query_text: Text to search for
        limit: Maximum number of results to return
        
    Returns:
        Search results or None if error occurs
    """
    try:
        client = QdrantClient(host="localhost", port=6333)
        results = client.query(
            collection_name=collection_name,
            query_text=query_text,
            limit=limit
        )
        return results
    except Exception as e:
        print(f"Error querying collection: {e}")
        return None

def search_by_text_in_collection(collection_name: str, query):
    try:
        client = QdrantClient(host="localhost", port=6333)
        search_results = client.query(
            collection_name=collection_name,
            query_text=query, limit=3
            )
        print(f"Search results:", search_results)
        return search_results
    except Exception as e:
        print(f"Error searching collection: {e}")

print('List collections', search_by_text_in_collection('test', 'Đà Nẵng'))

# Delete existing collection if it exists
def delete_collection(collection_name: str):
    try:
        client = QdrantClient(host="localhost", port=6333)
        client.delete_collection(collection_name=collection_name)
    except Exception as e:
        print(f"Error deleting collection: {e}")


