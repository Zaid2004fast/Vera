import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from backend.config import GROQ_API_KEY, GROQ_MODEL
from backend.rag.retriever import retrieve
from backend.graph.state import VERAState

llm = ChatGroq(api_key=GROQ_API_KEY, model=GROQ_MODEL, temperature=0.1)

PROMPT = """You are a CS interview expert helping a university student prepare.

Use the context below to answer the question accurately and clearly.
If the context does not fully cover the question, use your own knowledge but stay precise.

Context:
{context}

Question: {query}

Give a clear, technically accurate answer. Use examples where helpful.
Be concise — 3 to 6 sentences is ideal unless the topic genuinely needs more."""

def response_node(state: VERAState) -> VERAState:
    chunks = retrieve(state["query"])
    context = "\n\n---\n\n".join(chunks)
    prompt = PROMPT.format(context=context, query=state["query"])
    result = llm.invoke([HumanMessage(content=prompt)])
    return {
        **state,
        "retrieved_chunks": chunks,
        "initial_response": result.content,
    }