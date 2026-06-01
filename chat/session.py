from __future__ import annotations

import datetime as dt
import uuid
from typing import Any, Optional

from sqlalchemy import Column, DateTime, Integer, String, Text, JSON, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

SessionBase = declarative_base()


class StoredSession(SessionBase):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    updated_at = Column(DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)
    preferences = Column(JSON, default=dict)
    metadata_json = Column(JSON, default=dict)


class StoredMessage(SessionBase):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), nullable=False, index=True)
    role = Column(String(16), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=dt.datetime.utcnow)
    metadata_json = Column(JSON, default=dict)


class SessionManager:
    """Manages chat sessions with persistent SQLite storage."""

    def __init__(self, db_path: str = "data/chat_sessions.db"):
        self.engine = create_engine(f"sqlite:///{db_path}")
        SessionBase.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def create_session(self, preferences: dict | None = None) -> StoredSession:
        session = self.Session()
        s = StoredSession(
            session_id=str(uuid.uuid4())[:12],
            preferences=preferences or {},
        )
        session.add(s)
        session.commit()
        sid = s.session_id
        session.close()
        return sid

    def get_session(self, session_id: str) -> Optional[StoredSession]:
        session = self.Session()
        s = session.query(StoredSession).filter_by(session_id=session_id).first()
        session.close()
        return s

    def save_message(self, session_id: str, role: str, content: str, metadata: dict | None = None) -> None:
        session = self.Session()
        msg = StoredMessage(
            session_id=session_id,
            role=role,
            content=content,
            metadata_json=metadata or {},
        )
        session.add(msg)

        # Update session timestamp
        s = session.query(StoredSession).filter_by(session_id=session_id).first()
        if s:
            s.updated_at = dt.datetime.utcnow()

        session.commit()
        session.close()

    def get_history(self, session_id: str, limit: int = 50) -> list[dict[str, Any]]:
        session = self.Session()
        msgs = (
            session.query(StoredMessage)
            .filter_by(session_id=session_id)
            .order_by(StoredMessage.timestamp.asc())
            .limit(limit)
            .all()
        )
        session.close()
        return [
            {"role": m.role, "content": m.content, "timestamp": m.timestamp.isoformat() if m.timestamp else ""}
            for m in msgs
        ]

    def update_preferences(self, session_id: str, preferences: dict) -> None:
        session = self.Session()
        s = session.query(StoredSession).filter_by(session_id=session_id).first()
        if s:
            s.preferences = {**(s.preferences or {}), **preferences}
            session.commit()
        session.close()

    def list_sessions(self, limit: int = 20) -> list[dict[str, Any]]:
        session = self.Session()
        sessions = (
            session.query(StoredSession)
            .order_by(StoredSession.updated_at.desc())
            .limit(limit)
            .all()
        )
        session.close()
        return [
            {
                "session_id": s.session_id,
                "created_at": s.created_at.isoformat() if s.created_at else "",
                "updated_at": s.updated_at.isoformat() if s.updated_at else "",
                "preferences": s.preferences or {},
            }
            for s in sessions
        ]
