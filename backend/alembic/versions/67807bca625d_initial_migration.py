"""initial migration

Revision ID: 67807bca625d
Revises:
Create Date: 2023-11-15 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '67807bca625d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建所有表结构（实际项目中应该逐个定义）
    op.create_table(
        'user_info',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('avatar_path', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username')
    )

    op.create_table(
        'project_info',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_name', sa.String(), nullable=False),
        sa.Column('test_style', sa.String(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['user_info.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # 其他表结构...


def downgrade() -> None:
    # 按创建相反的顺序删除表
    op.drop_table('project_info')
    op.drop_table('user_info')
    # 其他表...