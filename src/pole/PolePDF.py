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
from reportlab.platypus import Image
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus.tables import Table
from reportlab.graphics.barcode import getCodeNames as BarCodeNames
from reportlab.graphics.barcode import createBarcodeDrawing as BarCode
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

X = 0
Y = 1
L = 2
A = 3
ALTO = 0
BAIXO = 1

# ' ' = '\xc2\xa0' = nbsp em utf-8

XML_ESCAPE = (('lt', '<'), ('gt', '>'), ('amp', '&'),
              ('quot', '"'), ('nbsp', ' '))

FORM_ESCAPE = (('<b>', '\0b\0'), ('</b>', '\0/b\0'),
               ('<i>', '\0i\0'), ('</i>', '\0/i\0'),
               ('<br/>', '\n'),
               ('&nbsp; ', '  '), (' &nbsp;', '  '))

def escape(text):
    if not text:
        return text
    if text == ' ':
        return '&nbsp;'
    for f, x in FORM_ESCAPE:
        text = text.replace(f, x)
    for e, c in XML_ESCAPE:
        if c == ' ' and isinstance(text, unicode):
            c = u' '
        text = text.replace(c, '&%s;' % e)
    for f, x in FORM_ESCAPE:
        text = text.replace(x, f)
    return text

def unescape(text):
    if not text:
        return text
    for f, x in FORM_ESCAPE:
        text = text.replace(x, f)
    for e, c in XML_ESCAPE:
        text = text.replace('&%s;' % e, c)
    for f, x in FORM_ESCAPE:
        text = text.replace(f, x)
    return text

def paragrafo(texto, estilo):
    return Paragraph(escape(texto), estilo)

