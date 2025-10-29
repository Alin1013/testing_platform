# complete_reset.py
# !/usr/bin/env python3
"""
完全重置数据库和迁移
"""

import os
import subprocess
from app.database import engine
from sqlalchemy import text


def drop_all_tables():
    """强制删除所有表（处理外键约束）"""
    print("强制删除所有表...")
    try:
        with engine.connect() as conn:
            # 禁用外键检查
            conn.execute(text("SET FOREIGN_KEY_CHECKS=0"))
            conn.commit()

            # 获取所有表
            result = conn.execute(text("SHOW TABLES"))
            tables = [row[0] for row in result]

            # 删除所有表
            for table in tables:
                print(f"删除表: {table}")
                conn.execute(text(f"DROP TABLE IF EXISTS `{table}`"))

            # 启用外键检查
            conn.execute(text("SET FOREIGN_KEY_CHECKS=1"))
            conn.commit()

            print("✓ 所有表已删除")
            return True
    except Exception as e:
        print(f"✗ 删除表失败: {e}")
        return False


def cleanup_migrations():
    """清理迁移文件"""
    print("清理迁移文件...")
    try:
        # 删除所有迁移版本文件
        versions_dir = "alembic/versions"
        for file in os.listdir(versions_dir):
            if file.endswith(".py") and file != "__init__.py":
                os.remove(os.path.join(versions_dir, file))
                print(f"删除: {file}")

        # 删除 alembic_version 表
        with engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS alembic_version"))
            conn.commit()

        print("✓ 迁移文件已清理")
        return True
    except Exception as e:
        print(f"✗ 清理迁移文件失败: {e}")
        return False


def create_initial_migration():
    """创建初始迁移"""
    print("创建初始迁移...")
    try:
        result = subprocess.run([
            "alembic", "revision", "--autogenerate", "-m", "Initial tables"
        ], capture_output=True, text=True)

        if result.returncode == 0:
            print("✓ 迁移脚本创建成功")
            return True
        else:
            print(f"✗ 创建迁移脚本失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ 创建迁移脚本异常: {e}")
        return False


def apply_migration():
    """应用迁移"""
    print("应用数据库迁移...")
    try:
        result = subprocess.run([
            "alembic", "upgrade", "head"
        ], capture_output=True, text=True)

        if result.returncode == 0:
            print("✓ 迁移应用成功")
            return True
        else:
            print(f"✗ 迁移应用失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ 迁移应用异常: {e}")
        return False


def main():
    print("开始完全重置数据库...")

    if drop_all_tables() and cleanup_migrations():
        if create_initial_migration() and apply_migration():
            print("\n🎉 数据库完全重置成功！")
            return

    print("\n❌ 数据库重置失败")


if __name__ == "__main__":
    main()