from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.database import Base
from app.models.user import UserInfo
from app.models.project import ProjectInfo
from app.models.api_test import APIInfo
from app.models.ui_test import UIInfo
from app.models.business_flow import BusinessFlow
from app.models.test_reports import TestReports

# 这是 Alembic Config 对象，提供对 .ini 文件中值的访问。
config = context.config

# 设置 SQLAlchemy URL
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL", "postgresql://test_user:test_password@localhost/testing_platform"))

# 解释记录器配置的配置文件。
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 添加你的模型的 MetaData 对象
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """在 'offline' 模式下运行迁移。"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """在 'online' 模式下运行迁移。"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()