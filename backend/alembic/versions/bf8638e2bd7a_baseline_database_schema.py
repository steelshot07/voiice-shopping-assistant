"""baseline database schema

Revision ID: bf8638e2bd7a
Revises: dca4b6e38384
Create Date: 2026-08-22 22:23:45.966564

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bf8638e2bd7a'
down_revision: Union[str, Sequence[str], None] = 'dca4b6e38384'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
