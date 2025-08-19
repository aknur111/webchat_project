"""add join_code to chats

Revision ID: a8de50abc84d
Revises: 5502f0254bcd
Create Date: 2025-08-15 12:09:23.688037

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from alembic import op
import sqlalchemy as sa
import secrets
import string


# revision identifiers, used by Alembic.
revision: str = 'a8de50abc84d'
down_revision: Union[str, Sequence[str], None] = '5502f0254bcd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def _gen_code():
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "".join(secrets.choice(alphabet) for _ in range(8))

def upgrade():
    op.add_column('chats', sa.Column('join_code', sa.String(length=16), nullable=True))
    op.create_unique_constraint('uq_chats_join_code', 'chats', ['join_code'])

    conn = op.get_bind()
    rows = conn.execute(sa.text("SELECT id FROM chats WHERE join_code IS NULL")).fetchall()
    for (cid,) in rows:
        code = _gen_code()
        while conn.execute(sa.text("SELECT 1 FROM chats WHERE join_code=:c"), {"c": code}).first():
            code = _gen_code()
        conn.execute(sa.text("UPDATE chats SET join_code=:c WHERE id=:i"), {"c": code, "i": cid})

    op.alter_column('chats', 'join_code', nullable=False)



def downgrade():
    op.drop_constraint('uq_chats_join_code', 'chats', type_='unique')
    op.drop_column('chats', 'join_code')

