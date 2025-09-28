"""
CREATE TABLE public.dept_keywords (
    id integer NOT NULL,
    dept_id integer,
    keyword text NOT NULL
);
"""

import enum
import uuid
from sqlalchemy import Column, String, Integer, Text, Enum, TIMESTAMP, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base
from .department import Department

class DeptKeyword(Base):
    __tablename__ = "dept_keywords"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dept_id = Column(Integer, ForeignKey('departments.id'), nullable=False)
    keyword = Column(Text, nullable=False)

    department = relationship("Department", back_populates="keywords")

    @classmethod
    def create(cls, session, dept_id: int, keyword: str):
        new_keyword = cls(dept_id=dept_id, keyword=keyword)
        session.add(new_keyword)
        session.commit()
        return new_keyword

    @classmethod
    def get_all(cls, session):
        return session.query(cls).all()

    @classmethod
    def get_by_id(cls, session, keyword_id: int):
        return session.query(cls).filter_by(id=keyword_id).first()

    @classmethod
    def get_by_dept_id(cls, session, dept_id: int):
        return session.query(cls).filter_by(dept_id=dept_id).all()
    
    def get_department(self, session):
        return session.query(Department).filter_by(id=self.dept_id).first()
    
    @classmethod
    def get_count(cls, session):
        return session.query(cls).count()