"""
Script para gerar dados sintéticos de teste para o sistema BIUAI
"""

import asyncio
import random
from datetime import datetime, timezone, timedelta
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models.tenant import Tenant
from app.models.role import Role, Permission
from app.models.module import Module, TenantModule, ModuleStatus
from app.models.user import User
from app.models.financeiro import Categoria, Conta, Lancamento, MetaFinanceira, TipoLancamento, StatusMeta
from app.models.fii import FII

# Configurar Faker para pt_BR
fake = Faker('pt_BR')

async def create_test_tenants(db: AsyncSession, count: int = 5) -> list[Tenant]:
    """Criar tenants de teste"""
    tenants = []
    plan_types = ['free', 'basic', 'premium', 'enterprise']
    
    for i in range(count):
        company = fake.company()
        tenant = Tenant(
            name=company,
            slug=f"{company.lower().replace(' ', '-')}-{i}",
            domain=f"{company.lower().replace(' ', '')}.biuai.com.br",
            settings={
                "theme": random.choice(['default', 'dark', 'light']),
                "timezone": "America/Sao_Paulo",
                "language": "pt-BR",
                "features": {
                    "multi_currency": bool(random.getrandbits(1)),
                    "advanced_analytics": bool(random.getrandbits(1)),
                    "ai_insights": bool(random.getrandbits(1))
                }
            },
            is_active=True,
            max_users=random.choice([5, 10, 20, 50, 100]),
            max_storage_mb=random.choice([1000, 2000, 5000, 10000]),
            plan_type=random.choice(plan_types),
            billing_email=fake.company_email()
        )
        db.add(tenant)
        tenants.append(tenant)
    
    await db.commit()
    return tenants

async def create_test_users(db: AsyncSession, tenants: list[Tenant], count_per_tenant: int = 5) -> list[User]:
    """Criar usuários de teste para cada tenant"""
    users = []
    
    # Buscar roles
    result = await db.execute(select(Role))
    roles = {role.name: role for role in result.scalars().all()}
    
    for tenant in tenants:
        # Criar admin do tenant
        admin = User(
            full_name=fake.name(),
            email=f"admin@{tenant.domain}",
            hashed_password=User.gerar_hash_senha("admin123"),
            is_active=True,
            is_superuser=False,
            is_verified=True,
            tenant_id=tenant.id,
            avatar_url=fake.image_url(),
            phone=fake.phone_number(),
            timezone="America/Sao_Paulo",
            language="pt-BR",
            settings="{}"
        )
        admin.roles.append(roles['tenant_admin'])
        db.add(admin)
        users.append(admin)
        
        # Criar sub_admin
        sub_admin = User(
            full_name=fake.name(),
            email=f"subadmin@{tenant.domain}",
            hashed_password=User.gerar_hash_senha("admin123"),
            is_active=True,
            is_verified=True,
            tenant_id=tenant.id,
            avatar_url=fake.image_url(),
            phone=fake.phone_number(),
            timezone="America/Sao_Paulo",
            language="pt-BR",
            settings="{}"
        )
        sub_admin.roles.append(roles['sub_admin'])
        db.add(sub_admin)
        users.append(sub_admin)
        
        # Criar usuários normais
        for i in range(count_per_tenant):
            user = User(
                full_name=fake.name(),
                email=f"user{i}@{tenant.domain}",
                hashed_password=User.gerar_hash_senha("user123"),
                is_active=True,
                is_verified=bool(random.getrandbits(1)),
                tenant_id=tenant.id,
                avatar_url=fake.image_url(),
                phone=fake.phone_number(),
                timezone="America/Sao_Paulo",
                language="pt-BR",
                settings="{}"
            )
            user.roles.append(roles['user'])
            db.add(user)
            users.append(user)
    
    await db.commit()
    return users

