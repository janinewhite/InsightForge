from __future__ import annotations

from typing import Any


class ConversationMemory:
    def __init__(self, session_state: Any):
        self.session_state = session_state
        if "conversation_memory" not in self.session_state:
            self.session_state["conversation_memory"] = []

    def remember(self, user_query: str, answer_text: str, retrieval_intent: str) -> None:
        self.session_state["conversation_memory"].append(
            {
                "user_query": user_query,
                "answer_text": answer_text,
                "retrieval_intent": retrieval_intent,
            }
        )
        self.session_state["conversation_memory"] = self.session_state["conversation_memory"][-8:]

    def context(self) -> list[dict[str, str]]:
        return self.session_state["conversation_memory"]
