#!/bin/env python
#-*- coding: utf-8 -*-

import PoleUtil
from PolePDF import *
import locale
import cx_Oracle

# Tamanho da fonte de a chave de acesso caber no espaço
fonte_chave_acesso = ParagraphStyle('normal', fontSize = 7, leading = 7, alignment = TA_CENTER)

def transforma_string(variavel):
    if variavel == None:
       return "&nbsp;"
    return str(variavel).replace("&", "&amp;amp;").replace("<", "&lt;").replace(">", "&gt;")

def danfe(cod_nota_fiscal, logo = None, diretorio = '/tmp'):

    cod_nota_fiscal = str(cod_nota_fiscal)

    frete_conta = ("Erro","0","1")

    # conexao Oracle
    connection = cx_Oracle.connect("usuario/senha@banco")
    cursor = connection.cursor()
    #cursor.execute("insert into administrador.nfe (cod_nota_fiscal, chave_acesso, data_autorizacao, protocolo_autorizacao) values (186567, '35100855666777000105550010000135834230972122', '10/08/2010 11:21:47', '135100445370768')")
    #cursor.execute("commit")

    #Busca Dados da Nota
    sql=("SELECT nt.COD_NOTA_FISCAL, nt.COD_INTERNO, nt.SEQUENCIA, nt.NUM_FORMULARIO, nt.TIPO, nt.DATA_DE_PROCESSAMENTO, TO_CHAR(nt.DATA_DE_EMISSAO,'DD/MM/YYYY'), TO_CHAR(nt.DATA_SAIDA_ENTRADA,'DD/MM/YYYY'),"
                 " TO_CHAR(nt.DATA_DE_ENTREGA,'DD/MM/YYYY'), nt.NATUREZA_OPERACAO, nt.CFOP, nt.INSC_EST_DO_SUBST_TRIBUTARIO, nt.PESSOA, nt.COD_ENTIDADE, nt.NOME_RAZAO_SOCIAL, nt.CNPJ, nt.COD_ENDERECO,"
                 " nt.ENDERECO, nt.BAIRRO, nt.CEP, nt.CIDADE, nt.TELEFONE__FAX, nt.UF, nt.INSCR_ESTADUAL, nt.QUANTIDADE_ITENS, nt.BASE_ICMS, nt.ICMS, nt.BASE_SUBSTITUICAO, nt.SUBSTITUICAO,"
                 " nt.TOTAL_PRODUTOS, nt.FRETE, nt.SEGURO, nt.DESPESAS_ACESSORIAS, nt.BASE_IPI, nt.IPI, nt.TOTAL_GERAL, nt.COD_TRANSPORTADORA, nt.FRETE_POR_CONTA, nt.PLACA, nt.UF_PLACA,"
                 " nt.CNPJ_TRANSP, nt.ENDERECO_TRANSP, nt.CIDADE_TRANSP, nt.UF_TRANSP, nt.INSCR_ESTADUAL_TRANSP, nt.QUANTIDADE_ESPECIES, nt.ESPECIE, nt.MARCA, NUMERO, nt.PESO_BRUTO,"
                 " nt.PESO_LIQUIDO, nt.NUM_PEDIDO, nt.USUARIO, nt.COND_PAGAMENTO, nt.CARTA_CORRECAO, nt.IMPRESSO, nt.OBSERVACAO, nt.STATUS, nt.LIVRO_FISCAL, nt.REGIAO_DA_LOJA, nt.REGIAO_DO_DESTINATARIO,"
                 " nt.RAZAO_SOCIAL_TRANSPORTADORA, nt.COD_ENDERECO_ENTREGA, nt.ENDERECO_ENTREGA, nt.BAIRRO_ENTREGA, nt.CIDADE_ENTREGA, nt.UF_ENTREGA, nt.CEP_ENTREGA, nt.TELEFONE_ENTREGA,"
                 " nt.FATURAMENTO_A_VISTA, nt.PAGO,  nt.NUM_NOTA, nt.COD_END_TRANSP, nt.BALCAO, nt.ANO, nt.MES, nt.DIA, nt.VALOR_FRETE, nt.NUM_COMANDA, nt.MODELO, nt.SERIE, n.CHAVE_ACESSO,"
                 " n.PROTOCOLO_AUTORIZACAO || ' - ' || TO_CHAR(n.DATA_AUTORIZACAO, 'DD/MM/YYYY HH24:MI'), (select f.login from administrador.funcionario f where f.cod_entidade = nt.usuario),"
                 " n.denegado"
                 " from administrador.nota_fiscal nt, administrador.nfe n "
                 " where n.COD_NOTA_FISCAL = " + cod_nota_fiscal + " and nt.COD_NOTA_FISCAL = " + cod_nota_fiscal)
    #print sql
    cursor.execute(sql)
    registros = cursor.fetchone()
    #for i in range(len(registros)):
    #   print '%3d => %s' % (i, registros[i])
    numero_nfe             = PoleUtil.formatar_inteiro(registros[71],9,"0")
    serie_nfe              = "001"
    chave_de_acesso        = transforma_string(registros[81])
    protocolo              = transforma_string(registros[82])
    natureza_operacao      = transforma_string(registros[9])
    ie_empresa               = "552.117.233.111"
    ie_sub_empresa           = "&nbsp;"
    cnpj_empresa             = "55.555.111/0001-01"
    cod_entidade           = PoleUtil.formatar_inteiro(registros[13])
    razao_social           = transforma_string(registros[14])
    if len(PoleUtil.somente_digitos(registros[15])) > 11:
        cnpj                   = PoleUtil.formatar_cnpj(registros[15])
    else:
        cnpj                   = PoleUtil.formatar_cpf(registros[15])
    data_emissao           = transforma_string(registros[6])
    endereco               = transforma_string(registros[17])
    bairro                 = transforma_string(registros[18])
    cep                    = transforma_string(registros[19])
    data_entrada_saida     = transforma_string(registros[6])
    municipio              = transforma_string(registros[20])
    fone_fax               = transforma_string(registros[21])
    uf                     = transforma_string(registros[22])
    ie                     = transforma_string(registros[23])
    hora_entrada_saida     = '&nbsp;'
    tipo_nota              = registros[4]
    tipo_pagamento         = transforma_string(registros[53])
    base_calculo_icms      = PoleUtil.formatar_real(registros[25])
    vl_icms                = PoleUtil.formatar_real(registros[26])
    base_calculo_icms_st   = PoleUtil.formatar_real(registros[27])
    vl_icms_st             = PoleUtil.formatar_real(registros[28])
    vl_total_produtos      = PoleUtil.formatar_real(registros[29])
    vl_frete               = PoleUtil.formatar_real(registros[30])
    vl_seguro              = PoleUtil.formatar_real(registros[31])
    desconto               = "0,00"
    outras_despesas        = PoleUtil.formatar_real(registros[32])
    vl_ipi                 = PoleUtil.formatar_real(registros[34])
    vl_total_nota          = PoleUtil.formatar_real(registros[35])
    razao_transportadora   = transforma_string(registros[61])
    frete_por_conta        = registros[37]
    #codigo_antt            = registros[37]
    placa_veiculo          = transforma_string(registros[38])
    uf_transporte          = transforma_string(registros[39])
    cnpj_transporte        = PoleUtil.formatar_cnpj(registros[40])
    endereco_transporte    = transforma_string(registros[41])
    municipio_transporte   = transforma_string(registros[42])
    uf_endereco_transporte = transforma_string(registros[43])
    ie_transporte          = PoleUtil.formatar_ie(registros[44], transforma_string(registros[43]))
    quantidade             = PoleUtil.formatar_inteiro(int(registros[45]))
    especie                = transforma_string(registros[46])
    marca                  = transforma_string(registros[47])
    numeracao              = transforma_string(registros[48])
    peso_bruto             = PoleUtil.formatar_real(registros[49], 3)
    peso_liquido           = PoleUtil.formatar_real(registros[50], 3)
    observacao             = transforma_string(registros[56])
    vendedor               = transforma_string(registros[83])
    denegado               = (registros[84] == 'S')

    documento = PDF('NF-e ' + numero_nfe + ' - Série 001 - Nome da Empresa', diretorio + '/' + chave_de_acesso + '.pdf')
    documento.celula(19 * cm, 0.1 * cm, None, [Paragraph('Ped.: ' + locale.format('%i', int(cod_nota_fiscal), True, True), normal_direita)], False, posicao=(1 * cm, 0.6 * cm))
    documento.celula(15 * cm, 0.4 * cm, 'RECEBEMOS DE <b>Nome da Empresa - Restante da razão social LTDA</b> OS PRODUTOS CONSTANTES DA NOTA FISCAL INDICADA AO LADO', '')
    documento.celula( 5 * cm, .8 * cm, 'DATA DE RECEBIMENTO', '')
    documento.celula(10 * cm, .8 * cm, 'IDENTIFICAÇÃO E ASSINATURA DO RECEBEDOR', '&nbsp;')
    documento.celula( 4 * cm, 1.2 * cm, None, [Paragraph('<b>NF-e<br/>Nº '+numero_nfe+'<br/>Série:'+serie_nfe+'</b>', normal_centro)])
    documento.celula(19 * cm, 0.4 * cm, '················································································································································································································································································································································································································································','', borda = False)

    # Logotipo
    if logo is not None:
        I = Image(logo)
    else:
        I = Image()
    I.drawWidth = 13 * mm * I.drawWidth / I.drawHeight
    I.drawHeight = 13 * mm

    #Codigo de Barras
    barcode = BarCode('Code128', value = chave_de_acesso, barWidth = 0.26 * mm) #, 0.4 * mm, 6.8 * mm)
    #barcode.barWidth = 0.26 * mm

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

    colWidths = (1 * cm, 5.51 * cm, .92  * cm, .42  * cm, .58  * cm, .58  * cm, 1 * cm, 1.08 * cm, 1.125  * cm, 1.125  * cm, 1.125  * cm, 1.125  * cm, 1.125  * cm, 1.125  * cm, .58 * cm, .58 * cm)
    colWidths = [width * fonte_tab_pequena.fontSize/5. for width in colWidths]
    colWidths = tuple([colWidths[0], 19 * cm - sum(colWidths) + colWidths[1]] + colWidths[2:])

    sql_itens = ("SELECT cod_produto, descricao, classificacao_fiscal NCM, situacao_tributaria_A || situacao_tributaria_B, cfop, cod_unidade, quantidade, valor_unitario_liquido, "
                        "total_liquido, base_icms, icms, base_substituicao, substituicao, ipi, percentual_icms, percentual_ipi "
                        "FROM administrador.item_nota_fiscal i where cod_nota_fiscal = " + cod_nota_fiscal)
    cursor.execute(sql_itens)
    dados = cursor.fetchall()

    dados_tabela = []
    for linha in dados:
        mascara_ncm = ('%08d', '%02d')[linha[2] < 100]
        ncm = mascara_ncm % linha[2]
        if linha[2] > 99:
            ncm = ncm[:4] + '.' + ncm[4:6] + '.' + ncm[6:]
        dados_tabela.append(
            [
                PoleUtil.formatar_inteiro(linha[ 0]),
                Paragraph(linha[ 1], fonte_tab_grande),
                ncm,
                linha[ 3],
                linha[ 4],
                linha[ 5],
                PoleUtil.formatar_real(str(linha[ 6]).replace('.', ','), 4),
                PoleUtil.formatar_real(str(linha[ 7]).replace('.', ','), 4),
                PoleUtil.formatar_real(str(linha[ 8]).replace('.', ','), 2),
                PoleUtil.formatar_real(str(linha[ 9]).replace('.', ','), 2),
                PoleUtil.formatar_real(str(linha[10]).replace('.', ','), 2),
                PoleUtil.formatar_real(str(linha[11]).replace('.', ','), 2),
                PoleUtil.formatar_real(str(linha[12]).replace('.', ','), 2),
                PoleUtil.formatar_real(str(linha[13]).replace('.', ','), 2),
                PoleUtil.formatar_real(str(linha[14]).replace('.', ','), 2),
                PoleUtil.formatar_real(str(linha[15]).replace('.', ','), 2),
            ]
        )
    alt_comp = documento.altura(  14 * cm,   3 * cm, None, [Paragraph('INFORMAÇÕES COMPLEMENTARES', pequena_esquerda), Paragraph('Pedido: ' + PoleUtil.formatar_inteiro(cod_nota_fiscal) + ' - ' + vendedor + ' - Cliente: ' + cod_entidade + '<br/>&nbsp;<br/>' + observacao.replace('>', '<br/>').replace('&gt;', '<br/>').replace('  ', '&nbsp; '), normal_esquerda)])
    a3 = 15 * cm - alt_comp
    tabela, itens, altura = documento.tabela(5.4 * cm, a3, dados_tabela, colWidths, style=ts)
    #print tabela, itens, altura / cm, len(dados), a3 / cm
    #raw_input('----------------------')
    itens_extras = itens
    paginas = 1
    while itens_extras < len(dados):
        tabela_extra, i, altura = documento.tabela(19 * cm, 21 * cm, dados_tabela[itens_extras:],colWidths=(1 * cm, 5.51 * cm, .92  * cm, .42  * cm, .58  * cm, .58  * cm, 1 * cm, 1.08 * cm, 1.125  * cm, 1.125  * cm, 1.125  * cm, 1.125  * cm, 1.125  * cm, 1.125  * cm, .58 * cm, .58 * cm), style=ts)
        #print tabela_extra, i, altura / cm, len(dados), itens_extras
        #raw_input('----------------------')
        itens_extras += i
        paginas += 1

    # Dados Empresa
    a1_1 = documento.altura( 8 * cm, 1 * mm, None, [I,Paragraph('<b>Nome da Empresa</b>', normal_centro),Paragraph('<b>Restante da razão social LTDA</b>', pequena_centro),Paragraph('Av. Pres. Kennedy, 2272 - Pq. Ind. Lagoinha, Ribeirão Preto, SP - CEP 14095-220<br/>Fone: (16)3514-9966 - Fax: (16)3514-9969 - www.empresamercantil.com.br', pequena_centro)])
    a1_2 = documento.altura( 8 * cm, 1 * mm, 'NATUREZA DA OPERAÇÃO', natureza_operacao)
    a2 = documento.altura( 3.5 * cm, 1 * mm, None, [Paragraph('<b>DANFE</b>', normal_centro),Paragraph('Documento Auxiliar da Nota Fiscal Eletrônica<br/>&nbsp;', pequena_centro),Paragraph('0 - Entrada', pequena_esquerda),Paragraph('1 - Saída<br/>&nbsp;', pequena_esquerda),Paragraph('&nbsp;<br/><b>Nº '+numero_nfe+'</b>', normal_esquerda),Paragraph('<b>Série: '+serie_nfe+'</b>', normal_esquerda),Paragraph('&nbsp;<br/><b>Página 1 de ' + str(paginas) + '</b>', normal_centro)], borda = False)
    a3 = documento.altura( 7.5 * cm, 1 * mm, None, [Paragraph('Controle do Fisco<br/>&nbsp;', pequena_esquerda),barcode,Paragraph('<br/>&nbsp;<br/>&nbsp;', pequena_esquerda),Paragraph('Consulta de autenticidade no portal nacional da NF-e www.nfe.gov.br/portal ou no site da Sefaz Autorizada', pequena_centro)])
    if a1_1 + a1_2 > a2:
        a = a1_1 + a1_2
    else:
        a = a2
    if a < a3:
        a = a3
    documento.celula( 8 * cm, a, None, [I,Paragraph('<b>Nome da Empresa</b>', normal_centro),Paragraph('<b>Restante da razão social LTDA</b>', pequena_centro),Paragraph('Av. Pres. Kennedy, 2272 - Pq. Ind. Lagoinha, Ribeirão Preto, SP - CEP 14095-220<br/>Fone: (16)3514-9966 - Fax: (16)3514-9969 - www.empresamercantil.com.br', pequena_centro)])
    documento.celula( 3.5 * cm, a, None, [Paragraph('<b>DANFE</b>', normal_centro),Paragraph('Documento Auxiliar da Nota Fiscal Eletrônica<br/>&nbsp;', pequena_centro),Paragraph('0 - Entrada', pequena_esquerda),Paragraph('1 - Saída<br/>&nbsp;', pequena_esquerda),Paragraph('&nbsp;<br/><b>Nº '+numero_nfe+'</b>', normal_esquerda),Paragraph('<b>Série: '+serie_nfe+'</b>', normal_esquerda),Paragraph('&nbsp;<br/><b>Página 1 de ' + str(paginas) + '</b>', normal_centro)], borda = False)
    documento.celula( 7.5 * cm, a, None, [Paragraph('Controle do Fisco<br/>&nbsp;', pequena_esquerda),Paragraph('<br/>&nbsp;<br/>&nbsp;<br/>&nbsp;<br/>&nbsp;<br/>&nbsp;<br/>&nbsp;<br/>&nbsp;<br/>&nbsp;', pequena_esquerda),Paragraph('Consulta de autenticidade no portal nacional da NF-e<br/>www.nfe.fazenda.gov.br ou no site da Sefaz Autorizada', normal_centro)])

    # Natureza da Operação flutuante
    documento.celula( 8 * cm, 1 * mm, 'NATUREZA DA OPERAÇÃO', natureza_operacao, posicao = (1 * cm, 2.6 * cm + a - a1_2))

    #Posição Chave de acesso celula flutuante
    chave_de_acesso = [Paragraph('Chave de acesso', pequena_esquerda), Paragraph(' '.join([chave_de_acesso[x*4:x*4+4] for x in range(11)]), fonte_chave_acesso)]
    documento.celula(7.2 * cm,.6 * cm, None, chave_de_acesso, posicao=(12.65 * cm, 4 * cm))
    #Posição Entrada Saida celula flutuante
    if tipo_nota=='S':
        tipo = "1"
    else:
        tipo = "0"
    documento.celula(.4* cm,.4 * cm, None,[Paragraph(str(tipo), normal_centro)],posicao=(10.65 * cm, 3.3 * cm))
    documento.celula(10 * mm, 1 * mm, None,[barcode],posicao=(15.75 * cm, 2.82 * cm), borda = False)

    #documento.celula( 19 * cm, 3.8 * mm, None, [Paragraph('PROTOCOLO DE AUTORIZAÇÃO DE USO', pequena_esquerda), Paragraph('00000000000000000000000000000000000', normal_esquerda)])

    # Inscrição estadual
    documento.celula( 3.5 * cm, 1 * mm, 'INSCRIÇÃO ESTADUAL', ie_empresa)
    documento.celula( 4.5 * cm, 1 * mm, None, [Paragraph('INSCRIÇÃO ESTADUAL DO SUBST. TRIB.', pequena_esquerda),Paragraph(ie_sub_empresa,normal_direita)])
    documento.celula( 3.5 * cm, 1 * mm, 'CNPJ', cnpj_empresa)
    documento.celula( 7.5 * cm, 1 * mm, None, [Paragraph('PROTOCOLO DE AUTORIZAÇÃO DE USO', pequena_esquerda), Paragraph(protocolo, normal_esquerda)])

    # DESTINATARIO REMETENTE
    documento.celula( 19 * cm, 1 * mm, None, [Paragraph('DESTINATÁRIO / REMETENTE', pequena_esquerda)], borda = False)

    #print razao_social
    documento.celula(14.0 * cm, 1 * mm, 'NOME/RAZAO SOCIAL', razao_social)
    documento.celula( 2.5 * cm, 1 * mm, 'CNPJ/CPF', cnpj)
    documento.celula( 2.5 * cm, 1 * mm, 'DATA EMISSÃO', data_emissao)

    documento.celula(11.1 * cm, 1 * mm, 'ENDEREÇO', endereco)
    documento.celula( 4.0 * cm, 1 * mm, 'BAIRRO/DISTRITO', bairro)
    documento.celula( 1.4 * cm, 1 * mm, 'CEP', cep)
    documento.celula( 2.5 * cm, 1 * mm, 'DATA ENTRADA/SAIDA', data_entrada_saida)

    documento.celula(10.5 * cm, 1 * mm, 'MUNICÍPIO', municipio)
    documento.celula( 2.5 * cm, 1 * mm, 'FONE/FAX', fone_fax)
    documento.celula( 0.5 * cm, 1 * mm, 'UF', uf)
    documento.celula( 3.0 * cm, 1 * mm, 'INSCRIÇÃO ESTADUAL', ie)
    documento.celula( 2.5 * cm, 1 * mm, 'HORA ENTRADA/SAIDA' , hora_entrada_saida)

    # FATURA
    documento.celula( 19 * cm, 3.8 * mm, None, [Paragraph('FATURA', pequena_esquerda)], borda = False)

    # ALTURA PAGAMENTO 1 DETALHES
    a1 = documento.altura( 1.8 * cm, 1 * mm, None, [Paragraph('01/02/2009', normal_direita),Paragraph('100,00', normal_direita)])


    # FORMA DE PAGAMENTO
    documento.celula( 4* cm, a1, None, [Paragraph('FORMA DE PAGAMENTO<br/>', pequena_esquerda),Paragraph(tipo_pagamento, normal_esquerda)])

    sql_parcelas=("select cod_nota_fiscal, num_parcela, valor_parcela, to_char(vencimento_parcela,'DD/MM/YYYY') "
                          "from administrador.parcela_nota_fiscal "
                          "where cod_nota_fiscal = " + cod_nota_fiscal + " order by num_parcela")

    cursor.execute(sql_parcelas)
    parcelas = cursor.fetchall()
    if not parcelas:
        parcelas = []

    for parcela in parcelas:
        data_parcela  = transforma_string(parcela[3])
        valor_parcela = PoleUtil.formatar_real(parcela[2])
        num_parcela   = transforma_string(parcela[1])
        # PAGAMENTO 1
        documento.celula( .3 * cm, a1, None, [Paragraph('&nbsp;', pequena_centro), Paragraph('&nbsp;' + num_parcela, normal_centro)])

        # PAGAMENTO 1 DETALHES
        documento.celula( 2.2 * cm, a1, None, [Paragraph(data_parcela, normal_direita),Paragraph(valor_parcela, normal_direita)])
    #
    # Preenche campo de parcelas em branco caso tenha menos pagamentos que 6
    #
    if len(parcelas) < 6:
        for parcela_branco in range(6-len(parcelas)):
            # PAGAMENTO 1
            documento.celula( .3 * cm, a1, None, [Paragraph('&nbsp;', pequena_centro), Paragraph('&nbsp;', normal_centro)], borda = False)

            # PAGAMENTO 1 DETALHES
            documento.celula( 2.2 * cm, a1, None, [Paragraph('&nbsp;', normal_direita),Paragraph('&nbsp;', normal_direita)],borda = False)

    # CALCULO DO IMPOSTO
    documento.celula( 19 * cm, 3.8 * mm, None, [Paragraph('CÁLCULO DO IMPOSTO', pequena_esquerda)], borda = False)

    # BASE DE CALCULO ICMS
    documento.celula( 3.8 * cm, 3.8 * mm, 'BASE DE CÁLCULO DO ICMS', base_calculo_icms, alinhamento = 'direita')

    # VALOR DO ICMS
    documento.celula( 3.8 * cm, 3.8 * mm, 'VALOR DO ICMS', vl_icms, alinhamento = 'direita')

    # BASE DE CALCULO DO ICMS ST
    documento.celula( 3.8 * cm, 3.8 * mm, 'BASE DE CÁLCULO DO ICMS ST', base_calculo_icms_st, alinhamento = 'direita')

    # VALOR DO ICMS ST
    documento.celula( 3.8 * cm, 3.8 * mm, 'VALOR DO ICMS ST', vl_icms_st, alinhamento = 'direita')

    # VALOR TOTAL DOS PRODUTOS
    documento.celula( 3.8 * cm, 3.8 * mm, 'VALOR TOTAL DOS PRODUTOS', vl_total_produtos, alinhamento = 'direita')

    # VALOR DO FRETE
    #documento.celula( 2.85 * cm, 3.8 * mm, 'VALOR DO FRETE', vl_frete, alinhamento = 'direita')
    documento.celula( 2.85 * cm, 3.8 * mm, 'VALOR DO FRETE', '0,00', alinhamento = 'direita')

    # VALOR DO SEGURO
    documento.celula( 2.85 * cm, 3.8 * mm, 'VALOR DO SEGURO', vl_seguro, alinhamento = 'direita')

    # DESCONTO
    documento.celula( 2.85 * cm, 3.8 * mm, 'DESCONTO', '0,00', alinhamento = 'direita')

    # OUTRAS DESPESAS ACESSÓRIAS
    documento.celula( 2.85 * cm, 3.8 * mm, 'OUTRAS DESPESAS', outras_despesas, alinhamento = 'direita')

    # VALOR DO IPI
    documento.celula( 3.8 * cm, 3.8 * mm, 'VALOR DO IPI', vl_ipi, alinhamento = 'direita')

    # VALOR TOTAL DA NOTA
    documento.celula( 3.8 * cm, 3.8 * mm, 'VALOR TOTAL DA NOTA', vl_total_nota, alinhamento = 'direita')

    # TRANSPORTADOR/VOLUMES TRANSPORTADOS
    documento.celula( 19 * cm, 3.8 * mm, None, [Paragraph('TRANSPORTADOR/VOLUMES TRANSPORTADOS', pequena_esquerda)], borda = False)

     # FRETE ALTURA
    a1 = documento.altura( 3.7 * cm, 3.8 * mm, None, [Paragraph('FRETE POR CONTA', pequena_esquerda), Paragraph('0-EMITENTE', pequena_esquerda), Paragraph('1-DESTINATÁRIO', pequena_esquerda)])

    # RAZÃO SOCIAL
    #documento.celula( 6.5 * cm, a1, None, [Paragraph('RAZÃO SOCIAL', pequena_esquerda), Paragraph(razao_transportadora, normal_esquerda)])
    documento.celula( 10 * cm, a1, 'RAZÃO SOCIAL', razao_transportadora)

    # FRETE
    documento.celula( 2.5 * cm, a1, None, [Paragraph('FRETE POR CONTA', pequena_esquerda), Paragraph('0-EMITENTE', pequena_esquerda), Paragraph('1-DESTINATÁRIO', pequena_esquerda)])

    # CÓDIGO ANTT
    documento.celula( 1.5 * cm, a1, 'CÓDIGO ANTT', '')

    # PLACA DO VEÍCULO
    documento.celula( 2 * cm, a1, 'PLACA DO VEÍCULO', placa_veiculo)

    # UF
    documento.celula(0.5 * cm, a1, 'UF', uf_transporte)

    # CNPJ/CPF
    documento.celula( 2.5 * cm, a1, 'CNPJ/CPF', cnpj_transporte)

    #FRETE POR CONTA NUMERO FLUTUANTE
    documento.celula(.4 * cm,.4 * cm, None,[Paragraph(frete_conta[int(frete_por_conta)],normal_centro)],posicao=(12.9 * cm, 10.95 * cm))

    # ENDEREÇO
    documento.celula( 10* cm, 3.8 * mm, 'ENDEREÇO', endereco_transporte)

    # MUNICÍPIO
    documento.celula( 6 * cm, 3.8 * mm, 'MUNICÍPIO', municipio_transporte)

    # UF
    documento.celula( .5 * cm, 3.8 * mm, 'UF', uf_endereco_transporte)

    # INSCRIÇÃO ESTADUAL
    documento.celula( 2.5 * cm, 3.8 * mm, 'INSCRIÇÃO ESTADUAL', ie_transporte)

    # QUANTIDADE
    documento.celula( 2.5 * cm, 3.8 * mm, 'QUANTIDADE', quantidade, alinhamento = 'direita')

    # ESPÉCIE
    documento.celula( 4.1 * cm, 3.8 * mm, 'ESPÉCIE', especie)

    # MARCA
    documento.celula( 4.2 * cm, 3.8 * mm, 'MARCA', marca)

    # NUMERAÇÃO
    documento.celula( 3 * cm, 3.8 * mm, 'NUMERAÇÃO', numeracao)

    # PESO BRUTO
    documento.celula( 2.6 * cm, 3.8 * mm, 'PESO BRUTO', peso_bruto, alinhamento = 'direita')

    # PESO LÍQUIDO
    documento.celula( 2.6 * cm, 3.8 * mm, 'PESO LÍQUIDO', peso_liquido, alinhamento = 'direita')

    # DADOS DO PRODUTO/SERVIÇO
    documento.celula( 19 * cm, 3.8 * mm, None, [Paragraph('DADOS DO PRODUTO/SERVIÇO', pequena_esquerda)], borda = False)


    # ALÍQ. ICMS - altura
    a1 = documento.altura( .6 * cm, 3.8 * mm, None, [Paragraph('ALÍQ. ICMS', pequena_esquerda)])

    # CÓDIGO
    documento.celula(colWidths[ 0], a1, None, [Paragraph('CÓDIGO', pequena_centro)])

    # DESCRIÇÃO DO PRODUTO/SERVIÇO
    documento.celula(colWidths[ 1], a1, None, [Paragraph('DESCRIÇÃO DO PRODUTO/SERVIÇO', pequena_centro)])

    # NCM/SH
    documento.celula(colWidths[ 2], a1, None, [Paragraph('NCM/SH', pequena_esquerda)])

    # CST
    documento.celula(colWidths[ 3], a1, None, [Paragraph('CST', pequena_esquerda)])

    # CFOP
    documento.celula(colWidths[ 4], a1, None, [Paragraph('CFOP', pequena_centro)])

    # UNID.
    documento.celula(colWidths[ 5], a1, None, [Paragraph('UNID.', pequena_esquerda)])

    # QTD
    documento.celula(colWidths[ 6], a1, None, [Paragraph('QTD', pequena_centro)])

    # VLR. UNIT.
    documento.celula(colWidths[ 7], a1, None, [Paragraph('VLR. UNIT.', pequena_centro)])

    # VLR. TOTAL
    documento.celula(colWidths[ 8], a1, None, [Paragraph('VLR. TOTAL', pequena_centro)])

    # BC ICMS
    documento.celula(colWidths[ 9], a1, None, [Paragraph('BC ICMS', pequena_centro)])

    # VLR. ICMS
    documento.celula(colWidths[10], a1, None, [Paragraph('VLR. ICMS', pequena_centro)])

    # BC ICMS ST
    documento.celula(colWidths[11], a1, None, [Paragraph('BC ICMS ST', pequena_centro)])

    # VLR. ICMS ST
    documento.celula(colWidths[12], a1, None, [Paragraph('VLR. ICMS ST', pequena_centro)])

    # VLR. IPI
    documento.celula(colWidths[13], a1, None, [Paragraph('VLR. IPI', pequena_centro)])

    # ALÍQ. ICMS
    documento.celula(colWidths[14], a1, None, [Paragraph('ALÍQ. ICMS', pequena_centro)])

    # ALÍQ. IPI
    documento.celula(colWidths[15], a1, None, [Paragraph('ALÍQ. IPI', pequena_centro)])

    #DADOS ADICIONAIS
    documento.celula( 19 * cm, 3.8 * mm, None, [Paragraph('DADOS ADICIONAIS', pequena_esquerda)], borda = False, posicao=(1 * cm, 28.4 * cm - alt_comp))
    documento.celula( 14 * cm,      alt_comp, None,      [Paragraph('INFORMAÇÕES COMPLEMENTARES', pequena_esquerda), Paragraph('Pedido: ' + PoleUtil.formatar_inteiro(cod_nota_fiscal) + ' - ' + vendedor + ' - Cliente: ' + cod_entidade + '<br/>&nbsp;<br/>' + observacao.replace('>', '<br/>').replace('&gt;', '<br/>').replace('  ', '&nbsp; '), normal_esquerda)], posicao=(1 * cm, 28.7 * cm - alt_comp))
    if denegado:
        documento.celula(  5 * cm,       alt_comp, None, [Paragraph('RESERVADO AO FISCO', pequena_esquerda), Paragraph('USO DENEGADO', extra_grande_centro), Paragraph('&nbsp;<br/>NFe SEM VALOR', grande_centro)], posicao=(15 * cm, 28.7 * cm - alt_comp))
    else:
        documento.celula(  5 * cm,       alt_comp, None, [Paragraph('RESERVADO AO FISCO', pequena_esquerda)],posicao=(15 * cm, 28.7 * cm - alt_comp))

    #Propaganda
    documento.celula( 19 * cm, 1 * mm, None, [Paragraph('NF-e ERP 3.0 - www.juniorpolegato.com.br', minuscula_direita)], posicao = (1 * cm, 28.7 * cm), borda = False)


    documento.celula(19 * cm, 15 * cm - alt_comp, None, (tabela,), borda=False, espacamento=0)

    pagina = 1
    while itens < len(dados):
        pagina += 1
        documento.nova_pagina()
        # cabec
        documento.celula(19 * cm, 1.2 * cm, '', '', borda = False)
        documento.celula(19 * cm, 0.4 * cm, '················································································································································································································································································································································································································································','', borda = False)

        # Dados Empresa
        a1_1 = documento.altura( 8 * cm, 1 * mm, None, [I,Paragraph('<b>Nome da Empresa</b>', normal_centro),Paragraph('<b>Restante da razão social LTDA</b>', pequena_centro),Paragraph('Av. Pres. Kennedy, 2272 - Pq. Ind. Lagoinha, Ribeirão Preto, SP - CEP 14095-220<br/>Fone: (16)3514-9966 - Fax: (16)3514-9969 - www.empresamercantil.com.br', pequena_centro)])
        a1_2 = documento.altura( 8 * cm, 1 * mm, 'NATUREZA DA OPERAÇÃO', natureza_operacao)
        a2 = documento.altura( 3.5 * cm, 1 * mm, None, [Paragraph('<b>DANFE</b>', normal_centro),Paragraph('Documento Auxiliar da Nota Fiscal Eletrônica<br/>&nbsp;', pequena_centro),Paragraph('0 - Entrada', pequena_esquerda),Paragraph('1 - Saída<br/>&nbsp;', pequena_esquerda),Paragraph('&nbsp;<br/><b>Nº '+numero_nfe+'</b>', normal_esquerda),Paragraph('<b>Série: '+serie_nfe+'</b>', normal_esquerda),Paragraph('&nbsp;<br/><b>Página ' + str(pagina) + ' de ' + str(paginas) + '</b>', normal_centro)], borda = False)
        a3 = documento.altura( 7.5 * cm, 1 * mm, None, [Paragraph('Controle do Fisco<br/>&nbsp;', pequena_esquerda),barcode,Paragraph('<br/>&nbsp;<br/>&nbsp;', pequena_esquerda),Paragraph('Consulta de autenticidade no portal nacional da NF-e www.nfe.gov.br/portal ou no site da Sefaz Autorizada', pequena_centro)])
        if a1_1 + a1_2 > a2:
            a = a1_1 + a1_2
        else:
            a = a2
        if a < a3:
            a = a3
        documento.celula( 8 * cm, a, None, [I,Paragraph('<b>Nome da Empresa</b>', normal_centro),Paragraph('<b>Restante da razão social LTDA</b>', pequena_centro),Paragraph('Av. Pres. Kennedy, 2272 - Pq. Ind. Lagoinha, Ribeirão Preto, SP - CEP 14095-220<br/>Fone: (16)3514-9966 - Fax: (16)3514-9969 - www.empresamercantil.com.br', pequena_centro)])
        documento.celula( 3.5 * cm, a, None, [Paragraph('<b>DANFE</b>', normal_centro),Paragraph('Documento Auxiliar da Nota Fiscal Eletrônica<br/>&nbsp;', pequena_centro),Paragraph('0 - Entrada', pequena_esquerda),Paragraph('1 - Saída<br/>&nbsp;', pequena_esquerda),Paragraph('&nbsp;<br/><b>Nº '+numero_nfe+'</b>', normal_esquerda),Paragraph('<b>Série: '+serie_nfe+'</b>', normal_esquerda),Paragraph('&nbsp;<br/><b>Página ' + str(pagina) + ' de ' + str(paginas) + '</b>', normal_centro)], borda = False)
        documento.celula( 7.5 * cm, a, None, [Paragraph('Controle do Fisco<br/>&nbsp;', pequena_esquerda),Paragraph('<br/>&nbsp;<br/>&nbsp;<br/>&nbsp;<br/>&nbsp;<br/>&nbsp;<br/>&nbsp;<br/>&nbsp;<br/>&nbsp;', pequena_esquerda),Paragraph('Consulta de autenticidade no portal nacional da NF-e<br/>www.nfe.fazenda.gov.br ou no site da Sefaz Autorizada', normal_centro)])

        # Natureza da Operação flutuante
        documento.celula( 8 * cm, 1 * mm, 'NATUREZA DA OPERAÇÃO', natureza_operacao, posicao = (1 * cm, 2.6 * cm + a - a1_2))

        #Posição Chave de acesso celula flutuante
        documento.celula(7.2 * cm,.6 * cm, None, chave_de_acesso, posicao=(12.65 * cm, 4 * cm))
        #Posição Entrada Saida celula flutuante
        if tipo_nota=='S':
            tipo = "1"
        else:
            tipo = "0"
        documento.celula(.4* cm,.4 * cm, None,[Paragraph(str(tipo), normal_centro)],posicao=(10.65 * cm, 3.3 * cm))
        documento.celula(10 * mm, 1 * mm, None,[barcode],posicao=(15.75 * cm, 2.82 * cm), borda = False)

        #documento.celula( 19 * cm, 3.8 * mm, None, [Paragraph('PROTOCOLO DE AUTORIZAÇÃO DE USO', pequena_esquerda), Paragraph('00000000000000000000000000000000000', normal_esquerda)])

        # Inscrição estadual
        documento.celula( 3.5 * cm, 1 * mm, 'INSCRIÇÃO ESTADUAL', ie_empresa)
        documento.celula( 4.5 * cm, 1 * mm, None, [Paragraph('INSCRIÇÃO ESTADUAL DO SUBST. TRIB.', pequena_esquerda),Paragraph(ie_sub_empresa,normal_direita)])
        documento.celula( 3.5 * cm, 1 * mm, 'CNPJ', cnpj_empresa)
        documento.celula( 7.5 * cm, 1 * mm, None, [Paragraph('PROTOCOLO DE AUTORIZAÇÃO DE USO', pequena_esquerda), Paragraph(protocolo, normal_esquerda)])

        # DADOS DO PRODUTO/SERVIÇO
        documento.celula( 19 * cm, 3.8 * mm, None, [Paragraph('DADOS DO PRODUTO/SERVIÇO', pequena_esquerda)], borda = False)

        # ALÍQ. ICMS - altura
        a1 = documento.altura( .6 * cm, 3.8 * mm, None, [Paragraph('ALÍQ. ICMS', pequena_esquerda)])

        # CÓDIGO
        documento.celula( 1 * cm, a1, None, [Paragraph('CÓDIGO', pequena_centro)])

        # DESCRIÇÃO DO PRODUTO/SERVIÇO
        documento.celula( 5.51 * cm, a1, None, [Paragraph('DESCRIÇÃO DO PRODUTO/SERVIÇO', pequena_centro)])

        # NCM/SH
        documento.celula( .92 * cm, a1, None, [Paragraph('NCM/SH', pequena_esquerda)])

        # CST
        documento.celula( .42 * cm, a1, None, [Paragraph('CST', pequena_esquerda)])

        # CFOP
        documento.celula( .58 * cm, a1, None, [Paragraph('CFOP', pequena_centro)])

        # UNID.
        documento.celula( .58 * cm, a1, None, [Paragraph('UNID.', pequena_esquerda)])

        # QTD
        documento.celula( 1 * cm, a1, None, [Paragraph('QTD', pequena_centro)])

        # VLR. UNIT.
        documento.celula( 1.08 * cm, a1, None, [Paragraph('VLR. UNIT.', pequena_centro)])

        # VLR. TOTAL
        documento.celula( 1.125 * cm, a1, None, [Paragraph('VLR. TOTAL', pequena_centro)])

        # BC ICMS
        documento.celula( 1.125 * cm, a1, None, [Paragraph('BC ICMS', pequena_centro)])

        # VLR. ICMS
        documento.celula( 1.125 * cm, a1, None, [Paragraph('VLR. ICMS', pequena_centro)])

        # BC ICMS ST
        documento.celula( 1.125 * cm, a1, None, [Paragraph('BC ICMS ST', pequena_centro)])

        # VLR. ICMS ST
        documento.celula( 1.125 * cm, a1, None, [Paragraph('VLR. ICMS ST', pequena_centro)])

        # VLR. IPI
        documento.celula( 1.125 * cm, a1, None, [Paragraph('VLR. IPI', pequena_centro)])

        # ALÍQ. ICMS
        documento.celula( .58 * cm, a1, None, [Paragraph('ALÍQ. ICMS', pequena_centro)])

        # ALÍQ. IPI
        documento.celula( .58 * cm, a1, None, [Paragraph('ALÍQ. IPI', pequena_centro)])


        tabela, i, altura = documento.tabela(19 * cm, 21 * cm, dados_tabela[itens:],colWidths=(1 * cm, 5.51 * cm, .92  * cm, .42  * cm, .58  * cm, .58  * cm, 1 * cm, 1.08 * cm, 1.125  * cm, 1.125  * cm, 1.125  * cm, 1.125  * cm, 1.125  * cm, 1.125  * cm, .58 * cm, .58 * cm), style=ts)
        documento.celula(19 * cm, 21 * cm, None, (tabela,), borda=False, espacamento=0)
        itens += i

    documento.salvar()
