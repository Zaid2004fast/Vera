import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from backend.config import GROQ_API_KEY, GROQ_MODEL
from backend.graph.state import VERAState

llm = ChatGroq(api_key=GROQ_API_KEY, model=GROQ_MODEL, temperature=0)

GUARD_PROMPT = """You are a classifier for a CS interview preparation chatbot.

Decide if the following question is related to computer science, software engineering,
programming, or technical interviews. Be generous — if it's even loosely related
to CS topics like data structures, algorithms, operating systems, databases,
networking, OOP, system design, coding, or software concepts, classify it as CS.

Question: {query}

Respond ONLY with valid JSON and nothing else:
{{"is_cs": true, "reason": "one sentence explanation"}}

Examples that ARE CS: "what is a binary tree", "explain TCP vs UDP",
"what is normalization in databases", "how does quicksort work",
"what is a race condition", "explain SOLID principles"

Examples that are NOT CS: "what is the capital of France",
"who is the president", "give me a recipe", "what do you think about politics",
"tell me a joke", "what is the weather today", "write me a poem" """

OFF_TOPIC_RESPONSE = """I'm VERA, a CS interview preparation assistant. I can only help with computer science topics such as:

- Data structures and algorithms
- Operating systems and memory management
- Databases and SQL
- Computer networks
- Object-oriented programming and design patterns
- System design concepts

Please ask me a CS-related question and I'll give you a verified, confidence-scored answer."""

def guard_node(state: VERAState) -> VERAState:
    prompt = GUARD_PROMPT.format(query=state["query"])
    result = llm.invoke([HumanMessage(content=prompt)])

    raw = result.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        parsed = json.loads(raw)
        is_cs = parsed.get("is_cs", True)
    except json.JSONDecodeError:
        is_cs = True  # if we can't parse, assume CS and let it through

    if not is_cs:
        return {
            **state,
            "is_cs_question":   False,
            "final_response":   OFF_TOPIC_RESPONSE,
            "confidence_score": 1.0,
            "in_review_queue":  False,
            "improvements_made": [],
        }

    return {**state, "is_cs_question": True}