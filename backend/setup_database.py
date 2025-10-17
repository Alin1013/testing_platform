#!/usr/bin/env python3
"""
PostgreSQL 数据库设置脚本
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def create_database():
    """创建数据库"""
    # 首先连接到默认数据库来创建我们的数据库
    conn = psycopg2.connect(
        host="localhost",
        database="testing_platform",
        user="admin",
        password="041013"
    )
    conn.autocommit = True
    cursor = conn.cursor()

    # 创建数据库
    try:
        cursor.execute("CREATE DATABASE testing_platform")
        print("✓ 数据库 'testing_platform' 创建成功")
    except psycopg2.errors.DuplicateDatabase:
        print("✓ 数据库 'testing_platform' 已存在")
    except Exception as e:
        print(f"✗ 创建数据库失败: {e}")

    cursor.close()
    conn.close()


def test_connection():
    """测试数据库连接"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="testing_platform",
            user="admin",
            password="041013"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✓ PostgreSQL 连接成功: {version[0]}")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"✗ 数据库连接失败: {e}")
        return False


if __name__ == "__main__":
    print("正在设置 PostgreSQL 数据库...")
    create_database()
    test_connection()