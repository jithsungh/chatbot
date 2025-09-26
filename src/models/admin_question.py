import enum
import uuid
from sqlalchemy import Column, Text, Enum, TIMESTAMP, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from collections import defaultdict

from .base import Base
from .user_question import DeptType

class AdminQuestionStatus(enum.Enum):
    pending = "pending"
    processed = "processed"

class AdminQuestion(Base):
    __tablename__ = "admin_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    adminid = Column(UUID(as_uuid=True), nullable=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)
    status = Column(Enum(AdminQuestionStatus), default=AdminQuestionStatus.pending)
    dept = Column(Enum(DeptType), nullable=True)
    frequency = Column(Integer, default=1)
    vectordbid = Column(UUID(as_uuid=True), nullable=True)
    createdat = Column(TIMESTAMP(timezone=True), server_default=func.now(), name='createdat')

    # Class methods for querying
    @classmethod
    def retrieve_all(cls, session):
        """Return all admin questions"""
        return session.query(cls).all()

    @classmethod
    def retrieve_all_processed(cls, session):
        """Return all processed admin questions"""
        return session.query(cls).filter(cls.status == AdminQuestionStatus.processed).all()

    @classmethod
    def retrieve_all_pending(cls, session):
        """Return all pending admin questions"""
        return session.query(cls).filter(cls.status == AdminQuestionStatus.pending).all()

    @classmethod
    def retrieve_all_by_dept(cls, session, dept: DeptType):
        """Return all questions by department"""
        return session.query(cls).filter(cls.dept == dept).all()

    @classmethod
    def retrieve_pending_by_dept(cls, session, dept: DeptType):
        """Return all pending questions for a specific department"""
        return (
            session.query(cls)
            .filter(cls.dept == dept, cls.status == AdminQuestionStatus.pending)
            .all()
        )

    @classmethod
    def retrieve_processed_by_dept(cls, session, dept: DeptType):
        """Return all processed questions for a specific department"""
        return (
            session.query(cls)
            .filter(cls.dept == dept, cls.status == AdminQuestionStatus.processed)
            .all()
        )

    @classmethod
    def retrieve_by_id(cls, session, question_id: uuid.UUID):
        """Return a single question by its ID"""
        return session.query(cls).filter(cls.id == question_id).first()

    @classmethod
    def fetch_pending_by_dept(cls, session):
        """
        Return pending admin questions grouped by department.
        """
        pending = session.query(cls).filter(cls.status == AdminQuestionStatus.pending).all()

        grouped = defaultdict(list)
        for q in pending:
            dept = q.dept.value if q.dept else "Unassigned"
            grouped[dept].append({
                "id": str(q.id),
                "adminid": str(q.adminid) if q.adminid else None,
                "question": q.question,
                "answer": q.answer,
                "status": q.status.value,
                "dept": dept,
                "frequency": q.frequency,
                "vectordbid": str(q.vectordbid) if q.vectordbid else None,
                "createdAt": q.createdat.isoformat() if q.createdat else None,
            })

        return dict(grouped)