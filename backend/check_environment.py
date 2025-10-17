#!/usr/bin/env python3
"""
环境验证脚本
"""

import os
import sys
from sqlalchemy import text  # 添加这行导入


def check_python_version():
    """检查 Python 版本"""
    version = sys.version_info
    print(f"Python 版本: {version.major}.{version.minor}.{version.micro}")
    if version.major == 3 and version.minor >= 8:
        print("✓ Python 版本符合要求")
        return True
    else:
        print("✗ 需要 Python 3.8 或更高版本")
        return False


def check_dependencies():
    """检查依赖"""
    try:
        import fastapi
        import sqlalchemy
        import psycopg2
        import uvicorn
        print("✓ 主要依赖已安装")
        return True
    except ImportError as e:
        print(f"✗ 缺少依赖: {e}")
        return False


def check_database():
    """检查数据库连接"""
    try:
        from app.database import engine
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))  # 使用 text()
            version = result.scalar()
            print(f"✓ 数据库连接成功: {version}")
            return True
    except Exception as e:
        print(f"✗ 数据库连接失败: {e}")
        return False


def check_models():
    """检查模型导入"""
    try:
        from app.models.user import UserInfo
        from app.models.project import ProjectInfo
        from app.models.api_test import APIInfo
        from app.models.ui_test import UIInfo
        from app.models.business_flow import BusinessFlow
        from app.models.test_reports import TestReports
        print("✓ 所有模型导入成功")
        return True
    except Exception as e:
        print(f"✗ 模型导入失败: {e}")
        return False


def check_routes():
    """检查路由导入"""
    try:
        from app.api.users import router as users_router
        from app.api.projects import router as projects_router
        from app.api.api_tests import router as api_tests_router
        from app.api.ui_tests import router as ui_tests_router
        from app.api.performance import router as performance_router
        print("✓ 所有路由导入成功")
        return True
    except Exception as e:
        print(f"✗ 路由导入失败: {e}")
        return False


if __name__ == "__main__":
    print("正在验证环境配置...")
    print("-" * 50)

    checks = [
        ("Python 版本", check_python_version),
        ("依赖", check_dependencies),
        ("数据库", check_database),
        ("数据模型", check_models),
        ("API 路由", check_routes),
    ]

    results = []
    for check_name, check_func in checks:
        print(f"\n检查 {check_name}...")
        results.append((check_name, check_func()))

    print("\n" + "=" * 50)
    print("环境验证结果:")

    all_passed = True
    for check_name, passed in results:
        status = "✓" if passed else "✗"
        print(f"{status} {check_name}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n🎉 所有检查通过！环境配置正确。")
        print("您可以启动应用了：")
        print("  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    else:
        print("\n❌ 有些检查未通过，请解决上述问题。")