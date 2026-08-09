"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2026-08-08 17:44:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_admin', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # Create device_type enum
    device_type_enum = postgresql.ENUM('router', 'switch', 'firewall', 'wireless', 'load_balancer', 'other', name='devicetype')
    device_type_enum.create(op.get_bind())

    # Create device_status enum
    device_status_enum = postgresql.ENUM('online', 'offline', 'unknown', name='devicestatus')
    device_status_enum.create(op.get_bind())

    # Create connection_protocol enum
    connection_protocol_enum = postgresql.ENUM('ssh', 'telnet', name='connectionprotocol')
    connection_protocol_enum.create(op.get_bind())

    # Create devices table
    op.create_table(
        'devices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=False),
        sa.Column('device_type', postgresql.ENUM(name='devicetype'), nullable=True),
        sa.Column('vendor', sa.String(length=100), nullable=True),
        sa.Column('model', sa.String(length=100), nullable=True),
        sa.Column('protocol', postgresql.ENUM(name='connectionprotocol'), nullable=True),
        sa.Column('port', sa.Integer(), nullable=True),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('password', sa.Text(), nullable=False),
        sa.Column('enable_password', sa.Text(), nullable=True),
        sa.Column('status', postgresql.ENUM(name='devicestatus'), nullable=True),
        sa.Column('last_backup', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_seen', sa.DateTime(timezone=True), nullable=True),
        sa.Column('backup_interval', sa.Integer(), nullable=True),
        sa.Column('auto_backup_enabled', sa.Boolean(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('tags', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_devices_id'), 'devices', ['id'], unique=False)
    op.create_index(op.f('ix_devices_ip_address'), 'devices', ['ip_address'], unique=True)
    op.create_index(op.f('ix_devices_name'), 'devices', ['name'], unique=False)

    # Create configurations table
    op.create_table(
        'configurations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('device_id', sa.Integer(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('config_hash', sa.String(length=64), nullable=False),
        sa.Column('file_path', sa.String(length=512), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('is_changed', sa.Boolean(), nullable=True),
        sa.Column('change_summary', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['device_id'], ['devices.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_configurations_config_hash'), 'configurations', ['config_hash'], unique=False)
    op.create_index(op.f('ix_configurations_id'), 'configurations', ['id'], unique=False)

    # Create backup_jobs table
    op.create_table(
        'backup_jobs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('device_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['device_id'], ['devices.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_backup_jobs_id'), 'backup_jobs', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_backup_jobs_id'), table_name='backup_jobs')
    op.drop_table('backup_jobs')
    
    op.drop_index(op.f('ix_configurations_id'), table_name='configurations')
    op.drop_index(op.f('ix_configurations_config_hash'), table_name='configurations')
    op.drop_table('configurations')
    
    op.drop_index(op.f('ix_devices_name'), table_name='devices')
    op.drop_index(op.f('ix_devices_ip_address'), table_name='devices')
    op.drop_index(op.f('ix_devices_id'), table_name='devices')
    op.drop_table('devices')
    
    # Drop enums
    postgresql.ENUM(name='connectionprotocol').drop(op.get_bind())
    postgresql.ENUM(name='devicestatus').drop(op.get_bind())
    postgresql.ENUM(name='devicetype').drop(op.get_bind())
    
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
