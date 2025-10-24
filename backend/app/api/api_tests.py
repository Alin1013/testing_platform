from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import APIInfo, ProjectInfo, UserInfo, TestReports
from app.schemas import APITestCaseBase, APITestCaseResponse
from app.auth import get_current_user
from app.core.api_test_runner import APITestRunner
from typing import List
import uuid

router = APIRouter()

# 获取接口测试用例
@router.get("/projects/{project_id}/api-tests", response_model=List[APITestCaseResponse])
def get_api_test_cases(
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

    test_cases = db.query(APIInfo).filter(APIInfo.project_id == project_id).all()
    return test_cases

# 创建接口测试用例
@router.post("/projects/{project_id}/api-tests", response_model=APITestCaseResponse)
def create_api_test_case(
        project_id: int,
        test_case: APITestCaseBase,
        current_user: UserInfo = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    project = db.query(ProjectInfo).filter(
        ProjectInfo.id == project_id,
        ProjectInfo.user_id == current_user.id
    ).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    db_test_case = APIInfo(
        case_name=test_case.case_name,
        project_id=project_id,
        method=test_case.method,
        base_url=test_case.base_url,
        path=test_case.path,
        headers=test_case.headers,
        params=test_case.params,
        body=test_case.body,
        extract=test_case.extract,
        validate=test_case.validate
    )
    db.add(db_test_case)
    db.commit()
    db.refresh(db_test_case)
    return db_test_case

# 执行接口测试
@router.post("/projects/{project_id}/api-tests/run")
def run_api_tests(
        project_id: int,
        test_case_ids: List[int],
        background_tasks: BackgroundTasks,
        current_user: UserInfo = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    project = db.query(ProjectInfo).filter(
        ProjectInfo.id == project_id,
        ProjectInfo.user_id == current_user.id
    ).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    test_cases = db.query(APIInfo).filter(
        APIInfo.project_id == project_id,
        APIInfo.id.in_(test_case_ids)
    ).all()

    if not test_cases:
        raise HTTPException(status_code=404, detail="No test cases found")

    report = TestReports(
        report_name=f"API_Test_{uuid.uuid4().hex[:8]}",
        project_id=project_id,
        test_type="api",
        status="running"
    )
    db.add(report)
    db.commit()

    background_tasks.add_task(
        run_api_tests_background,
        test_cases,
        report.id,
        db
    )

    return {"message": "API tests started", "report_id": report.id}

def run_api_tests_background(test_cases, report_id, db):
    try:
        runner = APITestRunner()
        results = runner.run_tests(test_cases)

        report = db.query(TestReports).filter(TestReports.id == report_id).first()
        if report:
            report.status = "completed"
            report.report_path = results.get("report_path")
            db.commit()
    except Exception as e:
        report = db.query(TestReports).filter(TestReports.id == report_id).first()
        if report:
            report.status = "failed"
            db.commit()