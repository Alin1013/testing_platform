from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import APIInfo, ProjectInfo, UserInfo, BusinessFlow, TestReports
from app.schemas import (
    APITestCaseCreate,
    APITestCaseResponse,
    BusinessFlowCreate,
    BusinessFlowResponse,
    TestReportResponse
)
from app.auth import get_current_user
from app.core.api_test_runner import APITestRunner

router = APIRouter(prefix="/api/v1", tags=["api-tests"])


@router.get("/projects/{project_id}/api-tests", response_model=List[APITestCaseResponse])
def get_api_test_cases(
        project_id: int,
        current_user: UserInfo = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """获取项目的所有API测试用例"""
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
    """创建API测试用例"""
    # 验证项目所有权
    project = db.query(ProjectInfo).filter(
        ProjectInfo.id == project_id,
        ProjectInfo.user_id == current_user.id
    ).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    # 创建测试用例
    db_test_case = APIInfo(
        project_id=project_id,
        case_name=test_case.case_name,
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


@router.put("/api-tests/{test_case_id}", response_model=APITestCaseResponse)
def update_api_test_case(
        test_case_id: int,
        test_case: APITestCaseCreate,
        current_user: UserInfo = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """更新API测试用例"""
    db_test_case = db.query(APIInfo).filter(APIInfo.id == test_case_id).first()
    if db_test_case is None:
        raise HTTPException(status_code=404, detail="Test case not found")

    # 验证项目所有权
    project = db.query(ProjectInfo).filter(
        ProjectInfo.id == db_test_case.project_id,
        ProjectInfo.user_id == current_user.id
    ).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    # 更新测试用例字段
    db_test_case.case_name = test_case.case_name
    db_test_case.method = test_case.method
    db_test_case.url = test_case.url
    db_test_case.headers = test_case.headers
    db_test_case.params = test_case.params
    db_test_case.body = test_case.body
    db_test_case.expected_data = test_case.expected_data

    db.commit()
    db.refresh(db_test_case)
    return db_test_case


@router.delete("/api-tests/{test_case_id}")
def delete_api_test_case(
        test_case_id: int,
        current_user: UserInfo = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """删除API测试用例"""
    db_test_case = db.query(APIInfo).filter(APIInfo.id == test_case_id).first()
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
    return {"message": "API test case deleted successfully"}


@router.post("/projects/{project_id}/api-tests/run")
def run_api_tests(
        project_id: int,
        background_tasks: BackgroundTasks,
        test_case_ids: Optional[List[int]] = None,
        current_user: UserInfo = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """执行API测试"""
    # 验证项目所有权
    project = db.query(ProjectInfo).filter(
        ProjectInfo.id == project_id,
        ProjectInfo.user_id == current_user.id
    ).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    # 获取测试用例
    query = db.query(APIInfo).filter(APIInfo.project_id == project_id)
    if test_case_ids:
        query = query.filter(APIInfo.id.in_(test_case_ids))
    test_cases = query.all()

    if not test_cases:
        raise HTTPException(status_code=404, detail="No test cases found")

    # 在后台运行测试
    background_tasks.add_task(run_tests_background, project_id, test_cases, current_user.id, db)

    return {"message": "Tests started in background", "test_count": len(test_cases)}


@router.get("/projects/{project_id}/api-tests/reports", response_model=List[TestReportResponse])
def get_api_test_reports(
        project_id: int,
        current_user: UserInfo = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """获取API测试报告"""
    # 验证项目所有权
    project = db.query(ProjectInfo).filter(
        ProjectInfo.id == project_id,
        ProjectInfo.user_id == current_user.id
    ).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    reports = db.query(TestReports).filter(
        TestReports.project_id == project_id,
        TestReports.test_type == 'api'
    ).order_by(TestReports.created_at.desc()).all()

    return reports


# 业务流程相关接口
@router.post("/projects/{project_id}/business-flows", response_model=BusinessFlowResponse)
def create_business_flow(
        project_id: int,
        business_flow: BusinessFlowCreate,
        current_user: UserInfo = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """创建业务流程"""
    # 验证项目所有权
    project = db.query(ProjectInfo).filter(
        ProjectInfo.id == project_id,
        ProjectInfo.user_id == current_user.id
    ).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    # 创建业务流程
    db_business_flow = BusinessFlow(
        project_id=project_id,
        flow_name=business_flow.flow_name,
        test_type=business_flow.test_type,
        case_ids=business_flow.case_ids
    )

    db.add(db_business_flow)
    db.commit()
    db.refresh(db_business_flow)
    return db_business_flow


@router.get("/projects/{project_id}/business-flows", response_model=List[BusinessFlowResponse])
def get_business_flows(
        project_id: int,
        current_user: UserInfo = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """获取项目的业务流程"""
    # 验证项目所有权
    project = db.query(ProjectInfo).filter(
        ProjectInfo.id == project_id,
        ProjectInfo.user_id == current_user.id
    ).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    business_flows = db.query(BusinessFlow).filter(
        BusinessFlow.project_id == project_id
    ).all()

    return business_flows


@router.get("/api-test")
def api_test_health_check():
    """API测试健康检查端点"""
    return {"status": "healthy", "message": "API Test module is working"}


def run_tests_background(project_id: int, test_cases: List[APIInfo], user_id: int, db: Session):
    """后台运行测试任务"""
    try:
        test_runner = APITestRunner()
        result = test_runner.run_tests(test_cases)

        # 保存测试报告到数据库
        report = TestReports(
            project_id=project_id,
            report_name=f"API Test Report - {test_cases[0].case_name}",
            test_type='api',
            report_path=result['report_path'],
            status='success' if result['exit_code'] == 0 else 'failed'
        )

        db.add(report)
        db.commit()

    except Exception as e:
        # 记录测试失败
        report = TestReports(
            project_id=project_id,
            report_name="API Test Report - Failed",
            test_type='api',
            report_path=None,
            status='failed'
        )
        db.add(report)
        db.commit()