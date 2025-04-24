"""
Task model for the Task Management API.
Defines the structure and relationships for task data in our database.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.config import Base
import enum

class TaskStatus(str, enum.Enum):
    """Enumeration for task status values."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class TaskPriority(str, enum.Enum):
    """Enumeration for task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Task(Base):
    """
    Task model representing individual tasks in our system.
    Each task belongs to a user and has various attributes for management.
    """
    __tablename__ = "tasks"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Task fields
    title = Column(String, nullable=False)
    description = Column(String)
    status = Column(Enum(TaskStatus), default=TaskStatus.TODO)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    due_date = Column(DateTime(timezone=True), nullable=True)

    # Foreign key to user
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Timestamp fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    owner = relationship("User", back_populates="tasks")

    def __repr__(self):
        """String representation of the task object for debugging."""
        return f"<Task(id={self.id}, title='{self.title}', status='{self.status}')>"