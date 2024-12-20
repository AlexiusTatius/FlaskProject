"""Initial migration

Revision ID: c8f4030822a3
Revises: 
Create Date: 2024-11-19 15:04:52.010391

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c8f4030822a3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=100), nullable=False),
    sa.Column('password', sa.String(length=200), nullable=False),
    sa.Column('role', sa.Enum('admin', 'user', name='role_types'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('file',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('filename', sa.String(length=255), nullable=False),
    sa.Column('filepath', sa.String(length=255), nullable=False),
    sa.Column('public', sa.Boolean(), nullable=False),
    sa.Column('category', sa.String(length=100), nullable=True),
    sa.Column('tags', sa.Text(), nullable=True),
    sa.Column('view_count', sa.Integer(), nullable=True),
    sa.Column('download_count', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('file_analytics',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('total_files', sa.Integer(), nullable=True),
    sa.Column('total_storage', sa.BigInteger(), nullable=True),
    sa.Column('most_viewed', sa.Integer(), nullable=True),
    sa.Column('most_downloaded', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['most_downloaded'], ['file.id'], ),
    sa.ForeignKeyConstraint(['most_viewed'], ['file.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('file_analytics')
    op.drop_table('file')
    op.drop_table('user')
    # ### end Alembic commands ###
