from typing import TypedDict

class VERAState(TypedDict):
    query:             str
    is_cs_question:    bool        # ← new
    retrieved_chunks:  list
    initial_response:  str
    critic_feedback:   dict
    final_response:    str
    confidence_score:  float
    in_review_queue:   bool
    improvements_made: list