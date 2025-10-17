from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

# 用户相关的模式
class UserBase(BaseModel):
    username: str
    email: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    avatar_path: Optional[str] = None

class UserResponse(UserBase):
    id: int
    avatar_path: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# 项目相关的模式
class ProjectBase(BaseModel):
    project_name: str
    test_style: str

class ProjectCreate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# 接口测试相关的模式
class APITestCaseBase(BaseModel):
    case_name: str
    method: str
    url: str
    headers: Optional[Dict[str, Any]] = None
    params: Optional[Dict[str, Any]] = None
    body: Optional[Dict[str, Any]] = None
    expected_data: Optional[Dict[str, Any]] = None

class APITestCaseCreate(APITestCaseBase):
    project_id: int

class APITestCaseResponse(APITestCaseBase):
    id: int
    project_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# UI测试相关的模式
class UITestCaseBase(BaseModel):
    case_name: str
    script_content: str

class UITestCaseCreate(UITestCaseBase):
    project_id: int

class UITestCaseResponse(UITestCaseBase):
    id: int
    project_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# 业务流程相关的模式
class BusinessFlowBase(BaseModel):
    flow_name: str
    test_type: str
    case_ids: List[int]

class BusinessFlowCreate(BusinessFlowBase):
    project_id: int

class BusinessFlowResponse(BusinessFlowBase):
    id: int
    project_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# 测试报告相关的模式
class TestReportBase(BaseModel):
    report_name: str
    test_type: str
    report_path: str
    status: str

class TestReportCreate(TestReportBase):
    project_id: int

class TestReportResponse(TestReportBase):
    id: int
    project_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# 认证相关的模式
class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# 导出所有模式类
__all__ = [
    # 用户相关
    "UserBase", "UserCreate", "UserLogin", "UserUpdate", "UserResponse",
    # 项目相关
    "ProjectBase", "ProjectCreate", "ProjectResponse",
    # 接口测试相关
    "APITestCaseBase", "APITestCaseCreate", "APITestCaseResponse",
    # UI测试相关
    "UITestCaseBase", "UITestCaseCreate", "UITestCaseResponse",
    # 业务流程相关
    "BusinessFlowBase", "BusinessFlowCreate", "BusinessFlowResponse",
    # 测试报告相关
    "TestReportBase", "TestReportCreate", "TestReportResponse",
    # 认证相关
    "Token"
]