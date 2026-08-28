"""initial schema for users, recordings, analyses, reports

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-08-19 18:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False, server_default='clinician'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # 2. recordings table
    op.create_table(
        'recordings',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('sound_category', sa.String(length=50), nullable=False),
        sa.Column('chest_location', sa.String(length=100), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('duration_seconds', sa.Float(), nullable=False),
        sa.Column('sample_rate', sa.Integer(), nullable=False, server_default='4000'),
        sa.Column('channels', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('patient_gender', sa.String(length=10), nullable=True),
        sa.Column('patient_age', sa.Integer(), nullable=True),
        sa.Column('clinical_notes', sa.Text(), nullable=True),
        sa.Column('recorded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_recordings_user_id'), 'recordings', ['user_id'], unique=False)
    op.create_index(op.f('ix_recordings_sound_category'), 'recordings', ['sound_category'], unique=False)

    # 3. analyses table
    op.create_table(
        'analyses',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('recording_id', sa.String(length=36), nullable=False),
        sa.Column('predicted_class', sa.String(length=100), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('class_probabilities', sa.JSON(), nullable=False),
        sa.Column('mel_spectrogram_path', sa.String(length=500), nullable=False),
        sa.Column('gradcam_heatmap_path', sa.String(length=500), nullable=False),
        sa.Column('anomaly_regions', sa.JSON(), nullable=True),
        sa.Column('inference_time_ms', sa.Float(), nullable=False),
        sa.Column('model_version', sa.String(length=50), nullable=False, server_default='v1.0.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['recording_id'], ['recordings.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('recording_id')
    )
    op.create_index(op.f('ix_analyses_recording_id'), 'analyses', ['recording_id'], unique=True)
    op.create_index(op.f('ix_analyses_predicted_class'), 'analyses', ['predicted_class'], unique=False)

    # 4. reports table
    op.create_table(
        'reports',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('recording_id', sa.String(length=36), nullable=False),
        sa.Column('analysis_id', sa.String(length=36), nullable=False),
        sa.Column('report_title', sa.String(length=255), nullable=False),
        sa.Column('patient_identifier', sa.String(length=100), nullable=False),
        sa.Column('primary_diagnosis', sa.String(length=255), nullable=False),
        sa.Column('severity', sa.String(length=50), nullable=False, server_default='normal'),
        sa.Column('clinical_summary', sa.Text(), nullable=False),
        sa.Column('recommendations', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='draft'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['recording_id'], ['recordings.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['analysis_id'], ['analyses.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reports_user_id'), 'reports', ['user_id'], unique=False)
    op.create_index(op.f('ix_reports_recording_id'), 'reports', ['recording_id'], unique=False)
    op.create_index(op.f('ix_reports_analysis_id'), 'reports', ['analysis_id'], unique=False)


def downgrade() -> None:
    op.drop_table('reports')
    op.drop_table('analyses')
    op.drop_table('recordings')
    op.drop_table('users')
