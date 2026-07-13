import chromadb
from sentence_transformers import SentenceTransformer
from pathlib import Path
import hashlib
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from backend.config import EMBED_MODEL, CHROMA_COLLECTION

client = chromadb.PersistentClient(path="./chroma_data")
embed_model = SentenceTransformer(EMBED_MODEL)

def chunk_text(text: str, chunk_size: int = 150, overlap: int = 20) -> list:
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i : i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    return chunks

def load_knowledge_base(kb_dir: str = "data/knowledge_base"):
    collection = client.get_or_create_collection(
        name=CHROMA_COLLECTION,
        metadata={"hnsw:space": "cosine"}
    )

    kb_path = Path(kb_dir)
    if not kb_path.exists():
        print(f"ERROR: Directory not found: {kb_dir}")
        return

    total_chunks = 0
    for md_file in sorted(kb_path.glob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        chunks = chunk_text(text)
        topic = md_file.stem

        for i, chunk in enumerate(chunks):
            doc_id = hashlib.md5(f"{topic}-{i}-{chunk[:50]}".encode()).hexdigest()[:12]
            embedding = embed_model.encode(chunk).tolist()
            collection.upsert(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[chunk],
                metadatas=[{"topic": topic, "chunk_index": i}]
            )
        total_chunks += len(chunks)
        print(f"  Loaded: {md_file.name}  ({len(chunks)} chunks)")

    print(f"\n✓ Knowledge base ready — {total_chunks} total chunks in ChromaDB")

if __name__ == "__main__":
    load_knowledge_base()