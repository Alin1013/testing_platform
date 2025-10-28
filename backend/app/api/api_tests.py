# app/api/api_tests.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import APIInfo, ProjectInfo, UserInfo, BusinessFlow, TestReports
from app.schemas import (
    APITestCaseCreate,
    APITestCaseResponse,
    BusinessFlowCreate,
    BusinessFlowResponse
)
from app.auth import get_current_user

router = APIRouter()


# 健康检查端点
@router.get("/api-test")
def api_test_health_check():
    return {"status": "healthy", "message": "API Test module is working"}


# 获取项目的所有API测试用例
@router.get("/projects/{project_id}/api-tests", response_model=List[APITestCaseResponse])
def get_api_test_cases(
        project_id: int,
        current_user: UserInfo = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """获取项目的所有API测试用例"""
    print(f"🔍 获取项目 {project_id} 的测试用例")

    # 验证项目所有权
    project = db.query(ProjectInfo).filter(
        ProjectInfo.id == project_id,
        ProjectInfo.user_id == current_user.id
    ).first()
    if project is None:
        print(f"❌ 项目 {project_id} 未找到")
        raise HTTPException(status_code=404, detail="Project not found")

    test_cases = db.query(APIInfo).filter(APIInfo.project_id == project_id).all()
    print(f"✅ 找到 {len(test_cases)} 个测试用例")
    return test_cases


# 创建API测试用例
@router.post("/projects/{project_id}/api-tests", response_model=APITestCaseResponse)
def create_api_test_case(
        project_id: int,
        test_case: APITestCaseCreate,
        current_user: UserInfo = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """创建API测试用例"""
    print(f"📝 为项目 {project_id} 创建测试用例: {test_case.case_name}")

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
    print(f"✅ 测试用例创建成功，ID: {db_test_case.id}")
    return db_test_case


# 更新API测试用例
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


# 删除API测试用例
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


# 执行API测试
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

    # 这里应该调用测试运行器，为了简化，我们直接返回
    return {"message": "Tests started", "test_count": len(test_cases)}


# 获取测试报告
@router.get("/projects/{project_id}/api-tests/reports")
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


# 创建业务流程
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


# 获取项目的业务流程
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


# 测试端点 - 用于调试
@router.get("/test")
def test_endpoint():
    return {"message": "API tests router is working"}


@router.get("/projects/{project_id}/test")
def test_project_endpoint(project_id: int):
    return {"message": f"Project {project_id} API tests endpoint is working"}