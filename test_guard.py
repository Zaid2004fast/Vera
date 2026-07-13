from backend.graph.workflow import run_vera

tests = [
    "What is a binary search tree?",           # should go through full pipeline
    "What is the time complexity of quicksort?", # should go through full pipeline
    "Who is the president of Pakistan?",        # should be blocked
    "What do you think about politics?",        # should be blocked
    "Tell me a joke",                           # should be blocked
    "Explain deadlocks in operating systems",   # should go through full pipeline
    "What is the weather today?",               # should be blocked
]

for q in tests:
    result = run_vera(q)
    status = "✓ CS — full pipeline" if result["is_cs_question"] else "✗ OFF-TOPIC — blocked"
    print(f"\n[{status}]")
    print(f"Q: {q}")
    if not result["is_cs_question"]:
        print(f"Response: {result['final_response'][:80]}...")
    else:
        print(f"Confidence: {round(result['confidence_score']*100,1)}%")