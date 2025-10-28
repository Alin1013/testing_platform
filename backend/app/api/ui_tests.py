from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import UIInfo, ProjectInfo, UserInfo, TestReports, BusinessFlow
from app.schemas import UITestCaseCreate, UITestCaseResponse, BusinessFlowCreate, BusinessFlowResponse
from app.auth import get_current_user
from app.core.ui_test_runner import UITestRunner
from typing import List, Optional
from datetime import datetime
import uuid
import json

router = APIRouter(prefix="/projects", tags=["UI Tests"])


# 获得测试用例
@router.get("/{project_id}/ui-tests", response_model=List[UITestCaseResponse])
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

    # 将steps字段从JSON字符串转换为列表
    for test_case in test_cases:
        if test_case.steps and isinstance(test_case.steps, str):
            try:
                test_case.steps = json.loads(test_case.steps)
            except json.JSONDecodeError:
                test_case.steps = []
        else:
            test_case.steps = test_case.steps or []

    return test_cases


# 创建测试用例
@router.post("/{project_id}/ui-tests", response_model=UITestCaseResponse)
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

    # 将steps列表转换为JSON字符串存储
    steps_json = json.dumps(test_case.steps) if test_case.steps else "[]"

    db_test_case = UIInfo(
        case_name=test_case.case_name,
        project_id=project_id,
        base_url=test_case.base_url,
        script_content=test_case.script_content,
        steps=steps_json,
        record=test_case.record if hasattr(test_case, 'record') else False
    )

    db.add(db_test_case)
    db.commit()
    db.refresh(db_test_case)

    # 将steps字段转换回列表返回
    if db_test_case.steps and isinstance(db_test_case.steps, str):
        db_test_case.steps = json.loads(db_test_case.steps)
    else:
        db_test_case.steps = db_test_case.steps or []

    return db_test_case


# 更新测试用例
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

    # 更新所有字段
    db_test_case.case_name = test_case.case_name
    db_test_case.base_url = test_case.base_url
    db_test_case.script_content = test_case.script_content
    db_test_case.steps = json.dumps(test_case.steps) if test_case.steps else "[]"
    if hasattr(test_case, 'record'):
        db_test_case.record = test_case.record
    db_test_case.updated_at = datetime.now()

    db.commit()
    db.refresh(db_test_case)

    # 将steps字段转换回列表返回
    if db_test_case.steps and isinstance(db_test_case.steps, str):
        db_test_case.steps = json.loads(db_test_case.steps)
    else:
        db_test_case.steps = db_test_case.steps or []

    return db_test_case


# 删除测试用例
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


# 执行测试用例
@router.post("/projects/{project_id}/ui-tests/run")
def run_ui_tests(
        project_id: int,
        request_data: dict,
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

    test_case_ids = request_data.get("test_case_ids", [])

    # 获取测试用例
    test_cases = db.query(UIInfo).filter(
        UIInfo.project_id == project_id,
        UIInfo.id.in_(test_case_ids)
    ).all()

    # 为每个测试用例解析steps字段
    for test_case in test_cases:
        if test_case.steps and isinstance(test_case.steps, str):
            try:
                test_case.steps = json.loads(test_case.steps)
            except json.JSONDecodeError:
                test_case.steps = []
        else:
            test_case.steps = test_case.steps or []

    # 创建测试报告记录
    report = TestReports(
        report_name=f"UI_Test_{uuid.uuid4().hex[:8]}",
        project_id=project_id,
        test_type="ui",
        status="running",
        created_at=datetime.now()
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
            report.updated_at = datetime.now()
            db.commit()
    except Exception as e:
        # 更新测试报告为失败
        report = db.query(TestReports).filter(TestReports.id == report_id).first()
        if report:
            report.status = "failed"
            report.updated_at = datetime.now()
            db.commit()
        print(f"UI tests failed: {e}")

# 创建工作流
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

# 获取测试报告
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

    reports = db.query(TestReports).filter(
        TestReports.project_id == project_id,
        TestReports.test_type == "ui"
    ).all()
    return reports

# 获取测试附件
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

# 获取业务流程列表
@router.get("/projects/{project_id}/ui-business-flows", response_model=List[BusinessFlowResponse])
def get_ui_business_flows(
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

    business_flows = db.query(BusinessFlow).filter(
        BusinessFlow.project_id == project_id,
        BusinessFlow.test_type == "ui"
    ).all()
    return business_flows

# 删除业务流程
@router.delete("/ui-business-flows/{flow_id}")
def delete_ui_business_flow(
        flow_id: int,
        current_user: UserInfo = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    business_flow = db.query(BusinessFlow).filter(
        BusinessFlow.id == flow_id,
    ).first()
    if business_flow is None:
        raise HTTPException(status_code=404, detail="No business flow found")

    # 验证项目所有权
    project = db.query(ProjectInfo).filter(
        ProjectInfo.id == business_flow.project_id,
        ProjectInfo.user_id == current_user.id
    ).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(business_flow)
    db.commit()
    return {"message": "Business flow deleted successfully"}

@router.get("/test-route")
def test_route():
    return {"message": "UI tests router is working"}