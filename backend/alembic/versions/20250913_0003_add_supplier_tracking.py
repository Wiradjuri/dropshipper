from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250913_0003'
down_revision = '20250913_0002'
branch_labels = None
depends_on = None

def upgrade() -> None:
    with op.batch_alter_table('orders') as batch_op:
        batch_op.add_column(sa.Column('supplier_order_id', sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column('tracking_number', sa.String(length=64), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('orders') as batch_op:
        batch_op.drop_column('tracking_number')
        batch_op.drop_column('supplier_order_id')
