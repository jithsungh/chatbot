import uuid
import enum
from sqlalchemy import Column, Integer, Text, Enum, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from .base import Base
from .user_question import DeptType

class DeptFailureStatus(enum.Enum):
    pending = "pending"
    processed = "processed"
    discarded = "discarded"

class DeptFailure(Base):
    __tablename__ = "dept_failures"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query = Column(Text, nullable=False)
    adminid = Column(UUID(as_uuid=True), nullable=True)
    comments = Column(Text, nullable=True)
    detected = Column(Text, nullable=False)
    expected = Column(Text, nullable=False)
    status = Column(Enum(DeptFailureStatus), default=DeptFailureStatus.pending)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    @classmethod
    def create(cls, session, query, detected, expected, adminid=None, comments=None):
        new_failure = cls(
            query=query,
            detected=detected,
            expected=expected,
            adminid=adminid,
            comments=comments
        )
        session.add(new_failure)
        session.commit()
        return new_failure
    
    @classmethod
    def get_all(cls, session):
        return session.query(cls).all()
    
    @classmethod
    def get_by_id(cls, session, failure_id):
        return session.query(cls).filter_by(id=failure_id).first()
    
    @classmethod
    def get_by_status(cls, session, status: DeptFailureStatus):
        return session.query(cls).filter_by(status=status).all()
    
    @classmethod
    def get_count(cls, session):
        return session.query(cls).count()