class PDF(object):
    def __init__(self, titulo = 'Sem Nome',  nome_do_arquivo = '/tmp/pole.pdf',
                 margem = 1 * cm, tamanho_pagina = A4, espacamento = 0.5 * mm,
                 espessura = 0.5, paisagem = False):
        if paisagem:
            tamanho_pagina = landscape(tamanho_pagina)
        self.canvas = Canvas(nome_do_arquivo, pagesize = tamanho_pagina)
        self.canvas.setTitle(titulo)
        self.titulo = titulo
        self.nome_do_arquivo = nome_do_arquivo
        self.retangulos = [[0, 0,
                            self.canvas._pagesize[0] - 2 * margem,
                            self.canvas._pagesize[1] - 2 * margem]]
        self.margem = margem
        self.espacamento = espacamento
        self.erro = 0.001 * mm
        self.espessura = espessura

    def _print_retangulos(self, retangulos = None):
        for retangulo in retangulos or self.retangulos:
            print ["%0.2f" % (x / cm) for x in retangulo]

    def entre(self, pi, p, pf):
        return (pi - self.erro < p < pf + self.erro)

    def x_entre(self, x, retangulo):
        r = retangulo
        return (r[X] - self.erro < x < r[X] + r[L] + self.erro)

    def y_entre(self, y, retangulo):
        r = retangulo
        return (r[Y] - self.erro < y < r[Y] + r[A] + self.erro)

    def igual(self, p1, p2):
        return (abs(p1 - p2) < self.erro)

    def retangulo_dentro(self, retangulo_menor, retangulo_maior):
        e = self.erro
        Xv, Yv, Lv, Av = retangulo_maior
        Xn, Yn, Ln, An = retangulo_menor
        return (Xv - e < Xn < Xv + Lv + e and
                Xv - e < Xn + Ln < Xv + Lv + e and
                Yv - e < Yn < Yv + Av + e and
                Yv - e < Yn + An < Yv + Av + e)

    def ponto_dentro(self, ponto, retangulo):
        e = self.erro
        Xp, Yp = ponto
        Xr, Yr, Lr, Ar = retangulo
        return (Xr - e < Xp < Xr + Lr + e and
                Yr - e < Yp < Yr + Ar + e)

    def cabe(self, retangulo, largura, altura):
        return (retangulo[L] > largura - self.erro and
                retangulo[A] > altura - self.erro)

    def ampliar(self, qual, retangulo):
        i = +(qual == ALTO) # X se baixo | Y se alto
        j = L + i           # L se baixo | A se alto
        #if retangulo[L + (qual == BAIXO)] < self.erro:
        #    return
        for r in self.retangulos:
            if self.ponto_dentro(retangulo[:2], r):
                retangulo[j] += retangulo[i] - r[i]
                retangulo[i] = r[i]
            if qual == BAIXO and self.ponto_dentro([retangulo[X] +
                                                    retangulo[L],
                                                    retangulo[Y]], r):
                retangulo[L] += r[X] + r[L] - (retangulo[X] + retangulo[L])

    def ponto_insercao(self, largura, altura):
        erro = self.erro
        #~ print '^' * 100
        #~ print 'Requerido:', largura / cm, altura / cm
        #~ print "Retângulos disponíveis"
        #~ self._print_retangulos()
        # Verificar se o retângulo requerido cabe num outro vazio
        coube = False
        for retangulo in self.retangulos:
            coube = self.cabe(retangulo, largura, altura)
            if coube:
                break
        # Se não coube em nenhum vazio, retorna None
        if not coube:
            #~ print "Não coube!"
            return None
        # Retirar o retângulo vazio da lista de disponíveis
        self.retangulos.remove(retangulo)
        # Posição para inserir o novo retângulo
        requerido = retangulo[X], retangulo[Y], largura, altura
        x, y, l, a = requerido
        retorno = (x + self.margem, self.canvas._pagesize[Y] - self.margem - y)
        # Reduzir retângulos disponíveis cruzados pelo requerido e inserir novos restantes
        restantes = []
        for r in self.retangulos:
            if r[Y] > y + altura + self.erro:
                break
            if self.x_entre(x, r) and self.y_entre(r[Y], requerido):
                #~ print 'restante',
                #~ self._print_retangulos([r])
                restantes.append([x + l, r[Y], r[X] + r[L] - (x + l), r[A]])
                r[L] = x - r[X]
            if self.y_entre(y, r) and self.x_entre(r[X], requerido):
                r[A] = y - r[Y]
        self.retangulos += restantes
        #~ print "Quebrados"
        #~ self._print_retangulos()
        # Inserir os dois novos retângulos resultantes do removido
        # Retângulo novo mais alto com o restante da largura e mesma altura
        novo = [x + l, y, retangulo[L] - l, retangulo[A]]
        #~ print "Alto:",
        #~ self._print_retangulos([novo])
        self.ampliar(ALTO, novo)
        #~ print "Alto ampliado:",
        #~ self._print_retangulos([novo])
        self.retangulos.append(novo)
        # Retângulo novo mais baixo com o restante da altura e mesma largura
        novo = [x, y + a, retangulo[L], retangulo[A] - a]
        #~ print "Baixo:",
        #~ self._print_retangulos([novo])
        self.ampliar(BAIXO, novo)
        #~ print "Baixo ampliado:",
        #~ self._print_retangulos([novo])
        self.retangulos.append(novo)
        # Apagar retângulos com altura ou largura zerados
        zeros = [r for r in self.retangulos if r[A] < erro or r[L] < erro]
        #~ print "Zerados"
        #~ self._print_retangulos(zeros)
        for zero in zeros:
            self.retangulos.remove(zero)
        #~ print "Limpo"
        #~ self._print_retangulos()
        # Apagar retângulos disponíveis que estejam dentro de outros
        dentros = []
        for r1 in self.retangulos:
            for r2 in self.retangulos:
                if r1 == r2:
                    continue
                if self.retangulo_dentro(r1, r2):
                    dentros.append(r1)
                    break
        #~ print "Dentros"
        #~ self._print_retangulos(zeros)
        for dentro in dentros:
            self.retangulos.remove(dentro)
        #~ print "Limpo"
        #~ self._print_retangulos()
        # Reordenar retângulos disponíveis por Y, X
        self.retangulos = sorted(self.retangulos, key=lambda x: [x[1], x[0]])

        # retorna o ponto de inserção
        #~ print "Retangulos depois"
        #~ self._print_retangulos()
        return retorno

    def tabela(self, largura, altura, dados, colWidths=None, rowHeights=None, style=None, repeatRows=0, repeatCols=0, splitByRow=1, emptyTableAction=None, ident=None, hAlign=None, vAlign=None):
        # Escape dados str ou unicode
        dados = [[escape(d) if isinstance(d, (str, unicode)) else d for d in l] for l in dados]
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
            componentes = (paragrafo(dados, estilo),)
        elif titulo:
            componentes = (paragrafo(titulo, pequena_esquerda), paragrafo(dados, estilo))
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
                    componentes = (componentes[0], paragrafo(' '.join(linhas[0][1]), estilo))
                else: # texto com formatação
                    componentes = (componentes[0], paragrafo(''.join(w.text for w in linhas[0].words), estilo))
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

    def tamanho(self, componente, largura_maxima):
        return componente.wrapOn(self.canvas, largura_maxima, 1)

    def salvar(self):
        self.canvas.save()

    def mostrar(self, programa = 'xdg-open'):
        self.canvas.save()
        subprocess.Popen([programa, self.nome_do_arquivo])

    def nova_pagina(self):
        self.canvas.showPage()
        self.retangulos = [(0, 0, self.canvas._pagesize[0] - 2 * self.margem, self.canvas._pagesize[1] - 2 * self.margem)]

