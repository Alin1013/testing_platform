from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import ProjectInfo, UserInfo, TestReports
from app.schemas import TestReportCreate, TestReportResponse
from app.auth import get_current_user
from app.core.performance_runner import PerformanceRunner
from typing import List
import uuid

router = APIRouter()


@router.post("/projects/{project_id}/performance-tests")
def create_performance_test(
        project_id: int,
        test_config: dict,
        current_user: UserInfo = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    # 验证项目所有权
    project = db.query(ProjectInfo).filter(
        ProjectInfo.id == project_id,
        ProjectInfo.user_id == current_user.id
    ).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    # 这里可以保存性能测试配置到数据库，为了简化，我们直接运行
    # 创建测试报告记录
    report = TestReports(
        report_name=f"Performance_Test_{uuid.uuid4().hex[:8]}",
        project_id=project_id,
        test_type="performance",
        status="running"
    )
    db.add(report)
    db.commit()

    return {"message": "Performance test created", "report_id": report.id}


@router.post("/projects/{project_id}/performance-tests/run")
def run_performance_test(
        project_id: int,
        test_config: dict,
        background_tasks: BackgroundTasks,
        current_user: UserInfo = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    # 验证项目所有权
    project = db.query(ProjectInfo).filter(
        ProjectInfo.id == project_id,
        ProjectInfo.user_id == current_user.id
    ).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    # 创建测试报告记录
    report = TestReports(
        report_name=f"Performance_Test_{uuid.uuid4().hex[:8]}",
        project_id=project_id,
        test_type="performance",
        status="running"
    )
    db.add(report)
    db.commit()

    # 在后台运行测试
    background_tasks.add_task(
        run_performance_test_background,
        test_config,
        report.id,
        db
    )

    return {"message": "Performance test started", "report_id": report.id}


def run_performance_test_background(test_config, report_id, db):
    try:
        runner = PerformanceRunner()
        results = runner.run_test(test_config)

        # 更新测试报告
        report = db.query(TestReports).filter(TestReports.id == report_id).first()
        if report:
            report.status = "completed"
            report.report_path = results.get("report_path")
            db.commit()
    except Exception as e:
        # 更新测试报告为失败
        report = db.query(TestReports).filter(TestReports.id == report_id).first()
        if report:
            report.status = "failed"
            db.commit()


@router.get("/projects/{project_id}/performance-tests/reports")
def get_performance_reports(
        project_id: int,
        current_user: UserInfo = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    # 验证项目所有权
    project = db.query(ProjectInfo).filter(
        ProjectInfo.id == project_id,
        ProjectInfo.user_id == current_user.id
    ).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    reports = db.query(TestReports).filter(
        TestReports.project_id == project_id,
        TestReports.test_type == "performance"
    ).all()
    return reports


@router.post("/projects/{project_id}/performance-tests/{test_id}/stop")
def stop_performance_test(
        project_id: int,
        test_id: int,
        current_user: UserInfo = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    # 这里实现停止性能测试的逻辑
    return {"message": "Performance test stopped"}