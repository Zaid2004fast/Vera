from backend.rag.knowledge_base import load_knowledge_base

print("Loading knowledge base into ChromaDB...")
print("(First run downloads the embedding model — takes 1-2 mins)\n")
load_knowledge_base()