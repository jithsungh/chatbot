import enum
import uuid
from sqlalchemy import Column, Text, Enum, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from collections import defaultdict

from .base import Base


class UserQuestionStatus(enum.Enum):
    pending = "pending"
    processed = "processed"


class DeptType(enum.Enum):
    HR = "HR"
    IT = "IT"
    Security = "Security"


class UserQuestion(Base):
    __tablename__ = "user_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    userid = Column(UUID(as_uuid=True), nullable=False)
    query = Column(Text, nullable=False)
    answer = Column(Text)
    context = Column(Text)
    status = Column(Enum(UserQuestionStatus), default=UserQuestionStatus.pending)
    dept = Column(Enum(DeptType))
    createdat = Column(TIMESTAMP(timezone=True), server_default=func.now())  # Changed from createdAt to createdat

    # ---------- Query Methods ----------

    @classmethod
    def retrieve_all(cls, session):
        """Return all user questions"""
        return session.query(cls).all()

    @classmethod
    def retrieve_all_processed(cls, session):
        """Return all processed user questions"""
        return session.query(cls).filter(cls.status == UserQuestionStatus.processed).all()

    @classmethod
    def retrieve_all_pending(cls, session):
        """Return all pending user questions"""
        return session.query(cls).filter(cls.status == UserQuestionStatus.pending).all()

    @classmethod
    def retrieve_all_by_dept(cls, session, dept: DeptType):
        """Return all user questions by department"""
        return session.query(cls).filter(cls.dept == dept).all()

    @classmethod
    def retrieve_pending_by_dept(cls, session, dept: DeptType):
        """Return all pending user questions for a specific department"""
        return (
            session.query(cls)
            .filter(cls.dept == dept, cls.status == UserQuestionStatus.pending)
            .all()
        )

    @classmethod
    def retrieve_processed_by_dept(cls, session, dept: DeptType):
        """Return all processed user questions for a specific department"""
        return (
            session.query(cls)
            .filter(cls.dept == dept, cls.status == UserQuestionStatus.processed)
            .all()
        )

    @classmethod
    def retrieve_by_id(cls, session, question_id: uuid.UUID):
        """Return a single user question by its ID"""
        return session.query(cls).filter(cls.id == question_id).first()

    @classmethod
    def fetch_pending_by_dept(cls, session):
        """
        Return pending user questions grouped by department.
        Result looks like:
        {
            "HR": [ {...}, {...} ],
            "IT": [ {...} ],
            "Security": [ {...} ],
            "Unassigned": [ {...} ]
        }
        """
        pending = session.query(cls).filter(cls.status == UserQuestionStatus.pending).all()

        grouped = defaultdict(list)
        for q in pending:
            dept = q.dept.value if q.dept else "Unassigned"
            grouped[dept].append({
                "id": str(q.id),
                "userid": str(q.userid),
                "query": q.query,
                "answer": q.answer,
                "context": q.context,
                "status": q.status.value,
                "dept": dept,
                "createdAt": q.createdat.isoformat() if q.createdat else None,  # Updated reference
            })

        return dict(grouped)