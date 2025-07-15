"""
Script para gerar dados de teste para o sistema multi-tenant.
"""

import asyncio
import random
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from faker import Faker

from app.database import get_db
from app.models.tenant import Tenant
from app.models.role import Role, Permission
from app.models.module import Module, TenantModule, ModuleStatus
from app.models.user import User
from app.models.financeiro import Categoria, Conta, Lancamento, MetaFinanceira, TipoLancamento, StatusMeta
from app.models.fii import FII, AnaliseFII, TransacaoFII
from app.core.security import get_password_hash

# Configurar Faker para pt_BR
fake = Faker('pt_BR')

async def create_modules(db: AsyncSession) -> List[Module]:
    """Cria módulos do sistema"""
    
    modules = [
        Module(
            name="core",
            display_name="Core - Sistema Base",
            description="Funcionalidades básicas do sistema",
            version="1.0.0",
            is_core=True,
            is_paid=False,
            is_active=True,
            requires_setup=False,
            dependencies=[],
            default_settings={
                "theme": "light",
                "language": "pt-BR",
                "timezone": "America/Sao_Paulo"
            },
            features=[
                {
                    "name": "auth",
                    "title": "Autenticação",
                    "description": "Sistema de login e controle de acesso"
                },
                {
                    "name": "dashboard",
                    "title": "Dashboard Básico",
                    "description": "Visão geral do sistema"
                }
            ]
        ),
        Module(
            name="financial",
            display_name="Financial - Gestão Financeira",
            description="Controle financeiro completo",
            version="1.0.0",
            is_core=False,
            is_paid=False,
            is_active=True,
            requires_setup=True,
            dependencies=["core"],
            default_settings={
                "currency": "BRL",
                "decimal_places": 2
            },
            features=[
                {
                    "name": "transactions",
                    "title": "Transações",
                    "description": "Controle de receitas e despesas"
                },
                {
                    "name": "categories",
                    "title": "Categorias",
                    "description": "Organização por categorias"
                }
            ],
            price_monthly=0,
            price_yearly=0
        ),
        Module(
            name="investments",
            display_name="Investments - Gestão de Investimentos",
            description="Análise e gestão de investimentos",
            version="1.0.0",
            is_core=False,
            is_paid=True,
            is_active=True,
            requires_setup=True,
            dependencies=["core", "financial"],
            default_settings={
                "max_assets": 100,
                "enable_alerts": True
            },
            features=[
                {
                    "name": "portfolio",
                    "title": "Carteira",
                    "description": "Gestão de carteira de investimentos"
                },
                {
                    "name": "analysis",
                    "title": "Análises",
                    "description": "Análises técnicas e fundamentalistas"
                }
            ],
            price_monthly=49.90,
            price_yearly=499.90,
            trial_days=30
        ),
        Module(
            name="ai_insights",
            display_name="AI Insights - Análises Inteligentes",
            description="Insights com inteligência artificial",
            version="1.0.0",
            is_core=False,
            is_paid=True,
            is_active=True,
            requires_setup=False,
            dependencies=["core"],
            default_settings={
                "model": "gpt-4",
                "max_tokens": 1000
            },
            features=[
                {
                    "name": "predictions",
                    "title": "Previsões",
                    "description": "Previsões baseadas em IA"
                },
                {
                    "name": "recommendations",
                    "title": "Recomendações",
                    "description": "Recomendações personalizadas"
                }
            ],
            price_monthly=99.90,
            price_yearly=999.90,
            trial_days=15
        )
    ]
    
    for module in modules:
        existing = await db.execute(select(Module).filter(Module.name == module.name))
        if not existing.scalars().first():
            db.add(module)
    
    await db.commit()
    
    return await db.execute(select(Module))

async def create_tenant(
    db: AsyncSession,
    name: str,
    modules: List[Module],
    is_trial: bool = True
) -> Tenant:
    """Cria um tenant com módulos"""
    
    # Criar tenant
    tenant = Tenant(
        name=name,
        slug=name.lower().replace(" ", "-"),
        domain=f"{name.lower().replace(' ', '-')}.biuai.com",
        is_active=True,
        settings={
            "theme": "light",
            "language": "pt-BR",
            "timezone": "America/Sao_Paulo"
        },
        features={
            "enable_ai": True,
            "enable_alerts": True
        },
        max_users=5,
        max_storage_gb=1,
        trial_ends_at=datetime.utcnow() + timedelta(days=30) if is_trial else None,
        metadata={
            "created_by": "test_data",
            "industry": fake.company_suffix(),
            "size": random.choice(["small", "medium", "large"])
        }
    )
    
    db.add(tenant)
    await db.commit()
    await db.refresh(tenant)
    
    # Criar admin
    admin = User(
        email=f"admin@{tenant.slug}.com",
        hashed_password=get_password_hash("admin123"),
        is_active=True,
        is_superuser=False,
        tenant_id=tenant.id,
        full_name=f"Admin {tenant.name}",
        role="TENANT_ADMIN"
    )
    
    db.add(admin)
    
    # Criar usuários
    for i in range(3):
        user = User(
            email=f"user{i+1}@{tenant.slug}.com",
            hashed_password=get_password_hash("user123"),
            is_active=True,
            is_superuser=False,
            tenant_id=tenant.id,
            full_name=fake.name(),
            role="USER"
        )
        db.add(user)
    
    await db.commit()
    
    # Ativar módulos
    for module in modules:
        if module.is_core or not module.is_paid:
            tenant_module = TenantModule(
                tenant_id=tenant.id,
                module_id=module.id,
                is_active=True,
                is_configured=True,
                settings=module.default_settings,
                features_enabled=[f["name"] for f in module.features],
                activated_at=datetime.utcnow()
            )
        elif is_trial and random.random() > 0.5:
            tenant_module = TenantModule(
                tenant_id=tenant.id,
                module_id=module.id,
                is_active=True,
                is_configured=True,
                settings=module.default_settings,
                features_enabled=[f["name"] for f in module.features],
                activated_at=datetime.utcnow(),
                trial_ends_at=datetime.utcnow() + timedelta(days=module.trial_days)
            )
        else:
            continue
        
        db.add(tenant_module)
    
    await db.commit()
    
    return tenant

