from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from .db import Base

class Agent(Base):
    __tablename__ = "agents"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    last_seen = Column(DateTime, nullable=True)
    status = Column(String(32), nullable=False, default="unknown")

    jobs = relationship("Job", back_populates="agent")

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    kind = Column(String(128), nullable=False)
    payload_json = Column(Text, nullable=True)
    status = Column(String(32), nullable=False, default="queued")  # queued | in_progress | completed | failed
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    agent = relationship("Agent", back_populates="jobs")
    result = relationship("Result", back_populates="job", uselist=False)

class Result(Base):
    __tablename__ = "results"
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, unique=True)
    status = Column(String(32), nullable=False)  # completed | failed
    output_json = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    job = relationship("Job", back_populates="result")
