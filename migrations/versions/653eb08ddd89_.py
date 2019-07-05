"""empty message

Revision ID: 653eb08ddd89
Revises: 684e38e8936b
Create Date: 2019-07-05 04:10:22.886562

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '653eb08ddd89'
down_revision = '684e38e8936b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('payments', sa.Column('PaidOn', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('payments', 'PaidOn')
    # ### end Alembic commands ###