async def create_fiis(db: AsyncSession, tenant: Tenant) -> List[FII]:
    """Cria FIIs para um tenant"""
    
    fiis_data = [
        {
            "codigo": "HGLG11",
            "nome": "CGHG Logística",
            "segmento": "Logística",
            "preco_atual": 180.50,
            "dividend_yield": 7.5,
            "patrimonio_liquido": 2_500_000_000,
            "valor_patrimonial": 165.30,
            "liquidez_diaria": 1_500_000,
            "rentabilidade_mes": 2.1,
            "rentabilidade_ano": 15.4,
            "rentabilidade_12m": 18.2,
            "quantidade_ativos": 15,
            "vacancia_media": 2.5
        },
        {
            "codigo": "XPLG11",
            "nome": "XP Log",
            "segmento": "Logística",
            "preco_atual": 120.80,
            "dividend_yield": 8.2,
            "patrimonio_liquido": 1_800_000_000,
            "valor_patrimonial": 110.20,
            "liquidez_diaria": 900_000,
            "rentabilidade_mes": 1.8,
            "rentabilidade_ano": 12.5,
            "rentabilidade_12m": 16.8,
            "quantidade_ativos": 12,
            "vacancia_media": 3.2
        },
        {
            "codigo": "HGRE11",
            "nome": "CGHG Real Estate",
            "segmento": "Lajes Corporativas",
            "preco_atual": 145.30,
            "dividend_yield": 6.8,
            "patrimonio_liquido": 2_100_000_000,
            "valor_patrimonial": 135.40,
            "liquidez_diaria": 1_200_000,
            "rentabilidade_mes": 1.5,
            "rentabilidade_ano": 11.2,
            "rentabilidade_12m": 14.5,
            "quantidade_ativos": 8,
            "vacancia_media": 8.5
        }
    ]
    
    fiis = []
    for fii_data in fiis_data:
        fii = FII(
            tenant_id=tenant.id,
            **fii_data,
            quantidade=random.randint(10, 100),
            preco_medio=fii_data["preco_atual"] * random.uniform(0.9, 1.1),
            favorito=random.random() > 0.7
        )
        db.add(fii)
        fiis.append(fii)
    
    await db.commit()
    
    # Criar análises
    for fii in fiis:
        analise = AnaliseFII(
            tenant_id=tenant.id,
            fii_id=fii.id,
            tendencia=random.choice(["ALTA", "BAIXA", "LATERAL"]),
            rsi=random.uniform(30, 70),
            suporte=fii.preco_atual * 0.9,
            resistencia=fii.preco_atual * 1.1,
            score_liquidez=random.uniform(60, 100),
            score_rentabilidade=random.uniform(60, 100),
            score_risco=random.uniform(60, 100),
            score_geral=random.uniform(60, 100),
            recomendacao=random.choice(["COMPRAR", "VENDER", "MANTER"]),
            confianca=random.uniform(0.7, 1.0),
            explicacao="Análise baseada em indicadores técnicos e fundamentalistas"
        )
        db.add(analise)
    
    # Criar transações
    for fii in fiis:
        for _ in range(random.randint(2, 5)):
            data = datetime.utcnow() - timedelta(days=random.randint(1, 365))
            preco = fii.preco_atual * random.uniform(0.8, 1.2)
            quantidade = random.randint(5, 20)
            
            transacao = TransacaoFII(
                tenant_id=tenant.id,
                fii_id=fii.id,
                tipo=random.choice(["COMPRA", "VENDA"]),
                data=data,
                quantidade=quantidade,
                preco=preco,
                corretagem=random.uniform(5, 15),
                emolumentos=preco * quantidade * 0.0025,
                notas=f"Transação de {'compra' if transacao.tipo == 'COMPRA' else 'venda'}"
            )
            db.add(transacao)
    
    await db.commit()
    
    return fiis

async def generate_test_data():
    """Gerar todos os dados de teste"""
    print("🚀 Gerando dados de teste para o sistema BIUAI...")
    
    async for db in get_db():
        try:
            # 1. Criar módulos
            print("Criando módulos...")
            modules = await create_modules(db)
            
            # 2. Criar tenants
            print("Criando tenants...")
            tenants = []
            for i in range(5):
                name = f"{fake.company()} {fake.company_suffix()}"
                tenant = await create_tenant(
                    db,
                    name=name,
                    modules=modules,
                    is_trial=random.random() > 0.3
                )
                tenants.append(tenant)
                print(f"Tenant criado: {tenant.name}")
            
            # 3. Criar FIIs para cada tenant
            print("Criando FIIs...")
            for tenant in tenants:
                fiis = await create_fiis(db, tenant)
                print(f"FIIs criados para {tenant.name}: {len(fiis)}")
            
            print("✅ Dados de teste gerados com sucesso!")
            print(f"📊 Resumo:")
            print(f"- {len(tenants)} tenants criados")
            print(f"- FIIs criados para todos os tenants")
            
        except Exception as e:
            print(f"❌ Erro ao gerar dados: {e}")
            await db.rollback()
            raise
        finally:
            await db.close()
        break

if __name__ == "__main__":
    asyncio.run(generate_test_data()) 