"""Add on delete clauses to bounty_categories FKs

Revision ID: af11679dca81
Revises: 1b56e85c41fa
Create Date: 2021-03-19 19:45:13.990076

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'af11679dca81'
down_revision = '1b56e85c41fa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('fk_bounty_categories_bounty_id_bounty', 'bounty_categories', type_='foreignkey')
    op.create_foreign_key(op.f('fk_bounty_categories_bounty_id_bounty'), 'bounty_categories', 'bounty', ['bounty_id'], ['bounty_id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f('fk_bounty_categories_bounty_id_bounty'), 'bounty_categories', type_='foreignkey')
    op.create_foreign_key('fk_bounty_categories_bounty_id_bounty', 'bounty_categories', 'bounty', ['bounty_id'], ['bounty_id'])
    # ### end Alembic commands ###
