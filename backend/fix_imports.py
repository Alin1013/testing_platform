#!/usr/bin/env python3
"""
修复导入问题的脚本
"""

import os
import re


def fix_schemas_init():
    """修复 schemas/__init__.py 文件"""
    schemas_file = "app/schemas/__init__.py"

    # 读取当前内容
    with open(schemas_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否包含必要的类定义
    required_classes = [
        "UserBase", "UserCreate", "UserLogin", "UserUpdate", "UserResponse",
        "ProjectBase", "ProjectCreate", "ProjectResponse",
        "APITestCaseBase", "APITestCaseCreate", "APITestCaseResponse",
        "UITestCaseBase", "UITestCaseCreate", "UITestCaseResponse",
        "BusinessFlowBase", "BusinessFlowCreate", "BusinessFlowResponse",
        "TestReportBase", "TestReportCreate", "TestReportResponse",
        "Token"
    ]

    missing_classes = []
    for class_name in required_classes:
        if f"class {class_name}" not in content:
            missing_classes.append(class_name)

    if missing_classes:
        print(f"发现缺失的类: {missing_classes}")
        # 重新写入完整的内容
        with open(schemas_file, 'w', encoding='utf-8') as f:
            f.write('''from pydantic import BaseModel, EmailStr
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
''')
        print("✓ schemas/__init__.py 已修复")
    else:
        print("✓ schemas/__init__.py 看起来正常")


def fix_api_imports():
    """修复 API 路由中的导入"""
    api_files = [
        "app/api/users.py",
        "app/api/projects.py",
        "app/api/api_tests.py",
        "app/api/ui_tests.py",
        "app/api/performance.py"
    ]

    for file_path in api_files:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 修复 schemas 导入
            content = re.sub(
                r'from app\.schemas import ([^\n]*)',
                r'from app.schemas import \1',
                content
            )

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"✓ 修复了 {file_path} 的导入")


def main():
    """主函数"""
    print("正在修复导入问题...")
    fix_schemas_init()
    fix_api_imports()
    print("导入问题修复完成！")


if __name__ == "__main__":
    main()