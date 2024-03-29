#!/usr/bin/env python
# -*- coding: utf-8 -*-

import PoleUtil
from PolePDF import *
import locale
# import cx_Oracle

cf = PoleUtil.cf

# Se o Python rodando é o 2.7
import sys
py_27 = sys.version_info[:2] == (2, 7)

# Tamanho da fonte de a chave de acesso caber no espaço
fonte_chave_acesso = ParagraphStyle('normal', fontSize = 7,
                                    leading = 7, alignment = TA_CENTER)

connection      = None # cx_Oracle.connect("usuario/senha@banco")
ie_empresa      = "552.117.233.111"
ie_sub_empresa  = " "
cnpj_empresa    = "55.555.111/0001-01"
nome_empresa    = "Nome da Empresa"
razao_social_p1 = "Razão Social"
razao_social_p2 = "da Empresa Ltda."
endereco_danfe  = 'Av. Ainda sem nome, S/N - Pq. Industrial, Ribeirão Preto, SP - CEP 14090-200\nFone: (16)3599-9999 - Fax: (16)3599-9911 - www.empresa.com.br'


def transforma_string(variavel):
    return ' ' if variavel is None else str(variavel)


def damdfe(xml_importado, logo=None, diretorio='/tmp'):
    
    #Busca Dados no xml
    
    nome_empresa               = arquivo_importado.MDFe.infMDFe.emit.xNome
    endereço                   = str(arquivo_importado.MDFe.infMDFe.emit.enderEmit.xLgr)  + ', nº ' + str(arquivo_importado.MDFe.infMDFe.emit.enderEmit.nro)
    modelo                     = arquivo_importado.MDFe.infMDFe.ide.mod
    serie                      = arquivo_importado.MDFe.infMDFe.ide.serie
    numero_mdfe                = arquivo_importado.MDFe.infMDFe.ide.nMDF
    data_emissao               = str(arquivo_importado.MDFe.infMDFe.ide.dhEmi)[:-6].replace('T',' ')
    estado_inicio              = arquivo_importado.MDFe.infMDFe.ide.UFIni
    estado_fim                 = arquivo_importado.MDFe.infMDFe.ide.UFFim
    quantidade_carga           = str(arquivo_importado.MDFe.infMDFe.tot.qCarga)[:-1]
    data_prot_autorizacao      = str(arquivo_importado_autorizado.retConsReciMDFe.protMDFe.infProt.nProt) +' - '+ str(arquivo_importado_autorizado.retConsReciMDFe.protMDFe.infProt.dhRecbto)[:-6].replace('T',' ')
    chave_de_acesso            = arquivo_importado_autorizado.retConsReciMDFe.protMDFe.infProt.chMDFe
    placa                      = arquivo_importado.MDFe.infMDFe.infModal.rodo.veicTracao.placa
    renavam                    = arquivo_importado.MDFe.infMDFe.infModal.rodo.veicTracao.RENAVAM
    cpf_condutor               = arquivo_importado.MDFe.infMDFe.infModal.rodo.veicTracao.condutor.CPF
    nome_condutor              = arquivo_importado.MDFe.infMDFe.infModal.rodo.veicTracao.condutor.xNome
    qrcode                     = arquivo_importado.MDFe.infMDFe.infMDFeSupl.qrCodMDFe

    if arquivo_importado.MDFe.infMDFe.tot.qNFe != '':
        quantidade_nfe = arquivo_importado.MDFe.infMDFe.tot.qNFe
    if arquivo_importado.MDFe.infMDFe.tot.qCTe != '':
        quantidade_cte = arquivo_importado.MDFe.infMDFe.tot.qCTe

    documento = PDF('MDF-e ' + numero_mdfe + ' - '+serie+' - ' + nome_empresa, diretorio + '/' + chave_de_acesso + '.pdf')
    p = 385 if py_27 else 432
    documento.celula(19 * cm, 0.4 * cm, '·' * p, '', borda = False)

    # Logotipo
    if logo is not None:
        I = Image(logo)
    else:
        I = Image()
    I.drawWidth = 13 * mm * I.drawWidth / I.drawHeight
    I.drawHeight = 13 * mm

    #Codigo de Barras
    barcode = Code128(chave_de_acesso)
    barcode.barWidth = 0.29 * mm
    barcode.barHeight = 1 * cm

    # Número de páginas e dados da tabela
    ts = [('GRID', (0,0), (-1,-1), .5, colors.black),
          ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
          ('ALIGN',(0,0),(-1,-1),'RIGHT'),
          ('ALIGN',(1,0),(1,-1),'LEFT'),
          ('ALIGN',(5,0),(5,-1),'CENTER'),
          ('TOPPADDING', (0,0), (-1,-1), 0),
          ('RIGHTPADDING', (0,0), (-1,-1), 1),
          ('LEFTPADDING', (0,0), (-1,-1), 1),
          ('BOTTOMPADDING', (0,0), (-1,-1), 1),
          ('LEADING', (2,0), (-1,-1), fonte_tab_pequena.leading),
          ('FONTSIZE', (2,0), (-1,-1), fonte_tab_pequena.fontSize),
          ('LEADING', (0,0), (1,-1), fonte_tab_grande.leading),
          ('FONTSIZE', (0,0), (1,-1), fonte_tab_grande.fontSize),
        ]

    # colWidths=(1 * cm, 5.51 * cm, .92  * cm, .46  * cm, .6   * cm, .59  * cm, .93 * cm, 1.08 * cm, 1.125  * cm, 1.125  * cm, 1.125  * cm, 1.125  * cm, 1.125  * cm, 1.125  * cm, .58 * cm, .58 * cm)
    # colWidths=(1 * cm, 5.51 * cm, .92  * cm, .42  * cm, .58  * cm, .58  * cm, 1   * cm, 1.08 * cm, 1.125  * cm, 1.125  * cm, 1.125  * cm, 1.125  * cm, 1.125  * cm, 1.125  * cm, .58 * cm, .58 * cm)
    # colWidths = (1 * cm, 5.51 * cm, .96  * cm, .46  * cm, .6   * cm, .42  * cm, 1.08 * cm, 1.08 * cm, 1.125  * cm, 1.125  * cm, 1.125  * cm, 1.125  * cm, 1.125  * cm, 1.125  * cm, .58 * cm, .58 * cm)
    colWidths = (1.1 * cm, 5.41 * cm, .96  * cm, .46  * cm, .6   * cm, .42  * cm, 1.08 * cm, 1.08 * cm, 1.125  * cm, 1.125  * cm, 1.125  * cm, 1.125  * cm, 1.125  * cm, 1.125  * cm, .58 * cm, .58 * cm)
    colWidths = [width * fonte_tab_pequena.fontSize/5. for width in colWidths]
    colWidths = tuple([colWidths[0], 19 * cm - sum(colWidths) + colWidths[1]] + colWidths[2:])

    #pPIS_presumido = 0.65
    #pCOFINS_presumido = 3.00
    #
    #sql_difal = ("select nvl(sum(icms_rem), 0), nvl(sum(icms_dest), 0),"
    #             " nvl(sum(icms_fcp), 0),"
    #             " nvl(sum(total_liquido), 0) * :0 / 100,"
    #             " nvl(sum(total_liquido), 0) * :1 / 100, min(cfop)"
    #             " from item_nota_fiscal"
    #             " where cod_nota_fiscal = :2",
    #             [pPIS_presumido, pCOFINS_presumido, cod_nota_fiscal])
    #cursor.execute(*sql_difal)
    #dados = cursor.fetchone()
    # print 'sql_difal:', sql_difal
    # print 'dados:', dados
    #cfop = dados[5]
    #if (cfop in ('5.910', '5.911', '6.910', '6.911') or cfop[0] in ('3', '7') or registros[60] in ('SPAD', 'MGAD') or tipo_pagamento == '- - - - -'):
    #    icms_rem = icms_dest = icms_fcp = pis = cofins = difal = '0,00'
    #else:
    #    icms_rem, icms_dest, icms_fcp, pis, cofins = [cf(v, 'Quebrado 2')[1] for v in dados[:5]]
    #    difal = cf(sum(dados[:3]), 'Quebrado 2')[1]
    #
    #sql_itens = ("select i.cod_produto, i.descricao, i.classificacao_fiscal ncm,"
    #             " i.situacao_tributaria_A || i.situacao_tributaria_B, i.cfop,"
    #             " i.cod_unidade, i.quantidade, i.total_liquido / i.quantidade,"
    #             " i.total_liquido, i.base_icms, i.icms, i.base_substituicao,"
    #             " i.substituicao, i.ipi, i.percentual_icms, i.percentual_ipi,"
    #             " p.fci, pi.cod_item cod_item_manuf"
    #             " from item_nota_fiscal i"
    #             " join produto p on p.cod_produto = i.cod_produto"
    #             " left join producao_item pi on pi.cod_item_orc = i.cod_item"
    #             " where i.cod_nota_fiscal = :0"
    #             " order by i.cod_item",
    #             [cod_nota_fiscal])
    #cursor.execute(*sql_itens)
    #dados = cursor.fetchall()

    #dados_tabela = []
    #for linha in dados:
    #    mascara_ncm = ('%08d', '%02d')[linha[2] < 100]
    #    ncm = mascara_ncm % linha[2]
    #    if linha[2] > 99:
    #        ncm = ncm[:4] + '.' + ncm[4:6] + '.' + ncm[6:]
    #    # Descrição e FCI se tiver
    #    descricao = paragrafo(linha[1], fonte_tab_grande)
    #    if linha[16]:
    #        descricao = [descricao,
    #                     paragrafo('FCI: ' + linha[16] if linha[16] else '',
    #                               fonte_tab_pequena)]
    #    dados_tabela.append(
    #        [
    #            (paragrafo("%i.\n%06i" % (linha[ 0], linha[17]), normal_direita) if linha[17]
    #             else PoleUtil.formatar_inteiro(linha[ 0])),
    #            descricao,
    #            ncm,
    #            linha[ 3],
    #            linha[ 4],
    #            linha[ 5],
    #            PoleUtil.formatar_real(str(linha[ 6]).replace('.', ','), 4),
    #            PoleUtil.formatar_real(str(linha[ 7]).replace('.', ','), 4),
    #            PoleUtil.formatar_real(str(linha[ 8]).replace('.', ','), 2),
    #            PoleUtil.formatar_real(str(linha[ 9]).replace('.', ','), 2),
    #            PoleUtil.formatar_real(str(linha[10]).replace('.', ','), 2),
    #            PoleUtil.formatar_real(str(linha[11]).replace('.', ','), 2),
    #            PoleUtil.formatar_real(str(linha[12]).replace('.', ','), 2),
    #            PoleUtil.formatar_real(str(linha[13]).replace('.', ','), 2),
    #            PoleUtil.formatar_real(str(linha[14]).replace('.', ','), 2),
    #            PoleUtil.formatar_real(str(linha[15]).replace('.', ','), 2),
    #        ]
    #    )
    #alt_comp = documento.altura(  14 * cm,   3 * cm, None, [paragrafo('INFORMAÇÕES COMPLEMENTARES', pequena_esquerda), paragrafo('Pedido ' + nome_empresa + ': ' + PoleUtil.formatar_inteiro(cod_nota_fiscal) + ' - ' + vendedor + ' - Cliente: ' + cod_entidade + '\n \n' + observacao.replace('<', '\n').replace('>', '\n'), normal_esquerda)])
    #a3 = 15 * cm - alt_comp
    #tabela, itens, altura = documento.tabela(5.4 * cm, a3, dados_tabela, colWidths, style=ts)
    #print tabela, itens, altura / cm, len(dados), a3 / cm
    #raw_input('----------------------')
    #itens_extras = itens
    #paginas = 1
    #while itens_extras < len(dados):
    #    tabela_extra, i, altura = documento.tabela(19 * cm, 21 * cm, dados_tabela[itens_extras:],colWidths=(1 * cm, 5.51 * cm, .92  * cm, .42  * cm, .58  * cm, .58  * cm, 1 * cm, 1.08 * cm, 1.125  * cm, 1.125  * cm, 1.125  * cm, 1.125  * cm, 1.125  * cm, 1.125  * cm, .58 * cm, .58 * cm), style=ts)
    #    #print tabela_extra, i, altura / cm, len(dados), itens_extras
    #    #raw_input('----------------------')
    #    itens_extras += i
    #    paginas += 1

    # Dados Empresa
    a1_1 = documento.altura( 7 * cm, 1 * mm, None, [I, paragrafo('<b>' + razao_social_p1 + '</b>', normal_centro), paragrafo('<b>' + razao_social_p2 + '</b>', pequena_centro), paragrafo(endereco_danfe, pequena_centro)])
    a1_2 = documento.altura( 7 * cm, 1 * mm, 'NATUREZA DA OPERAÇÃO', natureza_operacao)
    a2 = documento.altura( 3.65 * cm, 1 * mm, None, [paragrafo('<b>DANFE</b>', normal_centro), paragrafo('Documento Auxiliar da Nota Fiscal Eletrônica\n ', pequena_centro), paragrafo('0 - Entrada', pequena_esquerda), paragrafo('1 - Saída\n ', pequena_esquerda), paragrafo(' \n<b>Nº '+numero_nfe+'</b>', normal_esquerda), paragrafo('<b>Série: '+serie_nfe+'</b>', normal_esquerda), paragrafo(' \n<b>Página 1 de ' + str(paginas) + '</b>', normal_centro)], borda = False)
    a3 = documento.altura( 8.35 * cm, 1 * mm, None, [paragrafo('Controle do Fisco\n ', pequena_esquerda), paragrafo('\n \n \n \n \n \n \n \n ', pequena_esquerda), paragrafo('Consulta de autenticidade no portal nacional da NF-e www.nfe.gov.br/portal ou no site da Sefaz Autorizada', pequena_centro)])
    if a1_1 + a1_2 > a2:
        a = a1_1 + a1_2
    else:
        a = a2
    if a < a3:
        a = a3
    documento.celula( 7 * cm, a, None, [I, paragrafo('<b>' + razao_social_p1 + '</b>', normal_centro), paragrafo('<b>' + razao_social_p2 + '</b>', pequena_centro), paragrafo(endereco_danfe, pequena_centro)])
    documento.celula( 3.65 * cm, a, None, [paragrafo('<b>DANFE</b>', normal_centro), paragrafo('Documento Auxiliar da Nota Fiscal Eletrônica\n ', pequena_centro), paragrafo('0 - Entrada', pequena_esquerda), paragrafo('1 - Saída\n ', pequena_esquerda), paragrafo(' \n<b>Nº '+numero_nfe+'</b>', normal_esquerda), paragrafo('<b>Série: '+serie_nfe+'</b>', normal_esquerda), paragrafo(' \n<b>Página 1 de ' + str(paginas) + '</b>', normal_centro)], borda = False)
    documento.celula( 8.35 * cm, a, None, [paragrafo('Controle do Fisco\n ', pequena_esquerda), paragrafo('\n \n \n \n \n \n \n \n ', pequena_esquerda), paragrafo('Consulta de autenticidade no portal nacional da NF-e\nwww.nfe.fazenda.gov.br ou no site da Sefaz Autorizada', normal_centro)])

    # Natureza da Operação flutuante
    documento.celula( 7 * cm, 1 * mm, 'NATUREZA DA OPERAÇÃO', natureza_operacao, posicao = (1 * cm, 2.6 * cm + a - a1_2))

    #Posição Chave de acesso celula flutuante
    chave_de_acesso = [paragrafo('Chave de acesso', pequena_esquerda), paragrafo(' '.join([chave_de_acesso[x*4:x*4+4] for x in range(11)]), fonte_chave_acesso if py_27 else normal_centro)]
    documento.celula(7.2 * cm,.6 * cm, None, chave_de_acesso, posicao=(12.225 * cm, 4 * cm))
    #Posição Entrada Saida celula flutuante
    if tipo_nota=='S':
        tipo = "1"
    else:
        tipo = "0"
    documento.celula(.4* cm,.4 * cm, None, [paragrafo(str(tipo), normal_centro)], posicao=(9.1 * cm, 3.3 * cm))
    documento.celula(10 * mm, 1 * mm, None, [barcode], posicao=(15.325 * cm, 2.82 * cm), borda = False)

    #documento.celula( 19 * cm, 3.8 * mm, None, [paragrafo('PROTOCOLO DE AUTORIZAÇÃO DE USO', pequena_esquerda), paragrafo('00000000000000000000000000000000000', normal_esquerda)])

    # Inscrição estadual
    documento.celula( 3.5 * cm, 1 * mm, 'INSCRIÇÃO ESTADUAL', ie_empresa)
    documento.celula( 3.5 * cm, 1 * mm, None, [paragrafo('INSCRIÇÃO ESTADUAL SUBST. TRIB.', pequena_esquerda), paragrafo(ie_sub_empresa, normal_direita)])
    documento.celula( 3.65 * cm, 1 * mm, 'CNPJ', cnpj_empresa)
    documento.celula( 8.35 * cm, 1 * mm, None, [paragrafo('PROTOCOLO DE AUTORIZAÇÃO DE USO', pequena_centro), paragrafo(protocolo, normal_centro)])

    # DESTINATARIO REMETENTE
    documento.celula( 19 * cm, 1 * mm, None, [paragrafo('DESTINATÁRIO / REMETENTE', pequena_esquerda)], borda = False)

    #print razao_social
    documento.celula(13.8 * cm, 1 * mm, 'NOME/RAZAO SOCIAL', razao_social)
    documento.celula( 2.7 * cm, 1 * mm, 'CNPJ/CPF', cnpj)
    documento.celula( 2.5 * cm, 1 * mm, 'DATA EMISSÃO', data_emissao)

    documento.celula(11.1 * cm, 1 * mm, 'ENDEREÇO', endereco)
    documento.celula( 4.0 * cm, 1 * mm, 'BAIRRO/DISTRITO', bairro)
    documento.celula( 1.4 * cm, 1 * mm, 'CEP', cep)
    documento.celula( 2.5 * cm, 1 * mm, 'DATA ENTRADA/SAIDA', data_entrada_saida)

    documento.celula(10.5 * cm, 1 * mm, 'MUNICÍPIO', municipio)
    documento.celula( 2.5 * cm, 1 * mm, 'FONE/FAX', fone_fax)
    documento.celula( 0.6 * cm, 1 * mm, 'UF', uf)
    documento.celula( 2.9 * cm, 1 * mm, 'INSCRIÇÃO ESTADUAL', ie)
    documento.celula( 2.5 * cm, 1 * mm, 'HORA ENTRADA/SAIDA' , hora_entrada_saida)

    # FATURA
    documento.celula( 19 * cm, 3.8 * mm, None, [paragrafo('FATURA', pequena_esquerda)], borda = False)

    # ALTURA PAGAMENTO 1 DETALHES
    #a1 = documento.altura( 1.8 * cm, 1 * mm, None, [paragrafo('01/02/2009', normal_direita), paragrafo('100,00', normal_direita)])
    #
    #
    ## FORMA DE PAGAMENTO
    #documento.celula( 4* cm, a1, None, [paragrafo('FORMA DE PAGAMENTO\n', pequena_esquerda), paragrafo(tipo_pagamento, normal_esquerda)])
    #
    #sql_parcelas=("select cod_nota_fiscal, num_parcela, valor_parcela, to_char(vencimento_parcela,'DD/MM/YYYY') "
    #                      "from parcela_nota_fiscal "
    #                      "where cod_nota_fiscal = " + cod_nota_fiscal + " order by num_parcela")
    #
    #cursor.execute(sql_parcelas)
    #parcelas = cursor.fetchall()
    #if not parcelas:
    #    parcelas = []
    #
    #for parcela in parcelas:
    #    data_parcela  = transforma_string(parcela[3])
    #    valor_parcela = PoleUtil.formatar_real(parcela[2])
    #    num_parcela   = transforma_string(parcela[1])
    #    # PAGAMENTO 1
    #    documento.celula( .4 * cm, a1, None, [paragrafo(' ', pequena_centro), paragrafo(' ' + num_parcela, normal_centro)])
    #
    #    # PAGAMENTO 1 DETALHES
    #    documento.celula( 2.1 * cm, a1, None, [paragrafo(data_parcela, normal_direita), paragrafo(valor_parcela, normal_direita)])
    #
    # Preenche campo de parcelas em branco caso tenha menos pagamentos que 6
    #
    #if len(parcelas) < 6:
    #    for parcela_branco in range(6-len(parcelas)):
    #        # PAGAMENTO 1
    #        documento.celula( .4 * cm, a1, None, [paragrafo(' ', pequena_centro), paragrafo(' ', normal_centro)], borda = False)
    #
    #        # PAGAMENTO 1 DETALHES
    #        documento.celula( 2.1 * cm, a1, None, [paragrafo(' ', normal_direita), paragrafo(' ', normal_direita)],borda = False)
    #
    ## CALCULO DO IMPOSTO
    #documento.celula( 19 * cm, 3.8 * mm, None, [paragrafo('CÁLCULO DO IMPOSTO', pequena_esquerda)], borda = False)
    #
    ## BASE DE CALCULO ICMS
    #documento.celula( 2.11 * cm, mm, 'BASE DE CÁLC. ICMS', base_calculo_icms, alinhamento = 'direita')
    #
    ## VALOR DO ICMS
    #documento.celula( 2.11 * cm, mm, 'VALOR DO ICMS', vl_icms, alinhamento = 'direita')
    #
    ## BASE DE CALCULO DO ICMS ST
    #documento.celula( 2.11 * cm, mm, 'BASE CÁLC. ICMS ST', base_calculo_icms_st, alinhamento = 'direita')
    #
    ## VALOR DO ICMS ST
    #documento.celula( 2.11 * cm, mm, 'VALOR DO ICMS ST', vl_icms_st, alinhamento = 'direita')
    #
    ## VALOR DO IMPOSTO DE IMPORTAÇÃO
    #documento.celula( 2.11 * cm, mm, 'V. IMP. IMPORTAÇÃO', '0,00', alinhamento = 'direita')
    #
    ## VALOR DO ICMS DIFAL PARA UF DO REMETENTE
    #documento.celula( 2.11 * cm, mm, 'V. ICMS UF REMET.', icms_rem, alinhamento = 'direita')
    #
    ## VALOR DO FUNDO DE COMBATE À POBREZA
    #documento.celula( 2.11 * cm, mm, 'VALOR DO FCP', icms_fcp, alinhamento = 'direita')
    #
    ## VALOR DO PIS
    #documento.celula( 2.11 * cm, mm, 'VALOR DO PIS', pis, alinhamento = 'direita')
    #
    ## VALOR TOTAL DOS PRODUTOS
    #documento.celula( 2.12 * cm, mm, 'V. TOTAL PRODUTOS', vl_total_produtos, alinhamento = 'direita')
    #
    ## VALOR DO FRETE
    ## documento.celula( 2.85 * cm, mm, 'VALOR DO FRETE', vl_frete, alinhamento = 'direita')
    #documento.celula( 2.11 * cm, mm, 'VALOR DO FRETE', '0,00', alinhamento = 'direita')
    #
    ## VALOR DO SEGURO
    #documento.celula( 2.11 * cm, mm, 'VALOR DO SEGURO', vl_seguro, alinhamento = 'direita')
    #
    ## DESCONTO
    #documento.celula( 2.11 * cm, mm, 'DESCONTO', '0,00', alinhamento = 'direita')
    #
    ## OUTRAS DESPESAS ACESSÓRIAS
    #documento.celula( 2.11 * cm, mm, 'OUTRAS DESPESAS', outras_despesas, alinhamento = 'direita')
    #
    ## VALOR DO IPI
    #documento.celula( 2.11 * cm, mm, 'VALOR DO IPI', vl_ipi, alinhamento = 'direita')
    #
    ## VALOR DO ICMS DIFAL PARA UF DO DESTINATÁRIO
    #documento.celula( 2.11 * cm, mm, 'V. ICMS UF DESTINO', icms_dest, alinhamento = 'direita')
    #
    ## VALOR DO IMPOSTO DIFAL
    #documento.celula( 2.11 * cm, mm, 'V. TOTAL DIFAL', difal, alinhamento = 'direita')
    #
    ## VALOR DO COFINS
    #documento.celula( 2.11 * cm, mm, 'VALOR DO COFINS', cofins, alinhamento = 'direita')
    #
    ## VALOR TOTAL DA NOTA
    #documento.celula( 2.12 * cm, mm, 'V. TOTAL NOTA', vl_total_nota, alinhamento = 'direita')

    # TRANSPORTADOR/VOLUMES TRANSPORTADOS
    documento.celula( 19 * cm, 3.8 * mm, None, [paragrafo('TRANSPORTADOR/VOLUMES TRANSPORTADOS', pequena_esquerda)], borda = False)

    # FRETE ALTURA
    a1 = documento.altura( 3.7 * cm, 3.8 * mm, None, [paragrafo('FRETE POR CONTA', pequena_esquerda), paragrafo('0-EMITENTE', pequena_esquerda), paragrafo('1-DESTINATÁRIO', pequena_esquerda)])

    # RAZÃO SOCIAL
    #documento.celula( 6.5 * cm, a1, None, [paragrafo('RAZÃO SOCIAL', pequena_esquerda), paragrafo(razao_transportadora, normal_esquerda)])
    documento.celula( 9.8 * cm, a1, 'RAZÃO SOCIAL', razao_transportadora)

    # FRETE
    documento.celula( 2.5 * cm, a1, None, [paragrafo('FRETE POR CONTA', pequena_esquerda), paragrafo('0-EMITENTE', pequena_esquerda), paragrafo('1-DESTINATÁRIO', pequena_esquerda)])

    # CÓDIGO ANTT
    documento.celula( 1.5 * cm, a1, 'CÓDIGO ANTT', '')

    # PLACA DO VEÍCULO
    documento.celula(1.9 * cm, a1, 'PLACA DO VEÍCULO', placa_veiculo)

    # UF
    documento.celula(0.6 * cm, a1, 'UF', uf_transporte)

    # CNPJ/CPF
    documento.celula( 2.7 * cm, a1, 'CNPJ/CPF', cnpj_transporte)

    #FRETE POR CONTA NUMERO FLUTUANTE
    documento.celula(.4 * cm,.4 * cm, None,[paragrafo(frete_conta[int(frete_por_conta)],normal_centro)],posicao=(12.8 * cm, 10.9 * cm))

    # ENDEREÇO
    documento.celula(9.8 * cm, 3.8 * mm, 'ENDEREÇO', endereco_transporte)

    # MUNICÍPIO
    documento.celula(5.9 * cm, 3.8 * mm, 'MUNICÍPIO', municipio_transporte)

    # UF
    documento.celula( .6 * cm, 3.8 * mm, 'UF', uf_endereco_transporte)

    # INSCRIÇÃO ESTADUAL
    documento.celula( 2.7 * cm, 3.8 * mm, 'INSCRIÇÃO ESTADUAL', ie_transporte)

    # QUANTIDADE
    documento.celula( 2.5 * cm, 3.8 * mm, 'QUANTIDADE', quantidade, alinhamento = 'direita')

    # ESPÉCIE
    documento.celula( 4.1 * cm, 3.8 * mm, 'ESPÉCIE', especie)

    # MARCA
    documento.celula( 4.2 * cm, 3.8 * mm, 'MARCA', marca)

    # NUMERAÇÃO
    documento.celula( 2.8 * cm, 3.8 * mm, 'NUMERAÇÃO', numeracao)

    # PESO BRUTO
    documento.celula( 2.7 * cm, 3.8 * mm, 'PESO BRUTO', peso_bruto, alinhamento = 'direita')

    # PESO LÍQUIDO
    documento.celula( 2.7 * cm, 3.8 * mm, 'PESO LÍQUIDO', peso_liquido, alinhamento = 'direita')

    # DADOS DO PRODUTO/SERVIÇO
    documento.celula( 19 * cm, 3.8 * mm, None, [paragrafo('DADOS DO PRODUTO/SERVIÇO', pequena_esquerda)], borda = False)


    # ALÍQ. ICMS - altura
    a1 = documento.altura( .6 * cm, 3.8 * mm, None, [paragrafo('ALÍQ. ICMS', pequena_esquerda)])

    # CÓDIGO
    documento.celula(colWidths[ 0], a1, None, [paragrafo('CÓDIGO', pequena_direita)])

    # DESCRIÇÃO DO PRODUTO/SERVIÇO
    documento.celula(colWidths[ 1], a1, None, [paragrafo('DESCRIÇÃO DO PRODUTO / SERVIÇO', pequena_esquerda)])

    # NCM/SH
    documento.celula(colWidths[ 2], a1, None, [paragrafo('NCM / SH', pequena_direita)])

    # CST
    documento.celula(colWidths[ 3], a1, None, [paragrafo('CST', pequena_direita)])

    # CFOP
    documento.celula(colWidths[ 4], a1, None, [paragrafo('CFOP', pequena_direita)])

    # UN.
    documento.celula(colWidths[ 5], a1, None, [paragrafo('UN.', pequena_direita)])

    # QTD
    documento.celula(colWidths[ 6], a1, None, [paragrafo('QUANT.', pequena_direita)])

    # VLR. UNIT.
    documento.celula(colWidths[ 7], a1, None, [paragrafo('VALOR UNIT.', pequena_direita)])

    # VLR. TOTAL
    documento.celula(colWidths[ 8], a1, None, [paragrafo('VALOR TOTAL', pequena_direita)])

    # BC ICMS
    documento.celula(colWidths[ 9], a1, None, [paragrafo('B. CÁLC. ICMS', pequena_direita)])

    # VLR. ICMS
    documento.celula(colWidths[10], a1, None, [paragrafo('VALOR ICMS', pequena_direita)])

    # BC ICMS ST
    documento.celula(colWidths[11], a1, None, [paragrafo('B. CÁLC. ICMS ST', pequena_direita)])

    # VLR. ICMS ST
    documento.celula(colWidths[12], a1, None, [paragrafo('VALOR ICMS ST', pequena_direita)])

    # VLR. IPI
    documento.celula(colWidths[13], a1, None, [paragrafo('     VALOR IPI', pequena_direita)])

    # ALÍQ. ICMS
    documento.celula(colWidths[14], a1, None, [paragrafo('ALÍQ. ICMS', pequena_direita)])

    # ALÍQ. IPI
    documento.celula(colWidths[15], a1, None, [paragrafo('ALÍQ. IPI', pequena_direita)])

    #DADOS ADICIONAIS
    documento.celula( 19 * cm, 3.8 * mm, None, [paragrafo('DADOS ADICIONAIS', pequena_esquerda)], borda = False, posicao=(1 * cm, 28.4 * cm - alt_comp))
    documento.celula( 14 * cm,      alt_comp, None,      [paragrafo('INFORMAÇÕES COMPLEMENTARES', pequena_esquerda), paragrafo('Pedido ' + nome_empresa + ': ' + PoleUtil.formatar_inteiro(cod_nota_fiscal) + ' - ' + vendedor + ' - Cliente: ' + cod_entidade + '\n \n' + observacao.replace('<', '\n').replace('>', '\n'), normal_esquerda)], posicao=(1 * cm, 28.7 * cm - alt_comp))
    if denegado:
        documento.celula(  5 * cm,       alt_comp, None, [paragrafo('RESERVADO AO FISCO', pequena_esquerda), paragrafo('USO DENEGADO', extra_grande_centro), paragrafo(' \nNFe SEM VALOR', grande_centro)], posicao=(15 * cm, 28.7 * cm - alt_comp))
    else:
        documento.celula(  5 * cm,       alt_comp, None, [paragrafo('RESERVADO AO FISCO', pequena_esquerda)],posicao=(15 * cm, 28.7 * cm - alt_comp))

    #Propaganda
    documento.celula( 19 * cm, 1 * mm, None, [paragrafo('NF-e ERP 3.0 - www.juniorpolegato.com.br', minuscula_direita)], posicao = (1 * cm, 28.7 * cm), borda = False)


    documento.celula(19 * cm, 15 * cm - alt_comp, None, (tabela,), borda=False, espacamento=0)

    pagina = 1
    while itens < len(dados):
        pagina += 1
        documento.nova_pagina()
        # Cabeçalho
        documento.celula(19 * cm, 1.2 * cm, '', '', borda = False)
        p = 385 if py_27 else 432
        documento.celula(19 * cm, 0.4 * cm, '·' * p, '', borda = False)

        # Dados Empresa
        a1_1 = documento.altura( 7 * cm, 1 * mm, None, [I, paragrafo('<b>' + razao_social_p1 + '</b>', normal_centro), paragrafo('<b>' + razao_social_p2 + '</b>', pequena_centro), paragrafo(endereco_danfe, pequena_centro)])
        a1_2 = documento.altura( 7 * cm, 1 * mm, 'NATUREZA DA OPERAÇÃO', natureza_operacao)
        a2 = documento.altura( 3.65 * cm, 1 * mm, None, [paragrafo('<b>DANFE</b>', normal_centro), paragrafo('Documento Auxiliar da Nota Fiscal Eletrônica\n ', pequena_centro), paragrafo('0 - Entrada', pequena_esquerda), paragrafo('1 - Saída\n ', pequena_esquerda), paragrafo(' \n<b>Nº '+numero_nfe+'</b>', normal_esquerda), paragrafo('<b>Série: '+serie_nfe+'</b>', normal_esquerda), paragrafo(' \n<b>Página ' + str(pagina) + ' de ' + str(paginas) + '</b>', normal_centro)], borda = False)
        a3 = documento.altura( 8.35 * cm, 1 * mm, None, [paragrafo('Controle do Fisco\n ', pequena_esquerda), paragrafo('\n \n \n \n \n \n \n \n ', pequena_esquerda), paragrafo('Consulta de autenticidade no portal nacional da NF-e www.nfe.gov.br/portal ou no site da Sefaz Autorizada', pequena_centro)])
        if a1_1 + a1_2 > a2:
            a = a1_1 + a1_2
        else:
            a = a2
        if a < a3:
            a = a3
        documento.celula( 7 * cm, a, None, [I, paragrafo('<b>' + razao_social_p1 + '</b>', normal_centro), paragrafo('<b>' + razao_social_p2 + '</b>', pequena_centro), paragrafo(endereco_danfe, pequena_centro)])
        documento.celula( 3.65 * cm, a, None, [paragrafo('<b>DANFE</b>', normal_centro), paragrafo('Documento Auxiliar da Nota Fiscal Eletrônica\n ', pequena_centro), paragrafo('0 - Entrada', pequena_esquerda), paragrafo('1 - Saída\n ', pequena_esquerda), paragrafo(' \n<b>Nº '+numero_nfe+'</b>', normal_esquerda), paragrafo('<b>Série: '+serie_nfe+'</b>', normal_esquerda), paragrafo(' \n<b>Página ' + str(pagina) + ' de ' + str(paginas) + '</b>', normal_centro)], borda = False)
        documento.celula( 8.35 * cm, a, None, [paragrafo('Controle do Fisco\n ', pequena_esquerda), paragrafo('\n \n \n \n \n \n \n \n ', pequena_esquerda), paragrafo('Consulta de autenticidade no portal nacional da NF-e\nwww.nfe.fazenda.gov.br ou no site da Sefaz Autorizada', normal_centro)])

        # Natureza da Operação flutuante
        documento.celula( 7 * cm, 1 * mm, 'NATUREZA DA OPERAÇÃO', natureza_operacao, posicao = (1 * cm, 2.6 * cm + a - a1_2))

        #Posição Chave de acesso celula flutuante
        documento.celula(7.2 * cm,.6 * cm, None, chave_de_acesso, posicao=(12.225 * cm, 4 * cm))
        #Posição Entrada Saida celula flutuante
        if tipo_nota=='S':
            tipo = "1"
        else:
            tipo = "0"
        documento.celula(.4* cm,.4 * cm, None,[paragrafo(str(tipo), normal_centro)],posicao=(9.1 * cm, 3.3 * cm))
        documento.celula(10 * mm, 1 * mm, None, [barcode], posicao=(15.325 * cm, 2.82 * cm), borda = False)

        #documento.celula( 19 * cm, 3.8 * mm, None, [paragrafo('PROTOCOLO DE AUTORIZAÇÃO DE USO', pequena_esquerda), paragrafo('00000000000000000000000000000000000', normal_esquerda)])

        # Inscrição estadual
        documento.celula( 3.5 * cm, 1 * mm, 'INSCRIÇÃO ESTADUAL', ie_empresa)
        documento.celula( 3.5 * cm, 1 * mm, None, [paragrafo('INSCRIÇÃO ESTADUAL SUBST. TRIB.', pequena_esquerda), paragrafo(ie_sub_empresa,normal_direita)])
        documento.celula( 3.65 * cm, 1 * mm, 'CNPJ', cnpj_empresa)
        documento.celula( 8.35 * cm, 1 * mm, None, [paragrafo('PROTOCOLO DE AUTORIZAÇÃO DE USO', pequena_centro), paragrafo(protocolo, normal_centro)])

        # DADOS DO PRODUTO/SERVIÇO
        documento.celula( 19 * cm, 3.8 * mm, None, [paragrafo('DADOS DO PRODUTO/SERVIÇO', pequena_esquerda)], borda = False)

        # ALÍQ. ICMS - altura
        a1 = documento.altura( .6 * cm, 3.8 * mm, None, [paragrafo('ALÍQ. ICMS', pequena_esquerda)])

        # CÓDIGO
        documento.celula(colWidths[ 0], a1, None, [paragrafo('CÓDIGO', pequena_direita)])

        # DESCRIÇÃO DO PRODUTO/SERVIÇO
        documento.celula(colWidths[ 1], a1, None, [paragrafo('DESCRIÇÃO DO PRODUTO / SERVIÇO', pequena_esquerda)])

        # NCM/SH
        documento.celula(colWidths[ 2], a1, None, [paragrafo('NCM / SH', pequena_direita)])

        # CST
        documento.celula(colWidths[ 3], a1, None, [paragrafo('CST', pequena_direita)])

        # CFOP
        documento.celula(colWidths[ 4], a1, None, [paragrafo('CFOP', pequena_direita)])

        # UN.
        documento.celula(colWidths[ 5], a1, None, [paragrafo('UN.', pequena_direita)])

        # QTD
        documento.celula(colWidths[ 6], a1, None, [paragrafo('QUANT.', pequena_direita)])

        # VLR. UNIT.
        documento.celula(colWidths[ 7], a1, None, [paragrafo('VALOR UNIT.', pequena_direita)])

        # VLR. TOTAL
        documento.celula(colWidths[ 8], a1, None, [paragrafo('VALOR TOTAL', pequena_direita)])

        # BC ICMS
        documento.celula(colWidths[ 9], a1, None, [paragrafo('B. CÁLC. ICMS', pequena_direita)])

        # VLR. ICMS
        documento.celula(colWidths[10], a1, None, [paragrafo('VALOR ICMS', pequena_direita)])

        # BC ICMS ST
        documento.celula(colWidths[11], a1, None, [paragrafo('B. CÁLC. ICMS ST', pequena_direita)])

        # VLR. ICMS ST
        documento.celula(colWidths[12], a1, None, [paragrafo('VALOR ICMS ST', pequena_direita)])

        # VLR. IPI
        documento.celula(colWidths[13], a1, None, [paragrafo('     VALOR IPI', pequena_direita)])

        # ALÍQ. ICMS
        documento.celula(colWidths[14], a1, None, [paragrafo('ALÍQ. ICMS', pequena_direita)])

        # ALÍQ. IPI
        documento.celula(colWidths[15], a1, None, [paragrafo('ALÍQ. IPI', pequena_direita)])

        tabela, i, altura = documento.tabela(19 * cm, 21 * cm, dados_tabela[itens:],colWidths=colWidths, style=ts)
        documento.celula(19 * cm, 21 * cm, None, (tabela,), borda=False, espacamento=0)
        itens += i

    documento.salvar()
