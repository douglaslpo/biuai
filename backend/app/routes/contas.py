from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, timedelta
from app.api.deps import get_db, get_current_user
from app.models.financeiro import Conta, Lancamento, TipoLancamento
from app.schemas.financeiro import (
    ContaCreate, 
    ContaResponse, 
    ContaUpdate,
    ResumoContasResponse
)
from app.models.user import User
from sqlalchemy import func, and_, select, or_
from decimal import Decimal

router = APIRouter()

@router.get("/", response_model=List[ContaResponse])
async def listar_contas(
    skip: int = 0,
    limit: int = 100,
    ativa: Optional[str] = None,
    tipo_conta: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista todas as contas bancárias do usuário
    """
    try:
        query = select(Conta).where(Conta.user_id == current_user.id)
        
        if ativa:
            query = query.where(Conta.ativa == ativa)
        
        if tipo_conta:
            query = query.where(Conta.tipo_conta == tipo_conta)
        
        query = query.order_by(Conta.banco, Conta.nome).offset(skip).limit(limit)
        result = await db.execute(query)
        contas = result.scalars().all()
        
        # Calcular dados adicionais para cada conta
        contas_response = []
        for conta in contas:
            # Calcular estatísticas de lançamentos
            query_lancamentos = select(Lancamento).where(Lancamento.conta_id == conta.id)
            result_lancamentos = await db.execute(query_lancamentos)
            lancamentos = result_lancamentos.scalars().all()
            
            total_receitas = sum([l.valor for l in lancamentos if l.tipo == TipoLancamento.RECEITA])
            total_despesas = sum([abs(l.valor) for l in lancamentos if l.tipo == TipoLancamento.DESPESA])
            total_lancamentos = len(lancamentos)
            
            # Calcular saldo atual (saldo inicial + receitas - despesas)
            saldo_atual = conta.saldo_inicial + total_receitas - total_despesas
            
            # Atualizar saldo atual na conta
            conta.saldo_atual = saldo_atual
            
            conta_dict = {
                **conta.__dict__,
                "total_receitas": total_receitas,
                "total_despesas": total_despesas,
                "total_lancamentos": total_lancamentos,
                "saldo_atual": saldo_atual
            }
            contas_response.append(conta_dict)
        
        # Salvar atualizações de saldo
        await db.commit()
        
        return contas_response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar contas: {str(e)}")

@router.post("/", response_model=ContaResponse)
async def criar_conta(
    conta: ContaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cria uma nova conta bancária
    """
    try:
        # Verificar se já existe conta com mesmo nome/banco para o usuário
        query = select(Conta).where(
            and_(
                Conta.user_id == current_user.id,
                Conta.nome == conta.nome,
                Conta.banco == conta.banco
            )
        )
        result = await db.execute(query)
        conta_existente = result.scalar_one_or_none()
        
        if conta_existente:
            raise HTTPException(
                status_code=400,
                detail="Já existe uma conta com este nome neste banco"
            )
        
        nova_conta = Conta(
            **conta.dict(),
            user_id=current_user.id,
            saldo_atual=conta.saldo_inicial  # Inicializar saldo atual
        )
        db.add(nova_conta)
        await db.commit()
        await db.refresh(nova_conta)
        
        # Retornar com campos calculados iniciais
        conta_response = {
            **nova_conta.__dict__,
            "total_receitas": 0.0,
            "total_despesas": 0.0,
            "total_lancamentos": 0
        }
        
        return conta_response
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao criar conta: {str(e)}")

@router.get("/{conta_id}", response_model=ContaResponse)
async def obter_conta(
    conta_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtém uma conta específica por ID
    """
    try:
        query = select(Conta).where(
            and_(
                Conta.id == conta_id,
                Conta.user_id == current_user.id
            )
        )
        result = await db.execute(query)
        conta = result.scalar_one_or_none()
        
        if not conta:
            raise HTTPException(status_code=404, detail="Conta não encontrada")
        
        # Calcular estatísticas de lançamentos
        query_lancamentos = select(Lancamento).where(Lancamento.conta_id == conta.id)
        result_lancamentos = await db.execute(query_lancamentos)
        lancamentos = result_lancamentos.scalars().all()
        
        total_receitas = sum([l.valor for l in lancamentos if l.tipo == TipoLancamento.RECEITA])
        total_despesas = sum([abs(l.valor) for l in lancamentos if l.tipo == TipoLancamento.DESPESA])
        total_lancamentos = len(lancamentos)
        
        # Calcular saldo atual
        saldo_atual = conta.saldo_inicial + total_receitas - total_despesas
        conta.saldo_atual = saldo_atual
        await db.commit()
        
        conta_response = {
            **conta.__dict__,
            "total_receitas": total_receitas,
            "total_despesas": total_despesas,
            "total_lancamentos": total_lancamentos,
            "saldo_atual": saldo_atual
        }
        
        return conta_response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter conta: {str(e)}")

@router.put("/{conta_id}", response_model=ContaResponse)
async def atualizar_conta(
    conta_id: int,
    conta_update: ContaUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Atualiza uma conta existente
    """
    try:
        # Buscar conta
        query = select(Conta).where(
            and_(
                Conta.id == conta_id,
                Conta.user_id == current_user.id
            )
        )
        result = await db.execute(query)
        conta = result.scalar_one_or_none()
        
        if not conta:
            raise HTTPException(status_code=404, detail="Conta não encontrada")
        
        # Verificar se novo nome/banco já existe (se estiver sendo alterado)
        if (conta_update.nome and conta_update.nome != conta.nome) or \
           (conta_update.banco and conta_update.banco != conta.banco):
            nome_check = conta_update.nome or conta.nome
            banco_check = conta_update.banco or conta.banco
            
            query_nome = select(Conta).where(
                and_(
                    Conta.user_id == current_user.id,
                    Conta.nome == nome_check,
                    Conta.banco == banco_check,
                    Conta.id != conta_id
                )
            )
            result_nome = await db.execute(query_nome)
            conta_existente = result_nome.scalar_one_or_none()
            
            if conta_existente:
                raise HTTPException(
                    status_code=400,
                    detail="Já existe uma conta com este nome neste banco"
                )
        
        # Atualizar campos
        update_data = conta_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(conta, field, value)
        
        await db.commit()
        await db.refresh(conta)
        
        # Calcular estatísticas
        query_lancamentos = select(Lancamento).where(Lancamento.conta_id == conta.id)
        result_lancamentos = await db.execute(query_lancamentos)
        lancamentos = result_lancamentos.scalars().all()
        
        total_receitas = sum([l.valor for l in lancamentos if l.tipo == TipoLancamento.RECEITA])
        total_despesas = sum([abs(l.valor) for l in lancamentos if l.tipo == TipoLancamento.DESPESA])
        total_lancamentos = len(lancamentos)
        saldo_atual = conta.saldo_inicial + total_receitas - total_despesas
        
        conta_response = {
            **conta.__dict__,
            "total_receitas": total_receitas,
            "total_despesas": total_despesas,
            "total_lancamentos": total_lancamentos,
            "saldo_atual": saldo_atual
        }
        
        return conta_response
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar conta: {str(e)}")

@router.delete("/{conta_id}")
async def deletar_conta(
    conta_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Deleta uma conta bancária e desvincula lançamentos associados
    """
    try:
        query = select(Conta).where(
            and_(
                Conta.id == conta_id,
                Conta.user_id == current_user.id
            )
        )
        result = await db.execute(query)
        conta = result.scalar_one_or_none()
        
        if not conta:
            raise HTTPException(status_code=404, detail="Conta não encontrada")
        
        # Desvincular lançamentos desta conta (definir conta_id como NULL)
        query_lancamentos = select(Lancamento).where(Lancamento.conta_id == conta_id)
        result_lancamentos = await db.execute(query_lancamentos)
        lancamentos = result_lancamentos.scalars().all()
        
        for lancamento in lancamentos:
            lancamento.conta_id = None
        
        # Deletar conta
        await db.delete(conta)
        await db.commit()
        
        return {"message": "Conta deletada com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao deletar conta: {str(e)}")

@router.patch("/{conta_id}/ativar")
async def ativar_desativar_conta(
    conta_id: int,
    ativar: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Ativa ou desativa uma conta sem deletar (soft delete)
    """
    try:
        query = select(Conta).where(
            and_(
                Conta.id == conta_id,
                Conta.user_id == current_user.id
            )
        )
        result = await db.execute(query)
        conta = result.scalar_one_or_none()
        
        if not conta:
            raise HTTPException(status_code=404, detail="Conta não encontrada")
        
        conta.ativa = "true" if ativar else "false"
        await db.commit()
        
        status = "ativada" if ativar else "desativada"
        return {"message": f"Conta {status} com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao alterar status da conta: {str(e)}")

@router.get("/resumo/estatisticas", response_model=ResumoContasResponse)
async def obter_resumo_contas(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtém resumo estatístico das contas do usuário
    """
    try:
        # Query base
        query = select(Conta).where(Conta.user_id == current_user.id)
        result = await db.execute(query)
        todas_contas = result.scalars().all()
        
        total_contas = len(todas_contas)
        contas_ativas = len([c for c in todas_contas if c.ativa == "true"])
        
        # Calcular saldos atualizados
        saldos = []
        bancos = {}
        
        for conta in todas_contas:
            # Recalcular saldo atual
            query_lancamentos = select(Lancamento).where(Lancamento.conta_id == conta.id)
            result_lancamentos = await db.execute(query_lancamentos)
            lancamentos = result_lancamentos.scalars().all()
            
            total_receitas = sum([l.valor for l in lancamentos if l.tipo == TipoLancamento.RECEITA])
            total_despesas = sum([abs(l.valor) for l in lancamentos if l.tipo == TipoLancamento.DESPESA])
            saldo_atual = conta.saldo_inicial + total_receitas - total_despesas
            
            saldos.append(saldo_atual)
            
            # Contar por banco
            if conta.banco in bancos:
                bancos[conta.banco] += 1
            else:
                bancos[conta.banco] = 1
        
        saldo_total = sum(saldos)
        maior_saldo = max(saldos) if saldos else 0
        menor_saldo = min(saldos) if saldos else 0
        
        # Banco com mais contas
        banco_principal = max(bancos, key=bancos.get) if bancos else None
        
        return ResumoContasResponse(
            total_contas=total_contas,
            contas_ativas=contas_ativas,
            saldo_total=saldo_total,
            maior_saldo=maior_saldo,
            menor_saldo=menor_saldo,
            banco_principal=banco_principal
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter resumo: {str(e)}")

@router.get("/bancos/lista")
async def listar_bancos_unicos(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista todos os bancos únicos das contas do usuário
    """
    try:
        query = select(Conta.banco).where(Conta.user_id == current_user.id).distinct()
        result = await db.execute(query)
        bancos = [row[0] for row in result.fetchall()]
        
        return {"bancos": sorted(bancos)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar bancos: {str(e)}")

@router.get("/{conta_id}/lancamentos")
async def listar_lancamentos_conta(
    conta_id: int,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista lançamentos de uma conta específica
    """
    try:
        # Verificar se conta pertence ao usuário
        query_conta = select(Conta).where(
            and_(
                Conta.id == conta_id,
                Conta.user_id == current_user.id
            )
        )
        result_conta = await db.execute(query_conta)
        conta = result_conta.scalar_one_or_none()
        
        if not conta:
            raise HTTPException(status_code=404, detail="Conta não encontrada")
        
        # Buscar lançamentos da conta
        query = select(Lancamento).where(Lancamento.conta_id == conta_id)\
                                  .order_by(Lancamento.data_lancamento.desc())\
                                  .offset(skip).limit(limit)
        result = await db.execute(query)
        lancamentos = result.scalars().all()
        
        return {"conta": conta.nome, "banco": conta.banco, "lancamentos": lancamentos}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar lançamentos: {str(e)}") 