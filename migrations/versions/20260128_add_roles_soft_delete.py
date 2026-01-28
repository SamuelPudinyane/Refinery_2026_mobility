"""
Add is_deleted, deleted_at, deleted_by columns to roles table for soft delete support
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_roles_soft_delete'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('roles', sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column('roles', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    op.add_column('roles', sa.Column('deleted_by', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column('roles', 'deleted_by')
    op.drop_column('roles', 'deleted_at')
    op.drop_column('roles', 'is_deleted')
