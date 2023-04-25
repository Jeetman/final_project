"""Initial migration.

Revision ID: d0c7b8e4b57c
Revises: 
Create Date: 2022-11-08 17:00:02.151921

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd0c7b8e4b57c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('password', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username')
    )
    op.create_table('post',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('author_id', sa.Integer(), nullable=False),
        sa.Column('created', sa.TIMESTAMP(), server_default=sa.func.current_timestamp()),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('body', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['author_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('restaurant',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.Column('street_address', sa.String(length=50), nullable=True),
    sa.Column('description', sa.String(length=250), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('review',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('restaurant', sa.Integer(), nullable=True),
    sa.Column('user_name', sa.String(length=30), nullable=True),
    sa.Column('rating', sa.Integer(), nullable=True),
    sa.Column('review_text', sa.String(length=500), nullable=True),
    sa.Column('review_date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['restaurant'], ['restaurant.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('review')
    op.drop_table('restaurant')
    op.drop_table('post')
    op.drop_table('user')

    # ### end Alembic commands ###