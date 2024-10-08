"""Add category and grade columns to Question model

Revision ID: bdc4e2f77923
Revises: 
Create Date: 2024-09-02 14:58:19.629199

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bdc4e2f77923'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user')
    with op.batch_alter_table('comments', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'users', ['user_id'], ['id'])

    with op.batch_alter_table('performances', schema=None) as batch_op:
        batch_op.alter_column('student_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('question_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    with op.batch_alter_table('questions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('answer_text', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('type', sa.String(length=10), nullable=True))
        batch_op.add_column(sa.Column('category', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('grade', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=True))
        batch_op.create_foreign_key(None, 'users', ['user_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('questions', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('created_at')
        batch_op.drop_column('updated_at')
        batch_op.drop_column('grade')
        batch_op.drop_column('category')
        batch_op.drop_column('type')
        batch_op.drop_column('answer_text')

    with op.batch_alter_table('performances', schema=None) as batch_op:
        batch_op.alter_column('question_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('student_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    with op.batch_alter_table('comments', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')

    op.create_table('user',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('email', sa.VARCHAR(length=120), autoincrement=False, nullable=False),
    sa.Column('role', sa.VARCHAR(length=10), autoincrement=False, nullable=False),
    sa.Column('subscription', sa.VARCHAR(length=10), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='user_pkey'),
    sa.UniqueConstraint('email', name='user_email_key')
    )
    # ### end Alembic commands ###
