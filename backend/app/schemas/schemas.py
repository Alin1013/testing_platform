from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

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

class UITestCaseBase(BaseModel):
    case_name: str
    base_url: str
    steps: List[Dict[str, Any]]

class UITestCaseCreate(UITestCaseBase):
    project_id: int

class UITestCaseResponse(UITestCaseBase):
    id: int
    project_id: int
    created_at: datetime

    class Config:
        from_attributes = True

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

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse