#!/usr/bin/env python3
"""
数据库初始化脚本
"""

import os
import sys
from sqlalchemy import text  # 添加这行导入
from app.database import engine, Base
from app.models.user import UserInfo
from app.models.project import ProjectInfo
from app.models.api_test import APIInfo
from app.models.ui_test import UIInfo
from app.models.business_flow import BusinessFlow
from app.models.test_reports import TestReports


def init_database():
    """初始化数据库表"""
    try:
        print("正在创建数据库表...")
        Base.metadata.create_all(bind=engine)
        print("✓ 数据库表创建成功")
        return True
    except Exception as e:
        print(f"✗ 数据库表创建失败: {e}")
        return False


def test_database():
    """测试数据库连接和基本操作"""
    try:
        from app.database import SessionLocal

        print("测试数据库连接...")
        db = SessionLocal()

        # 测试连接 - 使用 text() 构造
        result = db.execute(text("SELECT 1"))
        print(f"✓ 数据库连接成功: {result.scalar()}")

        # 测试表访问
        user_count = db.query(UserInfo).count()
        print(f"✓ 用户表访问成功，当前用户数: {user_count}")

        db.close()
        return True

    except Exception as e:
        print(f"✗ 数据库测试失败: {e}")
        return False


if __name__ == "__main__":
    print("正在初始化数据库...")

    if init_database():
        if test_database():
            print("\n🎉 数据库初始化完成！")
        else:
            print("\n⚠ 数据库初始化完成，但测试失败")
    else:
        print("\n❌ 数据库初始化失败")