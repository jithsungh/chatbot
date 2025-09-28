"""
CREATE TABLE public.departments (
    id integer NOT NULL,
    name public.dept_type NOT NULL,
    description text NOT NULL,
    createdat timestamp with time zone DEFAULT now()
);
"""

import enum
import uuid
from sqlalchemy import Column, String, Integer, Text, Enum, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID

from .base import Base
from .user_question import DeptType

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Enum(DeptType), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    createdat = Column(TIMESTAMP(timezone=True), server_default=func.now())

    @classmethod
    def create(cls, session, name: DeptType, description: str):
        new_department = cls(name=name, description=description)
        session.add(new_department)
        session.commit()
        return new_department

    @classmethod
    def get_all(cls, session):
        return session.query(cls).all()

    @classmethod
    def get_by_id(cls, session, department_id: int):
        return session.query(cls).filter_by(id=department_id).first()

    @classmethod
    def get_by_name(cls, session, name: DeptType):
        return session.query(cls).filter_by(name=name).first()