async def create_test_financial_data(db: AsyncSession, users: list[User]):
    """Criar dados financeiros de teste"""
    
    # Criar categorias
    categorias_receita = [
        "Salário", "Investimentos", "Freelance", "Aluguel", 
        "Dividendos", "Bônus", "Vendas", "Outros"
    ]
    categorias_despesa = [
        "Alimentação", "Transporte", "Moradia", "Saúde",
        "Educação", "Lazer", "Vestuário", "Impostos"
    ]
    
    categorias = []
    for user in users:
        for cat_nome in categorias_receita:
            categoria = Categoria(
                nome=cat_nome,
                tipo=TipoLancamento.RECEITA,
                descricao=f"Categoria de receita: {cat_nome}",
                user_id=user.id
            )
            db.add(categoria)
            categorias.append(categoria)
        
        for cat_nome in categorias_despesa:
            categoria = Categoria(
                nome=cat_nome,
                tipo=TipoLancamento.DESPESA,
                descricao=f"Categoria de despesa: {cat_nome}",
                user_id=user.id
            )
            db.add(categoria)
            categorias.append(categoria)
    
    await db.commit()
    
    # Criar contas
    contas = []
    tipos_conta = ["CORRENTE", "POUPANCA", "INVESTIMENTO"]
    bancos = ["Nubank", "Itaú", "Bradesco", "Santander", "Inter"]
    
    for user in users:
        for _ in range(random.randint(1, 3)):
            conta = Conta(
                nome=f"Conta {random.choice(tipos_conta)}",
                banco=random.choice(bancos),
                numero_conta=str(random.randint(10000, 99999)),
                agencia=str(random.randint(1000, 9999)),
                tipo_conta=random.choice(tipos_conta),
                saldo_inicial=round(random.uniform(1000, 10000), 2),
                saldo_atual=round(random.uniform(1000, 10000), 2),
                ativa=True,
                user_id=user.id
            )
            db.add(conta)
            contas.append(conta)
    
    await db.commit()
    
    # Criar lançamentos
    for user in users:
        user_categorias = [c for c in categorias if c.user_id == user.id]
        user_contas = [c for c in contas if c.user_id == user.id]
        
        # Gerar lançamentos dos últimos 3 meses
        start_date = datetime.now(timezone.utc) - timedelta(days=90)
        
        for _ in range(random.randint(50, 100)):
            categoria = random.choice(user_categorias)
            conta = random.choice(user_contas)
            
            lancamento = Lancamento(
                descricao=fake.sentence(),
                valor=round(random.uniform(10, 1000), 2),
                tipo=categoria.tipo,
                data_lancamento=fake.date_time_between(
                    start_date=start_date,
                    end_date=datetime.now(timezone.utc),
                    tzinfo=timezone.utc
                ),
                user_id=user.id,
                categoria_id=categoria.id,
                conta_id=conta.id
            )
            db.add(lancamento)
    
    await db.commit()
    
    # Criar metas financeiras
    for user in users:
        user_categorias = [c for c in categorias if c.user_id == user.id]
        
        for _ in range(random.randint(2, 5)):
            categoria = random.choice(user_categorias)
            valor_meta = round(random.uniform(1000, 10000), 2)
            
            meta = MetaFinanceira(
                titulo=fake.sentence(),
                descricao=fake.text(),
                valor_meta=valor_meta,
                valor_atual=round(random.uniform(0, valor_meta), 2),
                data_inicio=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 30)),
                data_fim=datetime.now(timezone.utc) + timedelta(days=random.randint(30, 365)),
                status=random.choice(list(StatusMeta)),
                user_id=user.id,
                categoria_id=categoria.id
            )
            db.add(meta)
    
    await db.commit()

