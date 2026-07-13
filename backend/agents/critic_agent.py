import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from backend.config import GROQ_API_KEY, GROQ_MODEL
from backend.graph.state import VERAState

llm = ChatGroq(api_key=GROQ_API_KEY, model=GROQ_MODEL, temperature=0.2)

PROMPT = """You are a strict technical reviewer checking an AI answer to a CS interview question.

Question: {query}

Answer to review:
{initial_response}

Your job: find problems. Be specific and harsh.

Check for:
1. Factual errors — wrong complexity, wrong definition, wrong example
2. Missing key information a CS student must know for an interview
3. Misleading or oversimplified statements
4. Important edge cases that were ignored

Respond ONLY with valid JSON and absolutely nothing else before or after it.

{{
  "has_issues": true,
  "severity": "none",
  "errors": ["exact error 1"],
  "missing_info": ["important missing point 1"],
  "misleading_parts": ["quote from answer that is misleading"],
  "summary": "one sentence overall quality assessment"
}}

Use "severity": "none", "low", "medium", or "high".
If there are no issues, set has_issues to false and leave the lists empty."""

def critic_node(state: VERAState) -> VERAState:
    prompt = PROMPT.format(
        query=state["query"],
        initial_response=state["initial_response"]
    )
    result = llm.invoke([HumanMessage(content=prompt)])

    raw = result.content.strip()
    # Strip markdown code fences if model adds them
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        feedback = json.loads(raw)
    except json.JSONDecodeError:
        feedback = {
            "has_issues": False,
            "severity": "none",
            "errors": [],
            "missing_info": [],
            "misleading_parts": [],
            "summary": "Could not parse critic response."
        }

    return {**state, "critic_feedback": feedback}