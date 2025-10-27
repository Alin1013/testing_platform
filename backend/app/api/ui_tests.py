from django import db
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import UIInfo, ProjectInfo, UserInfo, TestReports, BusinessFlow
from app.schemas import UITestCaseCreate, UITestCaseResponse, BusinessFlowCreate, BusinessFlowResponse
from app.auth import get_current_user
from app.core.ui_test_runner import UITestRunner
from typing import List
from datetime import datetime
import uuid
import json

from sqlalchemy.sql.functions import current_user

from app.models import business_flow

router = APIRouter()

#获得测试用例
@router.get("/projects/{project_id}/ui-tests", response_model=List[UITestCaseResponse])
def get_ui_test_cases(
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

    test_cases = db.query(UIInfo).filter(UIInfo.project_id == project_id).all()
    return test_cases

#创建测试用例
@router.post("/projects/{project_id}/ui-tests", response_model=UITestCaseResponse)
def create_ui_test_case(
        project_id: int,
        test_case: UITestCaseCreate,
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

    db_test_case = UIInfo(
        case_name=test_case.case_name,
        project_id=project_id,
        script_content=test_case.script_content
    )
    db.add(db_test_case)
    db.commit()
    db.refresh(db_test_case)
    return db_test_case

#更新测试用例
@router.put("/ui-tests/{test_case_id}", response_model=UITestCaseResponse)
def update_ui_test_case(
        test_case_id: int,
        test_case: UITestCaseCreate,
        current_user: UserInfo = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    db_test_case = db.query(UIInfo).filter(UIInfo.id == test_case_id).first()
    if db_test_case is None:
        raise HTTPException(status_code=404, detail="Test case not found")

    # 验证项目所有权
    project = db.query(ProjectInfo).filter(
        ProjectInfo.id == db_test_case.project_id,
        ProjectInfo.user_id == current_user.id
    ).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    db_test_case.case_name = test_case.case_name
    db_test_case.script_content = test_case.script_content
    db.commit()
    db.refresh(db_test_case)
    return db_test_case

#删除测试用例
@router.delete("/ui-tests/{test_case_id}")
def delete_ui_test_case(
        test_case_id: int,
        current_user: UserInfo = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    db_test_case = db.query(UIInfo).filter(UIInfo.id == test_case_id).first()
    if db_test_case is None:
        raise HTTPException(status_code=404, detail="Test case not found")

    # 验证项目所有权
    project = db.query(ProjectInfo).filter(
        ProjectInfo.id == db_test_case.project_id,
        ProjectInfo.user_id == current_user.id
    ).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(db_test_case)
    db.commit()
    return {"message": "UI test case deleted successfully"}

#执行测试用例
@router.post("/projects/{project_id}/ui-tests/run")
def run_ui_tests(
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
    test_cases = db.query(UIInfo).filter(
        UIInfo.project_id == project_id,
        UIInfo.id.in_(test_case_ids)
    ).all()

    if not test_cases:
        raise HTTPException(status_code=404, detail="No test cases found")

    # 创建测试报告记录
    report = TestReports(
        report_name=f"UI_Test_{uuid.uuid4().hex[:8]}",
        project_id=project_id,
        test_type="ui",
        status="running"
    )
    db.add(report)
    db.commit()

    # 在后台运行测试
    background_tasks.add_task(
        run_ui_tests_background,
        test_cases,
        report.id,
        db
    )

    return {"message": "UI tests started", "report_id": report.id}


def run_ui_tests_background(test_cases, report_id, db):
    try:
        runner = UITestRunner()
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

#创建工作流
@router.post("/projects/{project_id}/ui-business-flows", response_model=BusinessFlowResponse)
def create_ui_business_flow(
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
        test_type="ui",
        case_ids=business_flow.case_ids
    )
    db.add(db_business_flow)
    db.commit()
    db.refresh(db_business_flow)
    return db_business_flow

#获取测试报告
@router.get("/projects/{project_id}/ui-tests/reports")
def get_ui_test_reports(
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
        TestReports.test_type == "ui"
    ).all()
    return reports

#获取测试附件
@router.get("/projects/{project_id}/ui-tests/reports/{report_id}/artifacts")
def get_ui_test_artifacts(
        project_id: int,
        report_id: int,
        current_user: UserInfo = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    # 验证项目所有权和报告
    project = db.query(ProjectInfo).filter(
        ProjectInfo.id == project_id,
        ProjectInfo.user_id == current_user.id
    ).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    report = db.query(TestReports).filter(
        TestReports.id == report_id,
        TestReports.project_id == project_id
    ).first()
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")

    # 这里应该返回测试产生的截图、录制文件等路径
    # 简化处理，返回一个空的列表
    return {"screenshots": [], "videos": []}
#获取业务流程列表
@router.get('projects/{project_id}/ui-business-flows',response_model=list[BusinessFlowResponse])
def get_ui_business_flows(
        project_id:int,
        current_user: UserInfo = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    #验证项目所有权
    project = db.query(ProjectInfo).filter(
        ProjectInfo.id == project_id,
        ProjectInfo.user_id == current_user.id
    ).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    business_flows=db.query(BusinessFlow).filter(
        BusinessFlow.project_id == project_id,
        BusinessFlow.test_type == "ui"
    ).all()
    return business_flows

#删除业务流程
@router.delete("/ui-business-flows/{flow_id}")
def delete_ui_business_flow(
        flow_id: int,
        current_user: UserInfo = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    project = db.query(BusinessFlow).filter(
        BusinessFlow.id == flow_id,
    ).first()
    if business_flow is None:
        raise HTTPException(status_code=404, detail="No business flow found")

    #验证项目所有权
    project = db.query(ProjectInfo).filter(
        ProjectInfo.id == project.id,
        ProjectInfo.user_id == current_user.id
    ).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(business_flow)
    db.commit()
    return{"message": "Business flow deleted successfully"}