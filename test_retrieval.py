from backend.rag.retriever import retrieve

query = "What is the worst case time complexity of a BST?"
print(f"Query: {query}\n")
chunks = retrieve(query, n_results=3)
for i, chunk in enumerate(chunks, 1):
    print(f"--- Chunk {i} ---")
    print(chunk[:300])
    print()