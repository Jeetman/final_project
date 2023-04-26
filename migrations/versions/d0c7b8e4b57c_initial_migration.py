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
        sa.Column('genre', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username')
    )
    op.create_table('books',
        sa.Column('isbn', sa.String(), nullable=False),
        sa.Column('author', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('uploader', sa.String(), nullable=True),
        sa.Column('available', sa.String(), nullable=False),
        sa.Column('genre', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('isbn')
    )



def downgrade():

    op.drop_table('books')
    op.drop_table('user')

    # ### end Alembic commands ###