"""Add user table

Revision ID: 963ec99e0e08
Revises: 803a85e63506
Create Date: 2021-01-11 15:42:47.893082

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '963ec99e0e08'
down_revision = '803a85e63506'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('user_id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.add_column('bounty', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'bounty', 'user', ['user_id'], ['user_id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'bounty', type_='foreignkey')
    op.drop_column('bounty', 'user_id')
    op.drop_table('user')
    # ### end Alembic commands ###
