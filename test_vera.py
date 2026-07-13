from backend.graph.workflow import run_vera
import json

query = "What is the difference between a stack and a queue?"
print(f"Query: {query}")
print("-" * 60)

result = run_vera(query)

print(f"INITIAL RESPONSE:\n{result['initial_response']}\n")
print(f"CRITIC FEEDBACK:\n{json.dumps(result['critic_feedback'], indent=2)}\n")
print(f"FINAL RESPONSE:\n{result['final_response']}\n")
print(f"CONFIDENCE: {round(result['confidence_score'] * 100, 1)}%")
print(f"IN REVIEW QUEUE: {result['in_review_queue']}")
print(f"IMPROVEMENTS MADE: {result['improvements_made']}")