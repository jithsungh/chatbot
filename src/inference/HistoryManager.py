import asyncio
from collections import deque, defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Any


class HistoryManager:
    def __init__(self, max_turns: int = 10):
        self.max_turns = max_turns
        self._history: Dict[str, deque] = {}
        self._last_context: Dict[str, Any] = {}
        self._last_followup: Dict[str, str] = {}
        self._locks: Dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)
        self._global_lock = asyncio.Lock()  # For purge or structural changes

    async def get_context(self, user_id: str, k: int = 10) -> List[Dict[str, Any]]:
        """Return last k turns of Q&A for a user (ignores context/followup)."""
        async with self._locks[user_id]:
            history = list(self._history.get(user_id, deque()))
            return history[-min(k, self.max_turns):]

    async def get_last_context(self, user_id: str) -> Any:
        """Return the last stored context for a user."""
        async with self._locks[user_id]:
            return self._last_context.get(user_id)

    async def get_last_followup(self, user_id: str) -> str:
        """Return the last stored follow-up for a user."""
        async with self._locks[user_id]:
            return self._last_followup.get(user_id)

    async def update_context(
        self, user_id: str, question: str, answer: str, followup: str, context: Any
    ) -> None:
        """Update history with new Q&A, and overwrite last context/followup."""
        async with self._locks[user_id]:
            if user_id not in self._history:
                self._history[user_id] = deque()

            # Append new Q&A
            self._history[user_id].append({
                "HUMAN": question,
                "ASSISTANT": answer,
                "timestamp": datetime.now()
            })

            # Maintain max_turns
            if len(self._history[user_id]) > self.max_turns:
                self._history[user_id].popleft()

            # Store last context & followup
            self._last_context[user_id] = context
            self._last_followup[user_id] = followup

    async def purge_old_context(self, older_than_hours: int = 48) -> None:
        """Remove users whose latest interaction is older than given hours."""
        cutoff = datetime.now() - timedelta(hours=older_than_hours)
        async with self._global_lock:
            to_remove = [
                user_id for user_id, turns in self._history.items()
                if turns and turns[-1]["timestamp"] < cutoff
            ]
            for user_id in to_remove:
                async with self._locks[user_id]:
                    self._history.pop(user_id, None)
                    self._last_context.pop(user_id, None)
                    self._last_followup.pop(user_id, None)
                    self._locks.pop(user_id, None)

    async def get_active_users_count(self) -> int:
        """Return the number of users who currently have any conversation history."""
        await self.purge_old_context(older_than_hours=48)
        async with self._global_lock:
            return len(self._history)

    async def clear_history(self, user_id: str) -> None: 
        """Clear conversation history for a specific user."""
        async with self._locks[user_id]:
            self._history.pop(user_id, None)
            self._last_context.pop(user_id, None)
            self._last_followup.pop(user_id, None)
            self._locks.pop(user_id, None)




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

