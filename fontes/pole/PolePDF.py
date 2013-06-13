#!/bin/env python
#-*- coding: utf-8 -*-

"""PolePDF - Classe PDF em Python que cria um papel e permite adicionar
             células e tabelas encaixando-as ou flutuantes

Arquivo: PolePDF.py
Versão.: 0.1.0
Autor..: Claudio Polegato Junior
Data...: 25 Mar 2011

Copyright © 2011 - Claudio Polegato Junior <junior@juniorpolegato.com.br>
Todos os direitos reservados
"""

import subprocess

from reportlab.lib.pagesizes import A4, legal, landscape
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus.paragraph import Paragraph
from reportlab.platypus import *
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus.flowables import PageBreak
from reportlab.platypus.tables import Table
from reportlab.graphics.barcode.code128 import Code128

extra_grande_centro = ParagraphStyle('normal', fontSize = 18, leading = 18, alignment = TA_CENTER)
grande_centro       = ParagraphStyle('normal', fontSize = 14, leading = 14, alignment = TA_CENTER)
pequena_esquerda    = ParagraphStyle('normal', fontSize = 5, leading = 5, alignment = TA_LEFT)
normal_esquerda     = ParagraphStyle('normal', fontSize = 8, leading = 8, alignment = TA_LEFT)
pequena_centro      = ParagraphStyle('normal', fontSize = 5, leading = 5, alignment = TA_CENTER)
normal_centro       = ParagraphStyle('normal', fontSize = 8, leading = 8, alignment = TA_CENTER)
pequena_direita     = ParagraphStyle('normal', fontSize = 5, leading = 5, alignment = TA_RIGHT)
normal_direita      = ParagraphStyle('normal', fontSize = 8, leading = 8, alignment = TA_RIGHT)
pequena_justa       = ParagraphStyle('normal', fontSize = 5, leading = 5, alignment = TA_JUSTIFY)
normal_justa        = ParagraphStyle('normal', fontSize = 8, leading = 8, alignment = TA_JUSTIFY)
fonte_tab_pequena   = ParagraphStyle('normal', fontSize = 5, leading = 5, alignment = TA_LEFT)
fonte_tab_grande    = ParagraphStyle('normal', fontSize = 8, leading = 8, alignment = TA_LEFT)
minuscula_direita   = ParagraphStyle('normal', fontSize = 4, leading = 4, alignment = TA_RIGHT)

