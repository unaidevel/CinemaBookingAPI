"""Adjusts

Revision ID: ac95d5e8ccc0
Revises: 2e89870878cd
Create Date: 2025-04-28 22:39:07.524709

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ac95d5e8ccc0'
down_revision: Union[str, None] = '2e89870878cd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