async def create_test_investment_data(db: AsyncSession, users: list[User]):
    """Criar dados de investimentos de teste"""
    
    fiis_data = [
        {
            "codigo": "HGLG11",
            "nome": "CGHG Logística",
            "segmento": "Logística",
            "preco_atual": 180.50,
            "dividend_yield": 0.65,
            "patrimonio_liquido": 2500000000,
            "valor_patrimonial": 170.20,
            "liquidez_diaria": 1500000
        },
        {
            "codigo": "KNRI11",
            "nome": "Kinea Renda Imobiliária",
            "segmento": "Escritórios",
            "preco_atual": 142.30,
            "dividend_yield": 0.72,
            "patrimonio_liquido": 3800000000,
            "valor_patrimonial": 138.90,
            "liquidez_diaria": 2100000
        },
        {
            "codigo": "MXRF11",
            "nome": "Maxi Renda",
            "segmento": "Títulos e Val. Mob.",
            "preco_atual": 10.20,
            "dividend_yield": 0.95,
            "patrimonio_liquido": 1200000000,
            "valor_patrimonial": 9.80,
            "liquidez_diaria": 3500000
        },
        {
            "codigo": "XPLG11",
            "nome": "XP Log",
            "segmento": "Logística",
            "preco_atual": 115.80,
            "dividend_yield": 0.68,
            "patrimonio_liquido": 1800000000,
            "valor_patrimonial": 112.40,
            "liquidez_diaria": 900000
        },
        {
            "codigo": "VISC11",
            "nome": "Vinci Shopping Centers",
            "segmento": "Shoppings",
            "preco_atual": 98.40,
            "dividend_yield": 0.75,
            "patrimonio_liquido": 2200000000,
            "valor_patrimonial": 95.60,
            "liquidez_diaria": 1200000
        }
    ]
    
    for user in users:
        # Cada usuário terá entre 0 e 5 FIIs aleatórios
        for _ in range(random.randint(0, 5)):
            fii_data = random.choice(fiis_data)
            fii = FII(
                codigo=fii_data["codigo"],
                nome=fii_data["nome"],
                segmento=fii_data["segmento"],
                preco_atual=fii_data["preco_atual"],
                dividend_yield=fii_data["dividend_yield"],
                patrimonio_liquido=fii_data["patrimonio_liquido"],
                valor_patrimonial=fii_data["valor_patrimonial"],
                liquidez_diaria=fii_data["liquidez_diaria"],
                user_id=user.id
            )
            db.add(fii)
    
    await db.commit()

async def create_test_module_data(db: AsyncSession, tenants: list[Tenant]):
    """Criar dados de módulos e uso para teste"""
    
    # Buscar módulos
    result = await db.execute(select(Module))
    modules = result.scalars().all()
    
    for tenant in tenants:
        # Atribuir módulos aleatoriamente
        for module in modules:
            if random.random() > 0.3:  # 70% de chance de ter o módulo
                tenant_module = TenantModule(
                    tenant_id=tenant.id,
                    module_id=module.id,
                    is_active=True,
                    settings=module.default_settings or {},
                    custom_max_records=None,
                    custom_max_api_calls=None,
                    is_trial=not module.is_free,
                    trial_ends_at=datetime.now(timezone.utc) + timedelta(days=30) if not module.is_free else None,
                    enabled_at=datetime.now(timezone.utc)
                )
                db.add(tenant_module)
    
    await db.commit()

async def generate_test_data():
    """Gerar todos os dados de teste"""
    print("🚀 Gerando dados de teste para o sistema BIUAI...")
    
    async for db in get_db():
        try:
            # 1. Criar tenants
            print("Criando tenants...")
            tenants = await create_test_tenants(db, count=5)
            
            # 2. Criar usuários
            print("Criando usuários...")
            users = await create_test_users(db, tenants, count_per_tenant=5)
            
            # 3. Criar dados financeiros
            print("Criando dados financeiros...")
            await create_test_financial_data(db, users)
            
            # 4. Criar dados de investimentos
            print("Criando dados de investimentos...")
            await create_test_investment_data(db, users)
            
            # 5. Criar dados de módulos
            print("Criando dados de módulos...")
            await create_test_module_data(db, tenants)
            
            print("✅ Dados de teste gerados com sucesso!")
            print(f"📊 Resumo:")
            print(f"- {len(tenants)} tenants criados")
            print(f"- {len(users)} usuários criados")
            print(f"- Dados financeiros gerados para todos os usuários")
            print(f"- Dados de investimentos gerados para todos os usuários")
            print(f"- Módulos atribuídos aos tenants")
            
        except Exception as e:
            print(f"❌ Erro ao gerar dados: {e}")
            await db.rollback()
            raise
        finally:
            await db.close()
        break

if __name__ == "__main__":
    asyncio.run(generate_test_data()) 