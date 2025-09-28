"""
CREATE TABLE public.file_knowledge (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    adminid uuid NOT NULL,
    file_name text NOT NULL,
    file_path text NOT NULL,
    createdat timestamp with time zone DEFAULT now(),
    dept public.dept_type NOT NULL,
);
"""
import enum
import uuid
from sqlalchemy import Column, String, Integer, Text, Enum, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID
from collections import defaultdict

from .base import Base
from .user_question import DeptType

class FileKnowledge(Base):
    __tablename__ = "file_knowledge"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    adminid = Column(UUID(as_uuid=True), nullable=False)
    file_name = Column(Text, nullable=False)
    file_path = Column(Text, nullable=False)
    createdat = Column(TIMESTAMP(timezone=True), server_default=func.now())
    dept = Column(Enum(DeptType), nullable=False)

    # Class methods for database operations
    @classmethod
    def create(cls, session, adminid, file_name, file_path, dept):
        new_record = cls(adminid=adminid, file_name=file_name, file_path=file_path, dept=dept)
        session.add(new_record)
        session.commit()
        return new_record
    
    @classmethod
    def get_count(cls, session):
        return session.query(cls).count()
    
    @classmethod
    def get_by_id(cls, session, record_id):
        return session.query(cls).filter_by(id=record_id).first()
    
    @classmethod
    def get_all(cls, session):
        return session.query(cls).all()
    
    @classmethod
    def delete_by_id(cls, session, record_id):
        record = session.query(cls).filter_by(id=record_id).first()
        if record:
            session.delete(record)
            session.commit()
            return True
        return False

