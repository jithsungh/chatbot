import enum
import uuid
from sqlalchemy import Column, Text, Enum, TIMESTAMP, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from collections import defaultdict

from .base import Base
from .user_question import DeptType

class TextKnowledge(Base):
    __tablename__ = "text_knowledge"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    adminid = Column(UUID(as_uuid=True), nullable=False)
    title = Column(Text, nullable=False)
    text = Column(Text, nullable=False)
    dept = Column(Enum(DeptType), nullable=False)
    createdat = Column(TIMESTAMP, nullable=False, server_default=func.now())

    # Class methods for database operations
    @classmethod
    def create(cls, session, adminid, title, text, dept):
        new_record = cls(adminid=adminid, title=title, text=text, dept=dept)
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
    
    @classmethod
    def get_all_by_adminid(cls, session, adminid):
        return session.query(cls).filter_by(adminid=adminid).all()
    
    @classmethod
    def get_all_grouped_by_dept(cls, session, adminid):
        records = session.query(cls).filter_by(adminid=adminid).all()
        grouped = defaultdict(list)
        for record in records:
            grouped[record.dept].append(record)
        return dict(grouped)
    
    @classmethod
    def get_all_by_dept(cls, session, dept):
        return session.query(cls).filter_by(dept=dept).all()
    
    @classmethod
    def get_all_by_dept_adminid(cls, session, adminid, dept):
        return session.query(cls).filter_by(adminid=adminid, dept=dept).all()
    

