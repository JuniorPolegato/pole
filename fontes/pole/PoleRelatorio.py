#!/usr/bin/env python
# -*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # ##
# Importar os módulos necessários para utilização do GTK com suport a GtkBuilder
import pygtk
pygtk.require("2.0")
import gtk
from gtk import gdk
import zlib
import base64
import pole
from datetime import datetime, timedelta
Paragraph = pole.pdf.Paragraph
normal_esquerda = pole.pdf.normal_esquerda


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # ##
# Classe que intermedia um widget do GTK+ para facilitar acesso a consultar e
#     alterar valores de propriedades dos widgets, tal como as propriedades das
#     classes em Python, se comportando como um widget virtual. Dessa forma, não
#     precisa usar as funções GTK widget.set_propriedade(valor) ou
#     widget.get_propriedade(), basta usar widget.propriedade = valor ou
#     widget.propriedade, respectivamente. Para obter o próprio widget,
#     use widget.widget
class VirtualWidget(object):
    def __init__(self, widget):
        object.__setattr__(self, "widget", widget)
    def __getattribute__(self, atributo):
        if atributo == "widget":
            return object.__getattribute__(self, atributo)
        try:
            resultado = object.__getattribute__(object.__getattribute__(self,
                                                      "widget"), atributo)
            return resultado
        except:
           try:
                resultado = object.__getattribute__(object.__getattribute__(
                                        self, "widget"), "get_" + atributo)
                return resultado()
           except:
                pass
        return None
    def __setattr__(self, atributo, valor):
        try:
            consulta = object.__getattribute__(object.__getattribute__(self,
                                                         "widget"), atributo)
            object.__setattr__(object.__getattribute__(self,
                                                  "widget"), atributo, valor)
        except:
            try:
                consulta = object.__getattribute__(object.__getattribute__(
                                        self, "widget"), "set_" + atributo)
                consulta(valor)
            except:
                object.__setattr__(object.__getattribute__(self,
                                                  "widget"), atributo, valor)
        return

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # ##
# Classe que contem todo o código relativo ao projeto em Glade correspondente
class Projeto(object):

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # ##
    # Função chamada toda vez que se requer informações de algum atributo/membro
    #     da classe. Aqui interceptamos verificando se já foi este consultado.
    #     Se não foi consultado ainda, procura este nome dentre os nomes de
    #     widgets do Glade. A busca retorna None se não for nome de um
    #     widget ou a instância do widget correspondente ao nome procurado. Este
    #     resultado fica guardado em um dicionário como um widget virtual,
    #     onde o nome do atribuito corresponderá a None ou à instância do widget
    #     virtual. No caso de já ter sido consultado, faz a procura deste no
    #     dicionário, onde se for None, continua com a busca do atributo
    #     normalmente, mas se não for None, isto é, será uma instância de um
    #     widget virtual correspondente, retorna essa instância.
    def __getattribute__(self, atributo):
        if atributo in object.__getattribute__(self, "atributos_consultados"):
            if object.__getattribute__(self, "atributos_consultados")[atributo]:
                return object.__getattribute__(self,
                                              "atributos_consultados")[atributo]
            return object.__getattribute__(self, atributo)
        widget = object.__getattribute__(self, "interface").get_object(atributo)
        if widget:
            widget = VirtualWidget(widget)
            object.__getattribute__(self,
                                   "atributos_consultados")[atributo] = widget
            return widget
        else:
            object.__getattribute__(self,
                                       "atributos_consultados")[atributo] = None
        return object.__getattribute__(self, atributo)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # ##
    # Inicialização da classe inicializando o dicionário consultados,
    #     o qual conterá o nome dos atributos da classe consultados, cada
    #     qual referenciando o widget do Glade ou None se não for widget,
    #     carregando a interface utilizando-se do GtkBuilder e
    #     conectando os sinais/eventos às suas repectivas funções, além de
    #     criar uma coluna texto para cada combo correspondente à primeira
    #     coluna do modelo
    def __init__(self, paisagem, data_inicial, data_final, titulo_relatorio, larguras, cabecalhos, tipos, casas, soma, sql, dados, conexao, pdf = None, finalizar = True, sumario = None):
        self.atributos_consultados = {}
        self.interface = gtk.Builder()
        #self.interface.add_from_string(open("/home/eliezer/erp_3.0.0/fontes/relatorios/relatorios.ui").read())
        #compilar pra jogar a tela aqui 
        self.interface = pole.gtk.build_interface(zlib.decompress(base64.b64decode("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")))
        #compentar quando for compilar
        #self.interface = pole.gtk.build_interface(open("/home/eliezer/erp_3.0.0/fontes/relatorios/relatorios.ui").read())
        
        
        self.interface.connect_signals(self)
        
        # Criar uma coluna de dados para os combos, por padrão a coluna 0
        # Comente ou altere para a coluna desejada
        for combo in [x for x in self.interface.get_objects()
                                                    if type(x) == gtk.ComboBox]:
            celula = gtk.CellRendererText()
            combo.pack_start(celula)
            combo.add_attribute(celula, "text", 0)
        # Resolver problema de imagens não exibidas nos botões
        # Comente caso queira o comportamento configurado no Gnome, pois
        #     a partir da versão 2.28 por padrão não mostra, sendo que
        #     para alterar o padrão edite via
        #     "Aplicativos->Sistema->Editor de configurações"
        #     a chave "/desktop/gnome/interface/buttons_have_icons" ou execute
        #     "gconftool --toggle /desktop/gnome/interface/buttons_have_icons"
        for botao in [x for x in self.interface.get_objects()
                                                      if type(x) == gtk.Button]:
            try:
                botao.child.child.get_children()[0].show()
            except:
                pass
        # Digite abaixo o seu código Python para ser
        #    executado antes de "abrir" a janela
        self.data_inicial = data_inicial
        self.data_final = data_final
        self.titulo_relatorio = titulo_relatorio
        self.larguras = [l*pole.pdf.cm for l in larguras]
        self.cabecalhos = cabecalhos
        self.tipos = tipos
        self.casas = casas

        self.soma = soma
        self.paisagem = paisagem
        self.ts = [('GRID', (0,0), (-1,-1),0.5, pole.pdf.colors.black),
                    ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                    ('ALIGN',(0,0),(-1,-1),'LEFT'),
                    ('TOPPADDING', (0,0), (-1,-1), 0),
                    ('RIGHTPADDING', (0,0), (-1,-1), 1*pole.pdf.mm),
                    ('LEFTPADDING', (0,0), (-1,-1), 1*pole.pdf.mm),
                    ('FONTSIZE', (0,0), (-1,-1), pole.pdf.normal_centro.fontSize),
                    ('LEADING', (0,0), (-1,-1), pole.pdf.normal_centro.leading),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 1)                
                  ]
        for coluna, tipo in enumerate(self.tipos):
            if tipo in ('int', 'float'):
                self.ts.append(('ALIGN', (coluna, 0), (coluna, -1), 'RIGHT'))
        
        
        self.sql = sql
        self.dados = dados
        
        
        #print "sql oficial relatorio ", sql
        #print self.dados
        self.conexao = conexao
        
        sql = self.sql
        cursor = self.conexao.cursor()
        print "EM RELATORIOSSSSSSSS", sql
        try:
            cursor.execute(sql)
            print sql 
            registros = cursor.fetchall()
            if not len (registros):
                pole.gtk.message(self.jn_principal, "Não consta dados no Período Selecionado")
                return
        except:
            if self.dados != '':
                    registros = self.dados
            else:
                pole.gtk.message(self.jn_principal, "Verifique os campos para o relatório",gtk.MESSAGE_ERROR)            
            
        cm = pole.pdf.cm
        mm = pole.pdf.mm
        #logo
        I = pole.pdf.Image("/usr/local/ERP_3.0.0/Imagens/okubo_logo.jpg")
        I.drawWidth = 13 * mm * I.drawWidth / I.drawHeight
        I.drawHeight = 13 * mm
        
        #define paisagem ou retrato
        soma_larguras = 0.0
        if self.paisagem == "":
            for largura in range (len(self.larguras)):
                soma_larguras += self.larguras[largura]/cm
            if soma_larguras <= 19:
                self.paisagem = False
            else:
                self.paisagem = True
            
        if self.paisagem == True:
            disponivel_altura = 19*cm
            altura_folha = 19*cm
            largura_folha = pole.pdf.A4[1]-2*cm
            largura_fixo = int(pole.pdf.A4[1]-2.1*cm)
            
        else:
            disponivel_altura = 27.7*cm
            altura_folha = 27.7*cm
            largura_folha = 19*cm
            largura_fixo = 19*cm
        
        #inicia PDF 
        if pdf is None:
            pdf = pole.pdf.PDF(paisagem = self.paisagem, nome_do_arquivo = "/tmp/"+self.titulo_relatorio.replace('/','-')+".pdf", titulo = self.titulo_relatorio+ " - "+self.data_inicial+" à "+self.data_final)
        else:
            pdf.nova_pagina()
        self.pdf = pdf

        #estilo do relatorio
        grande_esquerda = pole.pdf.ParagraphStyle('normal', fontSize = 18, leading = 18, alignment = pole.pdf.TA_LEFT)        
        
        disponivel_altura -= pdf.celula(I.drawWidth, 0.5*cm, None, [I], borda = False)[3]
        pdf.celula(10*cm , I.drawHeight, None, [pole.pdf.Paragraph('<br/><b>OKUBO MERCANTIL - PRODUTOS PARA FIXAÇÃO, ELEVAÇÃO E COBERTURA LTDA</b>',pole.pdf.pequena_centro),
                                                pole.pdf.Paragraph('Av. Pres. Kennedy, 2272 - Pq. Ind. Lagoinha, Ribeirão Preto, SP - CEP 14095-220<br/>Fone: (16)3514-9966 - Fax: (16)3514-9969<br/> www.okubomercantil.com.br',pole.pdf.pequena_centro)],borda = False)
        pdf.celula(largura_folha - 10*cm - I.drawWidth, I.drawHeight,'', '', borda = False)
        #pula 0,5 cm
        disponivel_altura -= pdf.celula(largura_folha, 0.5*cm, '', '', borda = False)[3] 
        #pegando titulo do relatorio
        disponivel_altura -= pdf.celula(largura_folha, 0.1*cm, None, [pole.pdf.Paragraph(self.titulo_relatorio,grande_esquerda)], borda = False)[3]
        disponivel_altura -= pdf.celula(largura_folha, 0.1*cm, None, [pole.pdf.Paragraph(self.data_inicial+" à "+self.data_final,pole.pdf.normal_esquerda)], borda = False)[3]
        disponivel_altura -= pdf.celula(largura_folha, 0.5*cm, '', '', borda = False)[3]
        #pdf.celula(largura_folha , disponivel_altura,'', str(largura_folha*cm), borda = True)
        
        altura_cabecalho = 0
        
        for largura, cabecalho in zip(self.larguras, self.cabecalhos):

            altura_cabecalho = max(altura_cabecalho,pdf.altura(largura, 1, None, [pole.pdf.Paragraph(cabecalho, pole.pdf.normal_centro)]))
        
        for largura, cabecalho,tipo in zip(self.larguras, self.cabecalhos, self.tipos):
            if tipo in ('int', 'float'):
                pdf.celula(largura, altura_cabecalho, None, [pole.pdf.Paragraph(cabecalho, pole.pdf.normal_direita)])
            else:
                pdf.celula(largura, altura_cabecalho, None, [pole.pdf.Paragraph(cabecalho, pole.pdf.normal_esquerda)])
                
        disponivel_altura -= altura_cabecalho
        total_geral = 0
        
        if len(self.dados):
            registros, dados_tabela = zip(*self.dados)
            dados_tabela = [[((' ','X')[c==True], (c, Paragraph(c, normal_esquerda))[t=='str'])[type(c)!=bool] for c, t in zip(l, tipos)] for l in dados_tabela]
        else:
            dados_tabela = []
            for registro in registros:
                linha = []
                linhatotal = []
                total = 0 
                tipos = {'str': str, 'int': int, 'float': float, 'bool': bool}
                
                for campo,tipo,casa in zip (registro,self.tipos,self.casas):
                    try:
                        conteudo = pole.util.convert_and_format(campo,tipos[tipo],casa)[1]
                        conteudo = (conteudo, Paragraph(conteudo, normal_esquerda))[tipos[tipo] == str]
                        linha.append(conteudo)
                    except ValueError:
                        linha.append((str(campo), '')[campo is None])                    
                dados_tabela.append(linha)

        #totais ou rodape dos dados
        #automatizar auqiq ----------------
        
        linhatotal = []
        for n,soma in enumerate(self.soma):            
            if n == 0:
                linhatotal.append([pole.pdf.Paragraph("Totais",pole.pdf.normal_esquerda)])
            else:
                linhatotal.append(' ')
        

        totalsoma = []
        for n,soma in enumerate(self.soma):            
            if soma == 'len':
                totalsoma.append(pole.util.convert_and_format(len (registros),int,self.casas[n])[1])
            elif soma == 'set':
                totalsoma.append(pole.util.convert_and_format(len(set(zip(*registros)[n])),int,self.casas[n])[1])
            elif soma == 'sum':
                totalsoma.append(pole.util.convert_and_format(sum(zip(*registros)[n]),float,self.casas[n])[1])
            else:
                totalsoma.append('')
        
        #perc
        for n,soma in enumerate(self.soma):            
            if soma[:4] == 'perc':
                p,a,b = soma.split(' ')
                print "GGGGGG",a,"bbbbbbbb",b
                a = pole.util.convert_and_format(totalsoma[int(a)],float)[0]
                b = pole.util.convert_and_format(totalsoma[int(b)],float)[0]
                print "Foir",a,"bbbbbbbb",b
                totalsoma[n] = pole.util.convert_and_format((a/b)*100,float,self.casas[n])[1] 

        dados_tabela.append (linhatotal)
        
        dados_tabela.append (totalsoma)
        t, i, a = pdf.tabela(sum(self.larguras), disponivel_altura, dados_tabela, self.larguras, style=self.ts)

        pdf.celula(sum(self.larguras), a, None, [t], borda = True, espacamento=0)
        dados_tabela = dados_tabela[i:]

        #numeo pagina
        numero_pagina = 1
        total_pagina = 1
        dados_total_pagina = dados_tabela
        
        
        while len(dados_total_pagina):
            disponivel_altura = altura_folha
            altura_table = 0
            disponivel_altura -= altura_cabecalho

            for linha in dados_total_pagina:
                altura_table = max(altura_table,pdf.altura(largura, 1, None, [pole.pdf.Paragraph(cabecalho, pole.pdf.normal_centro)]))
            
            t, i, a = pdf.tabela(sum(self.larguras), disponivel_altura, dados_tabela, self.larguras, style=self.ts)            
            dados_total_pagina = dados_total_pagina[i:]
            total_pagina += 1
        disponivel_altura -= a
        
        pdf.celula(largura_folha, 0.1, None, [pole.pdf.Paragraph("Página: "+str(numero_pagina)+" de "+str(total_pagina),pole.pdf.pequena_direita)], borda = False, posicao=(1 * cm, 0.6 * cm))

        # calcular a altura do sumário + espaço e se não couber em disponivel_altura somar mais uma página
        altura_sumario = 0
        #~ for linha in sumario:
            #~ print "sumariooooooooooooooooooooooooooooooooooooooooooooooo"
            #~ altura_sumario = max(altura_sumario,pdf.altura(largura, sumario[1], None, [pole.pdf.Paragraph(cabecalho, pole.pdf.normal_centro)]))
            #~ print altura_sumario , "dentro"
        #~ print altura_sumario , "Fora"
        #~ 
        
        
        while len(dados_tabela):
            pdf.nova_pagina()
            #numero pagina
            pdf.celula(largura_folha, 0.1, None, [pole.pdf.Paragraph("Página: "+str(numero_pagina+1)+" de "+str(total_pagina),pole.pdf.pequena_direita)], borda = False, posicao=(1 * cm, 0.6 * cm))
            disponivel_altura = altura_folha
            
            altura_table = 0

            for largura, cabecalho in zip(self.larguras, self.cabecalhos):
                #a = max(a,pdf.celula(largura, altura_cabecalho, None, [pole.pdf.Paragraph(cabecalho, pole.pdf.normal_centro)])[3])
                pdf.celula(largura, altura_cabecalho, None, [pole.pdf.Paragraph(cabecalho, pole.pdf.normal_centro)])
            disponivel_altura -= altura_cabecalho

            for linha in dados_tabela:
                altura_table = max(altura_table,pdf.altura(largura, 1, None, [pole.pdf.Paragraph(cabecalho, pole.pdf.normal_centro)]))
            t, i, a = pdf.tabela(sum(self.larguras), disponivel_altura, dados_tabela, self.larguras, style=self.ts)
            pdf.celula(sum(self.larguras), a, None, [t], borda = True, espacamento=0)
            dados_tabela = dados_tabela[i:]
            numero_pagina+=1
        disponivel_altura -= a
        
        # Colocar o sumário quebrando um página se não couber em disponivel_altura
        # SE O SUMARIO É DIFERENTE DE NONE
        if sumario is not None:
            pdf.celula(largura_folha, 1*cm, " ", " ", borda = False)
            for celula in sumario:
                pdf.celula(*celula)
        #pdf.celula(largura_folha, 0.1, None, [pole.pdf.Paragraph("Página: "+str(numero_pagina+1)+" de "+str(total_pagina),pole.pdf.pequena_direita)], borda = True)
            
            
        if finalizar:
            pdf.salvar()
            pdf.mostrar()
        
        #self.jn_principal.hide()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # ##
# Chama a interface GTK para o primeiro plano caso o arquivo esteja sendo
#     executado pelo usuário e não carregado como um módulo
if  __name__ == "__main__":
    projeto = Projeto('', 
                    '01/01/2011',
                    '31/03/2011', 
                    "Relatórios de Recursos Cadastrado", 
                    [1, 1, 3, 3.5, 7, 3, 3, 3, 3], 
                    ['Cod. Recuro','Descrição', 'Valor Hora', 'Valor Hora', 'Valor Hora', 'Valor Hora', 'Valor Hora', 'Valor Hora', 'Valor Hora'], 
                    ['str','str','str','str','str','str','str','str','str'], 
                    [1, 1, 3, 3, 3, 3, 3, 3, 3],
                    ['','set','len','len','len','len','len','len','len'],
                    '',
                    [[[123,123,5465,123465,1,2,3,4,5],['123','123','5465','123465','1','2','3','4','5']],
                     [[123,123,5465,123465,1,2,3,4,5],['123','123','5465','123465','1','2','3','4','5']],
                     [[123,123,5465,123465,1,2,3,4,5],['123','123','5465','123465','1','2','3','4','5']],
                    ],conexao)
    gtk.main()
