import chromadb
from sentence_transformers import SentenceTransformer
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from backend.config import EMBED_MODEL, CHROMA_COLLECTION

client = chromadb.PersistentClient(path="./chroma_data")
embed_model = SentenceTransformer(EMBED_MODEL)

def retrieve(query: str, n_results: int = 5) -> list:
    collection = client.get_collection(CHROMA_COLLECTION)
    query_embedding = embed_model.encode(query).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
    return results["documents"][0]