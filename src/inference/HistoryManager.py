from collections import deque
from datetime import datetime, timedelta
from typing import Dict, List, Any


class HistoryManager:
    def __init__(self, max_turns: int = 10):
        self.max_turns = max_turns
        self._history: Dict[str, deque] = {}
        self._last_context: Dict[str, Any] = {}
        self._last_followup: Dict[str, str] = {}

    def get_context(self, user_id: str, k: int = 10) -> List[Dict[str, Any]]:
        """Return last k turns of Q&A for a user (ignores context/followup)."""
        history = list(self._history.get(user_id, deque()))
        return history[-min(k, self.max_turns):]

    def get_last_context(self, user_id: str) -> Any:
        """Return the last stored context for a user."""
        return self._last_context.get(user_id)

    def get_last_followup(self, user_id: str) -> str:
        """Return the last stored follow-up for a user."""
        return self._last_followup.get(user_id)

    def update_context(self, user_id: str, question: str, answer: str, followup: str, context) -> None:
        """Update history with new Q&A, and overwrite last context/followup."""
        if user_id not in self._history:
            self._history[user_id] = deque()

        # Store Q&A history
        self._history[user_id].append({
            "HUMAN": question,
            "ASSISTANT": answer,
            "timestamp": datetime.now()
        })

        if len(self._history[user_id]) > self.max_turns:
            self._history[user_id].popleft()

        # Overwrite context & followup (only keep latest)
        self._last_context[user_id] = context
        self._last_followup[user_id] = followup

    def purge_old_context(self, older_than_hours: int = 48) -> None:
        """Remove users whose latest interaction is older than given hours."""
        cutoff = datetime.now() - timedelta(hours=older_than_hours)
        to_remove = [
            uid for uid, turns in self._history.items()
            if turns and turns[-1]["timestamp"] < cutoff
        ]
        for uid in to_remove:
            self._history.pop(uid, None)
            self._last_context.pop(uid, None)
            self._last_followup.pop(uid, None)
    
    def clear_history(self, user_id: str) -> None:
        """Clear conversation history for a specific user."""
        self._history.pop(user_id, None)
        self._last_context.pop(user_id, None)
        self._last_followup.pop(user_id, None)



# if __name__ == "__main__":
#     hm = HistoryManager(max_turns=10)

#     # Simulate 27 messages for one user
#     for i in range(27):
#         hm.update_context("user123", f"Q{i}", f"A{i}")

#     # Only 25 should remain
#     print(len(hm.get_context("user123")))   # -> 25

#     # Add another user
#     hm.update_context("alice", "Hi", "Hello!")

#     # Purge users with no activity in last 48h
#     hm.purge_old_context(older_than_hours=48)

#     # Inspect history
#     for turn in hm.get_context("alice"):
#         print(turn["timestamp"], turn["question"], "->", turn["answer"])

