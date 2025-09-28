"""
CREATE TABLE public.response_times (
    id integer NOT NULL,
    "timestamp" timestamp with time zone NOT NULL,
    avg_response_time double precision,
    requests_count integer DEFAULT 0 NOT NULL
);
"""

import enum
import uuid
from sqlalchemy import Column, String, Integer, Text, Enum, TIMESTAMP, Float, func
from sqlalchemy.dialects.postgresql import UUID
from collections import defaultdict

from .base import Base

class ResponseTime(Base):
    __tablename__ = "response_times"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    avg_response_time = Column(Float, nullable=True)
    requests_count = Column(Integer, default=0, nullable=False)

    # Class methods for database operations
    @classmethod
    def create(cls, session, avg_response_time=None, requests_count=0):
        new_record = cls(avg_response_time=avg_response_time, requests_count=requests_count)
        session.add(new_record)
        session.commit()
        return new_record
    
    @classmethod
    def get_count(cls, session):
        return session.query(cls).count()
    