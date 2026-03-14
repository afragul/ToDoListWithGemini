"""phone num added

Revision ID: 596c567ad975
Revises: 
Create Date: 2026-03-14 14:26:22.152538

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '596c567ad975'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('phone_number', sa.String , nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    pass
