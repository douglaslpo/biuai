"""add tenant support

Revision ID: 20250705_01
Revises: 
Create Date: 2025-07-05 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250705_01'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Criar tabela de tenants
    op.create_table(
        'tenants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False, unique=True),
        sa.Column('domain', sa.String(255), nullable=True, unique=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('settings', postgresql.JSONB(), nullable=False, default={}),
        sa.Column('features', postgresql.JSONB(), nullable=False, default={}),
        sa.Column('max_users', sa.Integer(), nullable=False, default=5),
        sa.Column('max_storage_gb', sa.Integer(), nullable=False, default=1),
        sa.Column('subscription_ends_at', sa.DateTime(), nullable=True),
        sa.Column('trial_ends_at', sa.DateTime(), nullable=True),
        sa.Column('last_billing_at', sa.DateTime(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=False, default={}),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Criar tabela de módulos
    op.create_table(
        'modules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(50), nullable=False, unique=True),
        sa.Column('display_name', sa.String(100), nullable=False),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('version', sa.String(20), nullable=False),
        sa.Column('is_core', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_paid', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('requires_setup', sa.Boolean(), nullable=False, default=False),
        sa.Column('dependencies', postgresql.JSONB(), nullable=False, default=[]),
        sa.Column('default_settings', postgresql.JSONB(), nullable=False, default={}),
        sa.Column('features', postgresql.JSONB(), nullable=False, default=[]),
        sa.Column('price_monthly', sa.Float(), nullable=True),
        sa.Column('price_yearly', sa.Float(), nullable=True),
        sa.Column('trial_days', sa.Integer(), nullable=False, default=30),
        sa.Column('max_users', sa.Integer(), nullable=True),
        sa.Column('max_storage_gb', sa.Integer(), nullable=True),
        sa.Column('api_rate_limit', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Criar tabela de assinaturas de módulos
    op.create_table(
        'tenant_modules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('module_id', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_configured', sa.Boolean(), nullable=False, default=False),
        sa.Column('settings', postgresql.JSONB(), nullable=False, default={}),
        sa.Column('features_enabled', postgresql.JSONB(), nullable=False, default=[]),
        sa.Column('activated_at', sa.DateTime(), nullable=False),
        sa.Column('trial_ends_at', sa.DateTime(), nullable=True),
        sa.Column('subscription_ends_at', sa.DateTime(), nullable=True),
        sa.Column('last_billing_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.ForeignKeyConstraint(['module_id'], ['modules.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Adicionar tenant_id nas tabelas existentes
    op.add_column('fiis', sa.Column('tenant_id', sa.Integer(), nullable=True))
    op.add_column('fiis', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    op.create_foreign_key('fk_fiis_tenant_id', 'fiis', 'tenants', ['tenant_id'], ['id'])
    
    op.add_column('analises_fii', sa.Column('tenant_id', sa.Integer(), nullable=True))
    op.add_column('analises_fii', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    op.create_foreign_key('fk_analises_fii_tenant_id', 'analises_fii', 'tenants', ['tenant_id'], ['id'])
    
    # Criar tabela de transações
    op.create_table(
        'transacoes_fii',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('fii_id', sa.Integer(), nullable=False),
        sa.Column('tipo', sa.String(10), nullable=False),
        sa.Column('data', sa.DateTime(), nullable=False),
        sa.Column('quantidade', sa.Integer(), nullable=False),
        sa.Column('preco', sa.Float(), nullable=False),
        sa.Column('corretagem', sa.Float(), nullable=False, default=0),
        sa.Column('emolumentos', sa.Float(), nullable=False, default=0),
        sa.Column('notas', sa.String(500), nullable=True),
        sa.Column('comprovante_url', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.ForeignKeyConstraint(['fii_id'], ['fiis.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Criar índices
    op.create_index('ix_tenants_slug', 'tenants', ['slug'])
    op.create_index('ix_tenants_domain', 'tenants', ['domain'])
    op.create_index('ix_modules_name', 'modules', ['name'])
    op.create_index('ix_tenant_modules_tenant_id', 'tenant_modules', ['tenant_id'])
    op.create_index('ix_tenant_modules_module_id', 'tenant_modules', ['module_id'])
    op.create_index('ix_fiis_tenant_id', 'fiis', ['tenant_id'])
    op.create_index('ix_analises_fii_tenant_id', 'analises_fii', ['tenant_id'])
    op.create_index('ix_transacoes_fii_tenant_id', 'transacoes_fii', ['tenant_id'])
    op.create_index('ix_transacoes_fii_fii_id', 'transacoes_fii', ['fii_id'])

def downgrade():
    # Remover índices
    op.drop_index('ix_transacoes_fii_fii_id')
    op.drop_index('ix_transacoes_fii_tenant_id')
    op.drop_index('ix_analises_fii_tenant_id')
    op.drop_index('ix_fiis_tenant_id')
    op.drop_index('ix_tenant_modules_module_id')
    op.drop_index('ix_tenant_modules_tenant_id')
    op.drop_index('ix_modules_name')
    op.drop_index('ix_tenants_domain')
    op.drop_index('ix_tenants_slug')
    
    # Remover foreign keys
    op.drop_constraint('fk_analises_fii_tenant_id', 'analises_fii')
    op.drop_constraint('fk_fiis_tenant_id', 'fiis')
    
    # Remover colunas
    op.drop_column('analises_fii', 'deleted_at')
    op.drop_column('analises_fii', 'tenant_id')
    op.drop_column('fiis', 'deleted_at')
    op.drop_column('fiis', 'tenant_id')
    
    # Remover tabelas
    op.drop_table('transacoes_fii')
    op.drop_table('tenant_modules')
    op.drop_table('modules')
    op.drop_table('tenants') 