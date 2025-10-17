from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import APIInfo, ProjectInfo, UserInfo, TestReports, BusinessFlow
from app.schemas import APITestCaseCreate, APITestCaseResponse, BusinessFlowCreate, BusinessFlowResponse
from app.auth import get_current_user
from app.core.api_test_runner import APITestRunner
from typing import List
import uuid
import json

router = APIRouter()


@router.get("/projects/{project_id}/api-tests", response_model=List[APITestCaseResponse])
def get_api_test_cases(
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

    test_cases = db.query(APIInfo).filter(APIInfo.project_id == project_id).all()
    return test_cases


@router.post("/projects/{project_id}/api-tests", response_model=APITestCaseResponse)
def create_api_test_case(
        project_id: int,
        test_case: APITestCaseCreate,
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

    db_test_case = APIInfo(
        case_name=test_case.case_name,
        project_id=project_id,
        method=test_case.method,
        url=test_case.url,
        headers=test_case.headers,
        params=test_case.params,
        body=test_case.body,
        expected_data=test_case.expected_data
    )
    db.add(db_test_case)
    db.commit()
    db.refresh(db_test_case)
    return db_test_case


@router.post("/projects/{project_id}/api-tests/run")
def run_api_tests(
        project_id: int,
        test_case_ids: List[int],
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

    # 获取测试用例
    test_cases = db.query(APIInfo).filter(
        APIInfo.project_id == project_id,
        APIInfo.id.in_(test_case_ids)
    ).all()

    if not test_cases:
        raise HTTPException(status_code=404, detail="No test cases found")

    # 创建测试报告记录
    report = TestReports(
        report_name=f"API_Test_{uuid.uuid4().hex[:8]}",
        project_id=project_id,
        test_type="api",
        status="running"
    )
    db.add(report)
    db.commit()

    # 在后台运行测试
    background_tasks.add_task(
        run_api_tests_background,
        test_cases,
        report.id,
        db
    )

    return {"message": "API tests started", "report_id": report.id}


def run_api_tests_background(test_cases, report_id, db):
    try:
        # 这里实现实际的测试运行逻辑
        runner = APITestRunner()
        results = runner.run_tests(test_cases)

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


@router.post("/projects/{project_id}/api-business-flows", response_model=BusinessFlowResponse)
def create_api_business_flow(
        project_id: int,
        business_flow: BusinessFlowCreate,
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

    db_business_flow = BusinessFlow(
        flow_name=business_flow.flow_name,
        project_id=project_id,
        test_type="api",
        case_ids=business_flow.case_ids
    )
    db.add(db_business_flow)
    db.commit()
    db.refresh(db_business_flow)
    return db_business_flow


@router.get("/projects/{project_id}/api-tests/reports")
def get_api_test_reports(
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
        TestReports.test_type == "api"
    ).all()
    return reports