if __name__ == "__main__":
    import cStringIO, base64
    LOGO_PYTHON = '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'
    logo = cStringIO.StringIO()
    logo.write(base64.b64decode(LOGO_PYTHON))
    logo.seek(0)
    # Criar instância do PDF
    pdf = PDF()
    componente = Paragraph('Junior&nbsp;Polegato', normal_direita)
    l, a = pdf.tamanho(componente, 1)
    l += 2 * pdf.espacamento
    a += 2 * pdf.espacamento + .3 * a
    pdf.celula( l, a, None, [componente], posicao = (20 * cm - l, 28.7 * cm - a), borda= True)
    pdf.celula( 5 * cm, 1 * cm, 'Teste', '1')
    pdf.celula(15 * cm, 2 * cm, 'Teste', '2')
    pdf.celula( 4 * cm, 5 * cm, 'Teste', '3')
    pdf.celula(10 * cm, 1 * cm, 'Teste', '4')
    pdf.celula( 5 * cm, 5 * cm, 'Teste', '5')
    pdf.celula( 4 * cm, 3 * cm, 'Teste', '6')
    pdf.celula( 7 * cm, 1 * cm, 'Teste', '7')

    # Renderiza uma imagem
    img = Image(logo)
    largura = 5 * cm   # redimensionar imagem para 5 cm de largura
    img.drawHeight = largura * img.drawHeight / img.drawWidth
    img.drawWidth = largura
    pdf.celula(largura, 1, None, [img])
    # Renderiza uma célula texto com título e outra sem título
    pdf.celula(10 * cm, 1, 'Título da célula', 'Texto de conteúdo da célula')
    pdf.celula(10 * cm, 1, '', 'Texto de conteúdo da célula sem título')
    # Renderiza uma tabela simples
    estilo = [('GRID', (0,0), (-1,-1),0.5, colors.black),
              ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
              ('TOPPADDING', (0,0), (-1,-1), 0),
              ('RIGHTPADDING', (0,0), (-1,-1), 1*mm),
              ('LEFTPADDING', (0,0), (-1,-1), 1*mm),
              ('FONTSIZE', (0,0), (-1,-1), normal_centro.fontSize),
              ('LEADING', (0,0), (-1,-1), normal_centro.leading),
              ('BOTTOMPADDING', (0,0), (-1,-1), 1)]
    dados = [[123, 'Hora 1', 5465, 123465, 1, 2, 3, 4, True] ,
             [123, 'Hora 2', 5465, 123465, 1, 2, 3, 4, False],
             [123, 'Hora 3', 5465, 123465, 1, 2, 3, 100, True] ,
             [123, 'Hora 4', 5465, 123465, 1, 2, 3, 4, True]] * 25
    tab, i, h = pdf.tabela(19 * cm, 3 * cm, dados, style = estilo) # Não renderiza
    w = sum(tab._colWidths) + 0.5 * cm
    pdf.celula(w, h, None, [Paragraph('Tabela', pequena_esquerda), tab, Paragraph('&nbsp;', pequena_esquerda)])
    # Renderizar códigos de barras
    for code_name in BarCodeNames():
        if code_name == 'FIM':
            value = 'C'
        elif code_name == 'POSTNET':
            value = '123456789'
        elif code_name == 'USPS_4State':
            value = '01234567094987654321'
        elif code_name == 'QR':
            value = 'Junior Polegato - Utilização do PolePDF para geração fácil de PDF de uso diário.'
        else:
            value = '7899041283458'
        bar = BarCode(code_name, value = value)
        pdf.celula(9 * cm, 1, None, [Paragraph(code_name, pequena_esquerda), bar])
    pdf.celula(1 * cm, 2 * cm, 'Onde estou', 'Fim')
    pdf.mostrar()