class PDF(object):
    X = 0
    Y = 1
    L = 2
    A = 3
    def __init__(self, titulo = 'Sem Nome',  nome_do_arquivo = '/tmp/teste.pdf', margem = 1 * cm, tamanho_pagina = A4, espacamento = 0.5 * mm, espessura = 0.5, paisagem = False):
        if paisagem:
            tamanho_pagina = landscape(tamanho_pagina)
        self.canvas = Canvas(nome_do_arquivo, pagesize = tamanho_pagina)
        self.canvas.setTitle(titulo)
        self.titulo = titulo
        self.nome_do_arquivo = nome_do_arquivo
        self.retangulos = [[0, 0, self.canvas._pagesize[0] - 2 * margem, self.canvas._pagesize[1] - 2 * margem]]
        self.margem = margem
        self.espacamento = espacamento
        self.erro = 0.001 * mm
        self.espessura = espessura

    def cortar(self, largura, altura, posicao = None):
        retangulo_encontrado = None
        posicao = None # Essa linha deverá ser comentada quando for possível cortar os retângulos vazios, ainda não implementado
        if not posicao:
            for i in range(len(self.retangulos)):
                # Verificar se o retângulo novo cabe num vazio virtual
                if self.retangulos[i][L] >= largura - erro and self.retangulos[i][A] >= altura - erro:
                    posicao = (self.retangulos[i][X], self.retangulos[i][Y])
                    retangulo_encontrado = i
                    break
        if not posicao:
            return None
        x, y = posicao
        erro = self.erro
        # Para cada i índice de retângulos
        #print "\n\nAntes:", self.retangulos
        # Quebrar retângulos vazios quebrados pelo novo inserido
        apagar = []
        for i in range(len(self.retangulos)):
            (xr, yr, lr, ar) = self.retangulos[i]
            # Analisando a aresta esquerda
            if xr - erro <= x <= xr + lr + erro and y + erro <= yr <= y + altura - erro:
                self.retangulos[j][2] = x - xr
                if self.retangulos[j][2] < erro:
                        apagar.append(j)
            if yr - erro <= y <= yr + ar + erro and x + erro <= xr <= x + largura - erro:
                    self.retangulos[j][3] = y - yr
                    if self.retangulos[j][3] < erro:
                        apagar.append(j)
        (x, y, l, a) = self.retangulos[i][retangulo_encontrado]
        #print "Quebr:", self.retangulos
        # Retângulo vazio novo mais alto com o restante da largura e mesma altura
        alto = [x + largura, y, l - largura, a]
        # Retângulo vazio novo mais baixo com o restante da altura e mesma largura
        baixo = [x, y + altura, l, a - altura]
        # Verificando se o mais alto está dentro de algum outro retângulo vazio virtual
        #print "Alto:", alto
        #print "Baixo:", baixo
        if alto[L] < erro:
            inserir_alto = False
        else:
            inserir_alto = True
            for j in range(retangulo_encontrado):
                #print "Analisando:", j, self.retangulos[j], self.retangulos[j][X] <= alto[X] <= self.retangulos[j][X] + self.retangulos[j][L], self.retangulos[j][Y] <= alto[Y] <= self.retangulos[j][Y] + self.retangulos[j][A], self.retangulos[j][X] <= alto[X] + alto[L] <= self.retangulos[j][X] + self.retangulos[j][L], self.retangulos[j][Y], alto[Y] + alto[A], self.retangulos[j][Y] + self.retangulos[j][A]
                if self.retangulos[j][X] - erro <= alto[X] <= self.retangulos[j][X] + self.retangulos[j][L] + erro and \
                   self.retangulos[j][Y] - erro <= alto[Y] <= self.retangulos[j][Y] + self.retangulos[j][A] + erro and \
                   self.retangulos[j][X] - erro <= alto[X] + alto[L] <= self.retangulos[j][X] + self.retangulos[j][L] + erro and \
                   self.retangulos[j][Y] - erro <= alto[Y] + alto[A] <= self.retangulos[j][Y] + self.retangulos[j][A] + erro:
                        inserir_alto = False
                        break
        # Verificando se o mais baixo está dentro de algum outro retângulo vazio virtual
        if baixo[A] < erro:
            inserir_baixo = False
        else:
            inserir_baixo = True
            for j in range(retangulo_encontrado + 1, len(self.retangulos)):
                if self.retangulos[j][X] - erro <= baixo[X] <= self.retangulos[j][X] + self.retangulos[j][L] + erro and \
                   self.retangulos[j][Y] - erro <= baixo[Y] <= self.retangulos[j][Y] + self.retangulos[j][A] + erro and \
                   self.retangulos[j][X] - erro <= baixo[X] + baixo[L] <= self.retangulos[j][X] + self.retangulos[j][L] + erro and \
                   self.retangulos[j][Y] - erro <= baixo[Y] + baixo[A] <= self.retangulos[j][Y] + self.retangulos[j][A] + erro:
                        inserir_baixo = False
                        break
        # Eliminar retângulo usado
        del self.retangulos[retangulo_encontrado]
        # Inserir o retângulo mais alto antes do que está sendo usado
        if inserir_alto:
            self.retangulos.insert(retangulo_encontrado, alto)
        if inserir_baixo:
            # Inserir o retângulo mais baixo na posição correta, levando-se em conta o Y e depois o X
            inserido_baixo = False
            for j in range(retangulo_encontrado, len(self.retangulos)):
                if self.retangulos[j][Y] >= baixo[Y]:
                    if self.retangulos[j][Y] > baixo[Y]:
                        self.retangulos.insert(j, baixo)
                        inserido_baixo = True
                        break
                    else:
                        for k in range(j, len(self.retangulos)):
                            if self.retangulos[j][X] > baixo[X] or self.retangulos[j][Y] > baixo[Y]:
                                self.retangulos.insert(k, baixo)
                                inserido_baixo = True
                                break
            if not inserido_baixo:
                self.retangulos.append(baixo)
        # Apagar retângulos com altura ou largura zerados
        for i in list(set(apagar))[::-1]:
            del self.retangulos[i]
        # retorna o ponto de inserção
        #print "Retangulos depois:", self.retangulos
        return (x + self.margem, self.canvas._pagesize[Y] - self.margem - y)

    def ponto_insercao(self, largura, altura, posicao = None):
        erro = self.erro
        # Para cada i índice de retângulos
        #print "\n\nAntes:", self.retangulos
        for i in range(len(self.retangulos)):
            # Verificar se o retângulo novo cabe num vazio virtual
            if self.retangulos[i][2] >= largura - erro and self.retangulos[i][3] >= altura - erro:
                # Posição para inserir o novo retângulo
                retorno = (self.retangulos[i][0] + self.margem, self.canvas._pagesize[1] - self.margem - self.retangulos[i][1])
                # Quebrar retângulos vazios quebrados pelo novo inserido
                apagar = []
                for j in range(len(self.retangulos)):
                    if self.retangulos[j][0] - erro <= self.retangulos[i][0] <= self.retangulos[j][0] + self.retangulos[j][2] + erro and \
                       self.retangulos[i][1] + erro <= self.retangulos[j][1] <= self.retangulos[i][1] + altura - erro:
                            self.retangulos[j][2] = self.retangulos[i][0] - self.retangulos[j][0]
                            if self.retangulos[j][2] < erro:
                                apagar.append(j)
                    if self.retangulos[j][1] - erro <= self.retangulos[i][1] <= self.retangulos[j][1] + self.retangulos[j][3] + erro and \
                       self.retangulos[i][0] + erro <= self.retangulos[j][0] <= self.retangulos[i][0] + largura - erro:
                            self.retangulos[j][3] = self.retangulos[i][1] - self.retangulos[j][1]
                            if self.retangulos[j][3] < erro:
                                apagar.append(j)
                #print "Quebr:", self.retangulos
                # Retângulo novo mais alto com o restante da largura e mesma altura
                alto = [self.retangulos[i][0] + largura, self.retangulos[i][1], self.retangulos[i][2] - largura, self.retangulos[i][3]]
                # Retângulo novo mais baixo com o restante da altura e mesma largura
                baixo = [self.retangulos[i][0], self.retangulos[i][1] + altura, self.retangulos[i][2], self.retangulos[i][3] - altura]
                # Verificando se o mais alto está dentro de algum outro retângulo vazio virtual
                #print "Alto:", alto
                #print "Baixo:", baixo
                if alto[2] < erro:
                    inserir_alto = False
                else:
                    inserir_alto = True
                    for j in range(i):
                        #print "Analisando:", j, self.retangulos[j], self.retangulos[j][0] <= alto[0] <= self.retangulos[j][0] + self.retangulos[j][2], self.retangulos[j][1] <= alto[1] <= self.retangulos[j][1] + self.retangulos[j][3], self.retangulos[j][0] <= alto[0] + alto[2] <= self.retangulos[j][0] + self.retangulos[j][2], self.retangulos[j][1], alto[1] + alto[3], self.retangulos[j][1] + self.retangulos[j][3]
                        if self.retangulos[j][0] - erro <= alto[0] <= self.retangulos[j][0] + self.retangulos[j][2] + erro and \
                           self.retangulos[j][1] - erro <= alto[1] <= self.retangulos[j][1] + self.retangulos[j][3] + erro and \
                           self.retangulos[j][0] - erro <= alto[0] + alto[2] <= self.retangulos[j][0] + self.retangulos[j][2] + erro and \
                           self.retangulos[j][1] - erro <= alto[1] + alto[3] <= self.retangulos[j][1] + self.retangulos[j][3] + erro:
                                inserir_alto = False
                                break
                # Verificando se o mais baixo está dentro de algum outro retângulo vazio virtual
                if baixo[3] < erro:
                    inserir_baixo = False
                else:
                    inserir_baixo = True
                    for j in range(i + 1, len(self.retangulos)):
                        if self.retangulos[j][0] - erro <= baixo[0] <= self.retangulos[j][0] + self.retangulos[j][2] + erro and \
                           self.retangulos[j][1] - erro <= baixo[1] <= self.retangulos[j][1] + self.retangulos[j][3] + erro and \
                           self.retangulos[j][0] - erro <= baixo[0] + baixo[2] <= self.retangulos[j][0] + self.retangulos[j][2] + erro and \
                           self.retangulos[j][1] - erro <= baixo[1] + baixo[3] <= self.retangulos[j][1] + self.retangulos[j][3] + erro:
                                inserir_baixo = False
                                break
                # Eliminar retângulo usado
                del self.retangulos[i]
                # Inserir o retângulo mais alto antes do que está sendo usado
                if inserir_alto:
                    self.retangulos.insert(i, alto)
                if inserir_baixo:
                    # Inserir o retângulo mais baixo na posição correta, levando-se em conta o Y e depois o X
                    inserido_baixo = False
                    for j in range(i, len(self.retangulos)):
                        if self.retangulos[j][1] >= baixo[1]:
                            if self.retangulos[j][1] > baixo[1]:
                                self.retangulos.insert(j, baixo)
                                inserido_baixo = True
                                break
                            else:
                                for k in range(j, len(self.retangulos)):
                                    if self.retangulos[j][0] > baixo[0] or self.retangulos[j][1] > baixo[1]:
                                        self.retangulos.insert(k, baixo)
                                        inserido_baixo = True
                                        break
                    if not inserido_baixo:
                        self.retangulos.append(baixo)
                # Apagar retângulos com altura ou largura zerados
                for i in list(set(apagar))[::-1]:
                    del self.retangulos[i]
                # retorna o ponto de inserção
                #print "Retangulos depois:", self.retangulos
                return retorno
        return None

    def tabela(self, largura, altura, dados, colWidths=None, rowHeights=None, style=None, repeatRows=0, repeatCols=0, splitByRow=1, emptyTableAction=None, ident=None, hAlign=None, vAlign=None):
        # Renderizar 1 linha
        tabela = Table(dados[:1], colWidths, rowHeights, style, repeatRows, repeatCols, splitByRow, emptyTableAction, ident, hAlign, vAlign)
        l, a = tabela.wrapOn(self.canvas, largura, altura)
        # Quantas linhas dessa altura cabem
        linhas = int(altura/a)
        # Renderizar linhas
        tabela = Table(dados[:linhas], colWidths, rowHeights, style, repeatRows, repeatCols, splitByRow, emptyTableAction, ident, hAlign, vAlign)
        l, a = tabela.wrapOn(self.canvas, largura, altura)
        # Se não couber, vou tirando de 1 em 1
        if a > altura:
            for i in range(linhas, 0, -1):
                tabela = Table(dados[:i], colWidths, rowHeights, style, repeatRows, repeatCols, splitByRow, emptyTableAction, ident, hAlign, vAlign)
                l, a = tabela.wrapOn(self.canvas, largura, altura)
                if a <= altura:
                    break
            return (tabela, i, a)
        # Se couber, vou colocando de 1 em 1
        i = linhas
        for i in range(linhas, len(dados)):
            tabela = Table(dados[:i], colWidths, rowHeights, style, repeatRows, repeatCols, splitByRow, emptyTableAction, ident, hAlign, vAlign)
            l, a = tabela.wrapOn(self.canvas, largura, altura)
            if a > altura:
                break
        i -= 1
        tabela = Table(dados[:i], colWidths, rowHeights, style, repeatRows, repeatCols, splitByRow, emptyTableAction, ident, hAlign, vAlign)
        l, a = tabela.wrapOn(self.canvas, largura, altura)
        return (tabela, i, a)

    def celula(self, largura, altura, titulo, dados, borda = True, arredondamento = 0.5 * mm, ajuste_inferior = 0 * mm, espacamento = None, posicao = None, espessura = None, alinhamento = 'justa', multilinha = None):
        if espessura == None:
            espessura = self.espessura
        if espacamento == None:
            espacamento = self.espacamento * 2
            #if titulo is None:
            #    tipos = [type(x) for x in dados]
            #    if not (str in tipos or unicode in tipos or Paragraph in tipos):
            #        espacamento = 0
        else:
            espacamento *= 2
        if alinhamento.lower() == 'esquerda':
            estilo = normal_esquerda
        elif alinhamento.lower() == 'direita':
            estilo = normal_direita
        elif alinhamento.lower() == 'centro':
            estilo = normal_centro
        else:
            estilo = normal_justa
        if titulo == '':
            componentes = (Paragraph(dados, estilo),)
        elif titulo:
            componentes = (Paragraph(titulo, pequena_esquerda), Paragraph(dados, estilo))
        else:
            componentes = dados
        altura_total = 0
        altura_texto = altura - espacamento + ajuste_inferior
        largura_texto = largura - espacamento
        renderizados = []
        if not multilinha and titulo and dados != '&nbsp;':
            componentes[1].wrapOn(self.canvas, largura_texto, altura_texto)
            linhas = componentes[1].breakLines(largura_texto).lines
            if len(linhas) > 0:
                if isinstance(linhas[0], tuple): # texto comum
                    componentes = (componentes[0], Paragraph(' '.join(linhas[0][1]), estilo))
                else: # texto com formatação
                    componentes = (componentes[0], Paragraph(''.join([linhas[0].words[i].text for i in range(len(linhas[0].words))]), estilo))
        for componente in componentes:
            larg, alt = componente.wrapOn(self.canvas, largura_texto, altura_texto)
            altura_total += alt
            altura_texto -= alt
            renderizados.append((altura_total, componente, larg))
        altura_total -= ajuste_inferior
        if altura_total < altura - espacamento:
            altura_total = altura - espacamento
        if posicao:
            x, y = posicao
            y = self.canvas._pagesize[1] - y
        else:
            pi = self.ponto_insercao(largura, altura_total + espacamento)
            if pi:
                x, y = pi
            else:
                print ('Um objeto de %i cm x %i cm não coube na página do PDF "%s" e será apresentado'
                       'no canto inferior direito desta página' % (largura / cm, altura_total / cm, self.titulo))
                x = self.canvas._pagesize[0] - largura - espessura / 2
                y = altura_total + espacamento + espessura / 2
        #print "Posição:", x/mm, y/mm
        for renderizado in renderizados:
            self.canvas.setLineWidth(espessura)
            #renderizado[1].drawOn(self.canvas, x + espacamento / 2, y - renderizado[0] - espacamento / 2)
            renderizado[1].drawOn(self.canvas, x + (largura - renderizado[2]) / 2, y - renderizado[0] - espacamento / 2)
        if borda:
            self.canvas.roundRect(x, y - altura_total - espacamento, largura, altura_total + espacamento, arredondamento)
        return (x, y, largura, altura_total + espacamento)

    def altura(self, largura, altura, titulo, dados, borda = True, arredondamento = 0.5 * mm, ajuste_inferior = 0 * mm, espacamento = None, posicao = None, espessura = None, alinhamento = 'justa', multilinha = None):
        if espessura == None:
            espessura = self.espessura
        if not espacamento:
            espacamento = self.espacamento * 2
        else:
            espacamento *= 2
        if alinhamento.lower() == 'esquerda':
            estilo = normal_esquerda
        elif alinhamento.lower() == 'direita':
            estilo = normal_direita
        elif alinhamento.lower() == 'centro':
            estilo = normal_centro
        else:
            estilo = normal_justa
        if titulo == '':
            componentes = (Paragraph(dados, estilo),)
        elif titulo:
            componentes = (Paragraph(titulo, pequena_esquerda), Paragraph(dados, estilo))
        else:
            componentes = dados
        altura_total = 0
        altura_texto = altura - espacamento + ajuste_inferior
        largura_texto = largura - espacamento
        renderizados = []
        if not multilinha and titulo and dados != '&nbsp;':
            componentes[1].wrapOn(self.canvas, largura_texto, altura_texto)
            linhas = componentes[1].breakLines(largura_texto).lines
            if len(linhas) > 0:
                if isinstance(linhas[0], tuple): # texto comum
                    componentes = (componentes[0], Paragraph(' '.join(linhas[0][1]), estilo))
                else: # texto com formatação
                    componentes = (componentes[0], Paragraph(''.join([linhas[0].words[i].text for i in range(len(linhas[0].words))]), estilo))
        for componente in componentes:
            larg, alt = componente.wrapOn(self.canvas, largura_texto, altura_texto)
            altura_total += alt
            altura_texto -= alt
            renderizados.append((altura_total, componente, larg))
        altura_total -= ajuste_inferior
        if altura_total < altura - espacamento:
            altura_total = altura - espacamento
        return altura_total + espacamento

    def salvar(self):
        self.canvas.save()

    def mostrar(self, programa = 'evince'):
        self.canvas.save()
        subprocess.Popen([programa, self.nome_do_arquivo])

    def nova_pagina(self):
        self.canvas.showPage()
        self.retangulos = [(0, 0, self.canvas._pagesize[0] - 2 * self.margem, self.canvas._pagesize[1] - 2 * self.margem)]
