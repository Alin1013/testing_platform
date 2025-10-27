from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import APIInfo, ProjectInfo, UserInfo
from app.schemas import APITestCaseCreate, APITestCaseResponse
from app.auth import get_current_user

router = APIRouter()  # 移至顶部，确保路由装饰器能正确引用


@router.put("/api-tests/{test_case_id}", response_model=APITestCaseResponse)
def update_api_test_case(
        test_case_id: int,
        test_case: APITestCaseCreate,
        current_user: UserInfo = Depends(get_current_user),
        db: Session = Depends(get_db)
):
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

    # 更新测试用例字段（根据实际模型字段调整）
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