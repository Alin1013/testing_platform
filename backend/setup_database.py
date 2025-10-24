#!/usr/bin/env python3
"""
MySQL 数据库设置脚本
"""

import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def create_database():
    """创建数据库"""
    # 连接到MySQL服务器（不指定数据库）
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("MYSQL_PASSWORD", "041013")
    )
    cursor = conn.cursor()

    # 创建数据库
    try:
        cursor.execute("CREATE DATABASE IF NOT EXISTS testing_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print("✓ 数据库 'testing_platform' 创建成功")
    except Exception as e:
        print(f"✗ 创建数据库失败: {e}")

    cursor.close()
    conn.close()


def test_connection():
    """测试数据库连接"""
    try:
        conn = mysql.connector.connect(
            host="localhost",
            database="testing_platform",
            user="root",
            password=os.getenv("MYSQL_PASSWORD", "041013")
        )
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION();")
        version = cursor.fetchone()
        print(f"✓ MySQL 连接成功: {version[0]}")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"✗ 数据库连接失败: {e}")
        return False


if __name__ == "__main__":
    print("正在设置 MySQL 数据库...")
    create_database()
    test_connection()