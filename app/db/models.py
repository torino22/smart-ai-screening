from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.db.setup import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    entities_entry = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    entities = relationship("Entity", back_populates="candidate", cascade="all, delete-orphan")
    logs = relationship("Log", back_populates="candidate", cascade="all, delete-orphan")


class Entity(Base):
    __tablename__ = "entities"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))

    # Core Interview Entities
    name = Column(String, nullable=True)
    skills = Column(Text, nullable=True)  # Comma-separated
    yoe = Column(String, nullable=True)
    previous_role = Column(String, nullable=True)
    desired_role = Column(String, nullable=True)
    previous_ctc = Column(String, nullable=True)
    expected_ctc = Column(String, nullable=True)

    # Additional Expected Entities
    education = Column(String, nullable=True)
    certifications = Column(Text, nullable=True)
    notice_period = Column(String, nullable=True)
    location = Column(String, nullable=True)
    current_company = Column(String, nullable=True)
    projects = Column(Text, nullable=True)
    preferred_location = Column(String, nullable=True)

    # Optional for any future flexible field
    other_info = Column(Text, nullable=True)

    candidate = relationship("Candidate", back_populates="entities")


class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))

    file_path = Column(String, nullable=True)
    transcription = Column(String, nullable=True)
    faq = Column(Text, nullable=True)

    candidate = relationship("Candidate", back_populates="logs")


