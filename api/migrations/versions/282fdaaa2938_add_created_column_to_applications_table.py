"""Add created column to applications table

Revision ID: 282fdaaa2938
Revises: 929da93b0fd7
Create Date: 2021-03-21 16:51:56.773561

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '282fdaaa2938'
down_revision = '929da93b0fd7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('bounty_application', sa.Column('created', sa.DateTime(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('bounty_application', 'created')
    # ### end Alembic commands ###
