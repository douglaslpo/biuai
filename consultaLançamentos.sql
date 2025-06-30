SELECT l.id_lan, ifnull(filial.nm_fantasia, filial.razao_social) AS filial, cta.nm_conta AS conta, bco.nm_banco AS banco, ps.nm_pessoa AS cliente_fornecedor,
case when l.tp_lancamento = 'D' then 'Saída'
ELSE 'Entrada' END AS tipo_lancamento, l.vl_original, l.vl_baixado, l.complemento, l.dt_vencimento, l.dt_baixa, l.dt_documento AS dt_emissao,
nat.nm_natureza, subnat.nm_natureza AS sub_natureza, 
case when l.status_lan = '0' then 'Em aberto'
when l.status_lan = '1' then 'Baixado'
when l.status_lan = '2' then 'Cancelado'
when l.status_lan = '4' then 'Baixa Parcial'
when l.status_lan = '5' then 'Baixado por Fatura' END status_lan FROM fin_lancamentos l
INNER JOIN fin_naturezafinanceira nat ON l.id_natureza = nat.id_natureza
INNER JOIN fin_naturezafinanceira subnat ON l.id_sub_natureza = subnat.id_natureza
INNER JOIN glb_pessoa ps ON l.id_pessoa = ps.id_pessoa
LEFT JOIN glb_loja filial ON l.id_loja = filial.id_loja
LEFT JOIN fin_conta cta ON l.id_conta = cta.id_conta
LEFT JOIN fin_banco bco ON cta.id_banco = bco.id_banco
