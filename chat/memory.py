from __future__ import annotations

from typing import Any, Optional

from chat.session import SessionManager


class ConversationMemory:
    """In-memory + persisted conversation memory system.

    Stores conversation history, user preferences, and session state
    so the agent can remember context across interactions.
    """

    def __init__(self, session_manager: SessionManager) -> None:
        self._sm = session_manager
        self._session_id: str = ""
        self._current_prefs: dict[str, Any] = {}

    @property
    def session_id(self) -> str:
        return self._session_id

    def init_session(self, preferences: dict | None = None) -> str:
        """Create a new session or resume existing one."""
        self._session_id = self._sm.create_session(preferences)
        self._current_prefs = preferences or {}
        return self._session_id

    def resume_session(self, session_id: str) -> bool:
        """Resume an existing session."""
        s = self._sm.get_session(session_id)
        if s is None:
            return False
        self._session_id = session_id
        self._current_prefs = s.preferences or {}
        return True

    def add_message(self, role: str, content: str, metadata: dict | None = None) -> None:
        """Store a message in the conversation history."""
        if not self._session_id:
            return
        self._sm.save_message(self._session_id, role, content, metadata)

    def get_history(self, limit: int = 50) -> list[dict[str, Any]]:
        """Retrieve recent conversation history."""
        if not self._session_id:
            return []
        return self._sm.get_history(self._session_id, limit)

    def update_preferences(self, updates: dict[str, Any]) -> None:
        """Persist user preferences."""
        self._current_prefs.update(updates)
        if self._session_id:
            self._sm.update_preferences(self._session_id, self._current_prefs)

    def get_preferences(self) -> dict[str, Any]:
        return dict(self._current_prefs)

    def get_recent_context(self, n: int = 10) -> list[dict[str, str]]:
        """Get recent messages formatted as LLM context."""
        history = self.get_history(n)
        return [
            {"role": m["role"], "content": m["content"]}
            for m in history[-n:]
        ]

    def build_system_prompt(self, candidate_profile: str, additional_context: str = "") -> str:
        """Build a system prompt incorporating history and preferences."""
        parts = [
            "You are an AI Job Hunting Assistant in a terminal application.",
            "Be concise, helpful, and use markdown formatting.",
        ]
        if candidate_profile:
            parts.append(f"\nCandidate Profile:\n{candidate_profile[:1500]}")
        if self._current_prefs:
            prefs_str = "\n".join(f"- {k}: {v}" for k, v in self._current_prefs.items())
            parts.append(f"\nUser Preferences:\n{prefs_str}")
        if additional_context:
            parts.append(f"\n{additional_context}")
        return "\n".join(parts)

    def clear(self) -> None:
        """Reset memory for the current session."""
        self._current_prefs = {}
