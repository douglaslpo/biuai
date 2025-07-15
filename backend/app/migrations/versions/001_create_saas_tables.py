"""Create SaaS tables

Revision ID: 001
Revises: 
Create Date: 2025-07-05 23:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON, ENUM

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Criar enum types
    op.execute("CREATE TYPE modulestatus AS ENUM ('active', 'inactive', 'deprecated', 'beta')")
    op.execute("CREATE TYPE permissioncategory AS ENUM ('user', 'data', 'admin', 'system', 'billing')")
    op.execute("CREATE TYPE userrole AS ENUM ('super_admin', 'tenant_admin', 'sub_admin', 'user')")
    
    # Criar tabela tenants
    op.create_table(
        'tenants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False, unique=True),
        sa.Column('domain', sa.String(255), nullable=True),
        sa.Column('settings', JSON, nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('max_users', sa.Integer(), default=10),
        sa.Column('max_storage_mb', sa.Integer(), default=1000),
        sa.Column('plan_type', sa.String(50), default='free'),
        sa.Column('billing_email', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Criar tabela roles
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(50), nullable=False, unique=True),
        sa.Column('display_name', sa.String(100), nullable=False),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('level', sa.Integer(), default=0),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_system', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Criar tabela permissions
    op.create_table(
        'permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('display_name', sa.String(100), nullable=False),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('module', sa.String(50), nullable=False),
        sa.Column('category', ENUM('user', 'data', 'admin', 'system', 'billing', name='permissioncategory'), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Criar tabela role_permissions
    op.create_table(
        'role_permissions',
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('permission_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('role_id', 'permission_id')
    )
    
    # Criar tabela modules
    op.create_table(
        'modules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(50), nullable=False, unique=True),
        sa.Column('display_name', sa.String(100), nullable=False),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('version', sa.String(20), default='1.0.0'),
        sa.Column('status', ENUM('active', 'inactive', 'deprecated', 'beta', name='modulestatus'), default='active'),
        sa.Column('dependencies', JSON, nullable=True),
        sa.Column('is_free', sa.Boolean(), default=True),
        sa.Column('price_monthly', sa.Float(), default=0.0),
        sa.Column('price_yearly', sa.Float(), default=0.0),
        sa.Column('max_records', sa.Integer(), default=1000),
        sa.Column('max_api_calls', sa.Integer(), default=10000),
        sa.Column('settings_schema', JSON, nullable=True),
        sa.Column('default_settings', JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Criar tabela tenant_modules
    op.create_table(
        'tenant_modules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('module_id', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('settings', JSON, nullable=True),
        sa.Column('custom_max_records', sa.Integer(), nullable=True),
        sa.Column('custom_max_api_calls', sa.Integer(), nullable=True),
        sa.Column('is_trial', sa.Boolean(), default=False),
        sa.Column('trial_ends_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()')),
        sa.Column('enabled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('enabled_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['module_id'], ['modules.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['enabled_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'module_id')
    )
    
    # Criar tabela module_usage
    op.create_table(
        'module_usage',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('module_id', sa.Integer(), nullable=False),
        sa.Column('records_count', sa.Integer(), default=0),
        sa.Column('api_calls_count', sa.Integer(), default=0),
        sa.Column('period_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('period_end', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()')),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['module_id'], ['modules.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Adicionar colunas na tabela users
    op.add_column('users', sa.Column('tenant_id', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('is_verified', sa.Boolean(), default=False))
    op.add_column('users', sa.Column('avatar_url', sa.String(500), nullable=True))
    op.add_column('users', sa.Column('phone', sa.String(20), nullable=True))
    op.add_column('users', sa.Column('timezone', sa.String(50), default='UTC'))
    op.add_column('users', sa.Column('language', sa.String(10), default='pt-BR'))
    op.add_column('users', sa.Column('settings', sa.String(), default='{}'))
    op.add_column('users', sa.Column('last_login', sa.DateTime(timezone=True), nullable=True))
    op.create_foreign_key('fk_users_tenant', 'users', 'tenants', ['tenant_id'], ['id'], ondelete='CASCADE')
    
    # Criar tabela user_roles
    op.create_table(
        'user_roles',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'role_id')
    )
    
    # Criar tabela user_permissions
    op.create_table(
        'user_permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('permission_id', sa.Integer(), nullable=False),
        sa.Column('granted', sa.Boolean(), default=True),
        sa.Column('context', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    # Drop tables
    op.drop_table('user_permissions')
    op.drop_table('user_roles')
    op.drop_table('module_usage')
    op.drop_table('tenant_modules')
    op.drop_table('role_permissions')
    op.drop_table('modules')
    op.drop_table('permissions')
    op.drop_table('roles')
    
    # Drop columns from users
    op.drop_constraint('fk_users_tenant', 'users', type_='foreignkey')
    op.drop_column('users', 'tenant_id')
    op.drop_column('users', 'is_verified')
    op.drop_column('users', 'avatar_url')
    op.drop_column('users', 'phone')
    op.drop_column('users', 'timezone')
    op.drop_column('users', 'language')
    op.drop_column('users', 'settings')
    op.drop_column('users', 'last_login')
    
    # Drop table tenants
    op.drop_table('tenants')
    
    # Drop enums
    op.execute('DROP TYPE modulestatus')
    op.execute('DROP TYPE permissioncategory')
    op.execute('DROP TYPE userrole') 