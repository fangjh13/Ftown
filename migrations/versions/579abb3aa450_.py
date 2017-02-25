"""empty message

Revision ID: 579abb3aa450
Revises: ac50e4d023ba
Create Date: 2017-02-20 11:25:37.605872

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '579abb3aa450'
down_revision = 'ac50e4d023ba'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('mtimestamp', sa.DateTime(), nullable=True))
    op.create_index(op.f('ix_posts_mtimestamp'), 'posts', ['mtimestamp'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_posts_mtimestamp'), table_name='posts')
    op.drop_column('posts', 'mtimestamp')
    # ### end Alembic commands ###