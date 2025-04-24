"""
Task routes for the Task Management API.
Handles CRUD operations for tasks.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.models.task import Task, TaskStatus, TaskPriority
from app.models.user import User
from app.middleware.auth_middleware import get_current_active_user
from app.utils.validators import sanitize_string
from config.config import get_db

router = APIRouter()

# Pydantic models for request/response
class TaskCreate(BaseModel):
    """Schema for task creation request."""
    title: str
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None

class TaskUpdate(BaseModel):
    """Schema for task update request."""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None

class TaskResponse(BaseModel):
    """Schema for task response data."""
    id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    due_date: Optional[datetime]
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True

@router.post("/", response_model=TaskResponse)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new task for the current user.

    Args:
        task_data: Task creation data
        current_user: The authenticated user
        db: Database session

    Returns:
        TaskResponse: The created task
    """
    # Sanitize input
    task_data.title = sanitize_string(task_data.title)
    task_data.description = sanitize_string(task_data.description)

    # Create new task
    new_task = Task(
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority,
        due_date=task_data.due_date,
        owner_id=current_user.id
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task

@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all tasks for the current user with optional filtering.

    Args:
        status: Optional filter by task status
        priority: Optional filter by task priority
        skip: Number of tasks to skip (for pagination)
        limit: Maximum number of tasks to return
        current_user: The authenticated user
        db: Database session

    Returns:
        List[TaskResponse]: List of tasks
    """
    query = db.query(Task).filter(Task.owner_id == current_user.id)

    # Apply filters if provided
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)

    # Apply pagination
    tasks = query.offset(skip).limit(limit).all()
    return tasks

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific task by ID.

    Args:
        task_id: The ID of the task to retrieve
        current_user: The authenticated user
        db: Database session

    Returns:
        TaskResponse: The requested task

    Raises:
        HTTPException: If task not found or user doesn't have permission
    """
    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == current_user.id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update a specific task.

    Args:
        task_id: The ID of the task to update
        task_data: The update data
        current_user: The authenticated user
        db: Database session

    Returns:
        TaskResponse: The updated task

    Raises:
        HTTPException: If task not found or user doesn't have permission
    """
    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == current_user.id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Update fields if provided
    if task_data.title is not None:
        task.title = sanitize_string(task_data.title)
    if task_data.description is not None:
        task.description = sanitize_string(task_data.description)
    if task_data.status is not None:
        task.status = task_data.status
        # Set completed_at timestamp if task is completed
        if task_data.status == TaskStatus.COMPLETED:
            task.completed_at = datetime.utcnow()
    if task_data.priority is not None:
        task.priority = task_data.priority
    if task_data.due_date is not None:
        task.due_date = task_data.due_date

    db.commit()
    db.refresh(task)

    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a specific task.

    Args:
        task_id: The ID of the task to delete
        current_user: The authenticated user
        db: Database session

    Raises:
        HTTPException: If task not found or user doesn't have permission
    """
    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == current_user.id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    db.delete(task)
    db.commit()

    return None