"""
SQLAlchemy models for database storage
Production-ready version (SQLAlchemy 2.x compatible)
"""

from sqlalchemy import (
    create_engine,
    Column,
    String,
    Float,
    DateTime,
    JSON,
    ForeignKey,
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime


Base = declarative_base()


# =========================
# STUDENTS TABLE
# =========================

class StudentDB(Base):
    __tablename__ = "students"

    student_id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    branch = Column(String(50), nullable=False)
    year = Column(String(20), nullable=False)

    skills = Column(JSON, default=list)
    target_companies = Column(JSON, default=list)
    cgpa = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationship
    sessions = relationship(
        "AssessmentSessionDB",
        back_populates="student",
        cascade="all, delete-orphan"
    )


# =========================
# ASSESSMENT SESSIONS TABLE
# =========================

class AssessmentSessionDB(Base):
    __tablename__ = "assessment_sessions"

    session_id = Column(String(50), primary_key=True)

    student_id = Column(
        String(50),
        ForeignKey("students.student_id"),
        index=True,
        nullable=False
    )

    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)

    status = Column(String(20), default="in_progress")

    responses = Column(JSON)  # MVP approach (can normalize later)
    scores = Column(JSON)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    student = relationship(
        "StudentDB",
        back_populates="sessions"
    )


# =========================
# QUESTION BANK TABLE
# =========================

class QuestionBankDB(Base):
    __tablename__ = "question_bank"

    question_id = Column(String(50), primary_key=True)

    type = Column(String(20), nullable=False, index=True)
    topic = Column(String(100), nullable=False, index=True)
    subtopic = Column(String(100))
    difficulty = Column(String(20), index=True)

    question_data = Column(JSON)

    # IMPORTANT: renamed from "metadata"
    question_metadata = Column(JSON)

    created_at = Column(DateTime, default=datetime.utcnow)


# =========================
# DATABASE INITIALIZER
# =========================

def init_db(db_url="sqlite:///./placement.db"):
    """
    Initialize database and create tables
    """

    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False}
        if "sqlite" in db_url
        else {},
    )

    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(bind=engine)

    return engine, SessionLocal