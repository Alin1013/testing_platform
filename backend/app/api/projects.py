from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.project import ProjectInfo
from app.models.user import UserInfo
from app.schemas import ProjectCreate, ProjectResponse
from app.auth import get_current_user
from typing import List

router = APIRouter()


@router.get("/projects", response_model=List[ProjectResponse])
def get_projects(
        skip: int = 0,
        limit: int = 100,
        current_user: UserInfo = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    try:
        # 即使没有项目，也会返回空列表，而不是错误
        projects = db.query(ProjectInfo).filter(ProjectInfo.user_id == current_user.id).offset(skip).limit(limit).all()
        return projects  # 没有项目时返回空列表
    except Exception as e:
        import logging
        logging.error(f"Error fetching projects: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch projects: {str(e)}")


@router.post("/projects", response_model=ProjectResponse)
def create_project(
        project: ProjectCreate,
        current_user: UserInfo = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    # 验证测试类型
    valid_test_styles = ["api", "ui", "performance"]
    if project.test_style not in valid_test_styles:
        raise HTTPException(status_code=400, detail="Invalid test style")

    db_project = ProjectInfo(
        project_name=project.project_name,
        test_style=project.test_style,
        user_id=current_user.id
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


@router.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(
        project_id: int,
        current_user: UserInfo = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    project = db.query(ProjectInfo).filter(
        ProjectInfo.id == project_id,
        ProjectInfo.user_id == current_user.id
    ).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.put("/projects/{project_id}", response_model=ProjectResponse)
def update_project(
        project_id: int,
        project: ProjectCreate,
        current_user: UserInfo = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    db_project = db.query(ProjectInfo).filter(
        ProjectInfo.id == project_id,
        ProjectInfo.user_id == current_user.id
    ).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    db_project.project_name = project.project_name
    db_project.test_style = project.test_style
    db.commit()
    db.refresh(db_project)
    return db_project


@router.delete("/projects/{project_id}")
def delete_project(
        project_id: int,
        current_user: UserInfo = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    project = db.query(ProjectInfo).filter(
        ProjectInfo.id == project_id,
        ProjectInfo.user_id == current_user.id
    ).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(project)
    db.commit()
    return {"message": "Project deleted successfully"}