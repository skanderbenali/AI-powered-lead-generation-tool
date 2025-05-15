from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas import Project, ProjectCreate, ProjectUpdate, ProjectStats
from app.services.projects import (
    get_projects,
    get_project,
    create_project,
    update_project,
    delete_project,
    get_project_stats
)
from app.deps.auth import get_current_user

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("/", response_model=List[Project])
def read_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all projects owned by the current user"""
    projects = get_projects(db, owner_id=current_user.id, skip=skip, limit=limit)
    return projects


@router.post("/", response_model=Project)
def create_new_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new project"""
    return create_project(db=db, project=project, owner_id=current_user.id)


@router.get("/{project_id}", response_model=Project)
def read_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific project by ID"""
    project = get_project(db, project_id=project_id)
    if project is None or project.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.put("/{project_id}", response_model=Project)
def update_existing_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a project"""
    project = get_project(db, project_id=project_id)
    if project is None or project.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    return update_project(db=db, project=project, project_data=project_data)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a project"""
    project = get_project(db, project_id=project_id)
    if project is None or project.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    delete_project(db=db, project_id=project_id)
    return None


@router.get("/{project_id}/stats", response_model=ProjectStats)
def get_statistics_for_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get statistics for a project"""
    project = get_project(db, project_id=project_id)
    if project is None or project.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    return get_project_stats(db=db, project_id=project_id)
