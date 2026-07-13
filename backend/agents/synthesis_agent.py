import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from backend.config import GROQ_API_KEY, GROQ_MODEL, CONFIDENCE_THRESHOLD
from backend.graph.state import VERAState

llm = ChatGroq(api_key=GROQ_API_KEY, model=GROQ_MODEL, temperature=0.1)

PROMPT = """You are producing the final verified answer to a CS interview question.

You have an initial answer and a critic's feedback. Fix every issue the critic found.

Question: {query}

Initial answer:
{initial_response}

Critic feedback:
{critic_feedback}

Instructions:
- Fix all errors the critic identified
- Add every piece of missing information the critic flagged
- Remove or correct misleading parts
- Keep the answer clear and student-friendly

Then give a confidence score between 0.0 and 1.0 based on:
- Did the critic find major errors? lower score
- Is the answer now complete? higher score
- Were there things you were uncertain about? lower score

Respond ONLY with valid JSON and absolutely nothing else.

{{
  "final_answer": "the complete improved answer here",
  "confidence_score": 0.87,
  "confidence_reasoning": "brief reason for this score",
  "improvements_made": ["fixed X", "added Y"]
}}"""

def synthesis_node(state: VERAState) -> VERAState:
    prompt = PROMPT.format(
        query=state["query"],
        initial_response=state["initial_response"],
        critic_feedback=json.dumps(state["critic_feedback"], indent=2)
    )
    result = llm.invoke([HumanMessage(content=prompt)])

    raw = result.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        parsed = {
            "final_answer": state["initial_response"],
            "confidence_score": 0.5,
            "confidence_reasoning": "Parse error — used initial response as fallback.",
            "improvements_made": []
        }

    score = parsed.get("confidence_score", 0.5)
    return {
        **state,
        "final_response":    parsed.get("final_answer", state["initial_response"]),
        "confidence_score":  score,
        "improvements_made": parsed.get("improvements_made", []),
        "in_review_queue":   score < CONFIDENCE_THRESHOLD,
    }