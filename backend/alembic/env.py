from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.database import Base
from app.models.user import UserInfo
from app.models.project import ProjectInfo
from app.models.api_test import APIInfo,APIBusinessFlow,APIReport
from app.models.ui_test import UIInfo,UIBusinessFlow,UIReport
from app.models.business_flow import BusinessFlow
from app.models.test_reports import TestReports

config = context.config

# 设置MySQL连接URL
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL", "mysql+pymysql://root:041013@localhost/testing_platform?charset=utf8mb4"))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
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