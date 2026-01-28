"""
Add level column to roles table for role hierarchy support
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20260128_add_roles_level'
down_revision = 'add_roles_soft_delete'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('roles', sa.Column('level', sa.Integer(), nullable=False, server_default='0'))

def downgrade():
    op.drop_column('roles', 'level')
