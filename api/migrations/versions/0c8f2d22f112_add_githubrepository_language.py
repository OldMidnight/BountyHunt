"""Add GithubRepository language

Revision ID: 0c8f2d22f112
Revises: d6a7fdeab59b
Create Date: 2021-04-22 22:32:27.688283

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0c8f2d22f112'
down_revision = 'd6a7fdeab59b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('github_repository', sa.Column('language', sa.String(), nullable=True))
    op.drop_column('github_repository', 'langauge')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('github_repository', sa.Column('langauge', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('github_repository', 'language')
    # ### end Alembic commands ###