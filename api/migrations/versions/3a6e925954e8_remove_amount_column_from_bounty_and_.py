"""remove amount column from bounty and investment table

Revision ID: 3a6e925954e8
Revises: 8a5a0fc19ae9
Create Date: 2021-03-19 20:58:50.086364

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '3a6e925954e8'
down_revision = '8a5a0fc19ae9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('bounty', 'external_links',
               existing_type=postgresql.ARRAY(sa.TEXT()),
               type_=sa.ARRAY(sa.String()),
               existing_nullable=False)
    op.drop_column('bounty', 'amount')
    op.drop_column('investment', 'amount')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('investment', sa.Column('amount', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('bounty', sa.Column('amount', postgresql.MONEY(), autoincrement=False, nullable=False))
    op.alter_column('bounty', 'external_links',
               existing_type=sa.ARRAY(sa.String()),
               type_=postgresql.ARRAY(sa.TEXT()),
               existing_nullable=False)
    # ### end Alembic commands ###