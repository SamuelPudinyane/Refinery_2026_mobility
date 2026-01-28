"""
Remove level column from roles table
"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '20260128_remove_roles_level'
down_revision = '20260128_add_roles_level'
branch_labels = None
depends_on = None

def upgrade():
    op.drop_column('roles', 'level')

def downgrade():
    import sqlalchemy as sa
    op.add_column('roles', sa.Column('level', sa.Integer(), nullable=False, server_default='0'))
