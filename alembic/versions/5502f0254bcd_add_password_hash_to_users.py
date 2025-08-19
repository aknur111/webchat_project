"""add password_hash to users

Revision ID: 5502f0254bcd
Revises: c7e94e00e298
Create Date: 2025-08-14 15:53:15.509795

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5502f0254bcd'
down_revision: Union[str, Sequence[str], None] = 'c7e94e00e298'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('users', sa.Column('password_hash', sa.String(length=128), nullable=False, server_default=''))
    op.alter_column('users', 'password_hash', server_default=None)


def downgrade():
    op.drop_column('users', 'password_hash')

