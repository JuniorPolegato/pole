#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Imports
import locale
import os.path
import hashlib
import PoleLog
import string
import re
import math
import smtplib
import datetime
import unicodedata
import mimetypes
import base64
import sys
from decimal import Decimal, ROUND_DOWN
from collections import OrderedDict, namedtuple
from dateutil.relativedelta import relativedelta
from dateutil.rrule import MONTHLY, rrule, WEEKLY

"""PoleUtil - Conjunto de funções úteis em Python de uso frequente

Arquivo: PoleUtil.py
Versão.: 1.0.0
Autor..: Claudio Polegato Junior
Data...: 15 Mar 2016

Copyright © 2011 - Claudio Polegato Junior <junior@juniorpolegato.com.br>
Todos os direitos reservados
"""

r"""\package PoleUtil
\brief Conjunto de funções úteis para auxiliar na geração da NFe.

Este pacote imcorpora funções para auxiliar na geração de NFe's, bem
como poder ser utilizados para outros fins.
Inclui-se aqui funções para validar e formatar CPF, CNPJ, RG e
Inscrição Estadual, além de cálculo para módulo variável, como módulo
11, 10 e 9, extração de dígitos, com ou sem símbolo decimal, de uma
lista de caracteres, formatar números inteiro e real com os símbolos
decimal e agrupamento, bem como tranformar números formatados em inteiro
e real.
"""


APP_NAME = 'pole'
VER = (1, 0, 0)

language, encode = (locale.setlocale(locale.LC_ALL, '') + '..').split('.')[:2]
local = locale.localeconv()

try:
    _ = locale.gettext
except Exception:
    try:
        import gettext
        _ = gettext.gettext
    except Exception:
        _ = str

p = sys.prefix
s = os.path.sep
locale_dir_levels = [[], ['..'], ['..', '..'], ['..', '..', '..']]
locale_dir_names = [['po'], ['pole', 'po']]
locale_dirs = [loc + n for loc in locale_dir_levels for n in locale_dir_names]
locale_dirs += [[p], [p, 'share'], [p, 'local'], [p, 'local', 'share'],
                [p, 'usr'], [p, 'usr', 'share'], [p, 'usr', 'local'],
                [p, 'usr', 'local', 'share'],
                [s, 'usr'], [s, 'usr', 'share'], [s, 'usr', 'local'],
                [s, 'usr', 'local', 'share']]
locale_dirs = [os.path.join(*(d + ['locale'])) for d in locale_dirs]

for locale_dir in locale_dirs:
    if os.path.exists(os.path.join(locale_dir, language,
                      'LC_MESSAGES', APP_NAME + '.mo')):
        locale.bindtextdomain(APP_NAME, locale_dir)
        locale.textdomain(APP_NAME)
        break


def digits(string, zero_when_empty=True):
    r"""\brief Extrai apenas os dígitos de uma lista de \a caracteres.

    Função que retorna apenas os dígitos de uma lista de \a carateres
    fornecidos, fazendo uso de expressão regulares para tanto. Caso
    \a zero_se_vazio_ou_nulo seja \c True, retorna '0' se
    \a caracteres for \c None ou \c '', sendo que for \c False, retorna
    o próprio \a caracteres.

    \param caracteres               [\c str/int]    Caracteres dos quais
                                                    serão extraídos os
                                                    dígitos.
    \param zero_se_vazio_ou_nulo    [\c bool]       Se \a carecters for
                                                    \c None ou \c '',
                                                    retorna zero se
                                                    \c True ou
                                                    \c caracteres se
                                                    \c False.
    \return                         [\c str]        Dígitos contidos na
                                                    lista de
                                                    \a caracters
                                                    fornecidos.
    """
    res = re.sub('[^0-9]', '', str(string))
    if not res and zero_when_empty:
        return '0'
    return res


somente_digitos = digits


def somente_digitos_e_decimal(caracteres,
                              zero_se_vazio_ou_nulo=True, casas=None):
    r"""\brief Extrai apenas os dígitos e o primeiro separador de decimal
    de uma lista de \a caracteres.

    Função que retorna apenas os dígitos de uma lista de \a carateres
    fornecidos, fazendo uso da função somente_digitos. Caso
    \a zero_se_vazio_ou_nulo seja \c True, retorna '0D0' se
    \a caracteres for \c None ou \c '', onde D é o símbolo decimal
    atual.Caso \a zero_se_vazio_ou_nulo seja \c False, retorna o próprio
    \a caracteres se \a caracteres for \c None ou \c ''.

    \param caracteres               [\c str/int]    Caracteres dos quais
                                                    serão extraídos os
                                                    dígitos.
    \param zero_se_vazio_ou_nulo    [\c bool]       Se \a carecters for
                                                    \c None ou \c '',
                                                    retorna zero se
                                                    \c True ou
                                                    \c caracteres se
                                                    \c False.
    \return                         [\c str]        Dígitos e símbolo
                                                    decimal contidos na
                                                    lista de
                                                    \a caracters
                                                    fornecidos.
    """
    if isinstance(caracteres, (float, int)):
        return locale.str(caracteres)
    if not isinstance(caracteres, (str, unicode, type(None))):
        caracteres = str(caracteres)
    decimal = locale.localeconv()['decimal_point']
    if caracteres:
        caracteres = re.sub('[^0-9%s]' % decimal, '', caracteres)
    if casas is None:
        casas = locale.localeconv()['frac_digits']
    if not caracteres:
        if zero_se_vazio_ou_nulo:
            return '0' + decimal + '0' * casas
        return caracteres
    caracteres = [re.sub('[^0-9]', '', t)
                  for t in caracteres.split(decimal, 1)]
    caracteres.append('')  # sentinel
    return "%s%s%s" % (caracteres[0] or '0', decimal,
                       (caracteres[1] + '0' * casas)[:casas])


def inteiro(caracteres, arredondamento=0, zero_se_vazio_ou_nulo=True):
    r"""\brief Transforma uma lista de carecteres, geralmente um inteiro
              ou real formatado, em um inteiro.
    \param caracteres       [\c str/int/float]  caracteres ou número a
                                                ser transformado em
                                                inteiro.
    \param arredondamento   [\c int]            Tipo de arredondamento:
                                                negativo => para baixo;
                                                zero => arredondamento
                                                4/5;
                                                positivo => para cima.
    \return                 [\c int]            Inteiro representado por
                                                \a caracteres
    """
    return int(real(caracteres, 0, arredondamento, zero_se_vazio_ou_nulo))


def real(caracteres, casas=2, arrendodamento=0, zero_se_vazio_ou_nulo=True):
    r"""\brief Transforma uma lista de carecteres, geralmente um inteiro
              ou real formatado, em um número real.
    \param caracteres       [\c str/int/float]  caracteres ou número a
                                                ser transformado em
                                                inteiro.
    \param casas            [c\ int]            Casas decimais
                                                significativas onde será
                                                aplicado arredondamento.
    \param arredondamento   [\c int]            Tipo de arredondamento:
                                                negativo => para baixo;
                                                zero => arredondamento
                                                4/5;
                                                positivo => para cima.
    \return                 [\c float]          Real representado por
                                                \a caracteres
    """
    numero = locale.atof(
        somente_digitos_e_decimal(caracteres, zero_se_vazio_ou_nulo, casas))
    mult_casas = 10.0 ** casas
    if arrendodamento < 0:
        return math.floor(numero * mult_casas) / (mult_casas)
    if arrendodamento == 0:
        return round(numero, casas)
    return math.ceil(numero * mult_casas) / (mult_casas)


def formatar_inteiro(caracteres, tamanho=0, preenchimento='',
                     arredondamento=0, zero_se_vazio_ou_nulo=True):
    r"""\brief Formata um inteiro de acordo com as regras de agrupamento
              da localização atual.
    \param caracteres       [\c str/int/float]  Caracteres ou número a
                                                ser formatado em
                                                inteiro.
    \param tamanho          [\c int]            Tamanho mínimo do campo
                                                retornado.
    \param preenchimento    [\c str]            Preencimento do campo
                                                retornado, podendo ser
                                                '0' ou ''.
    \param arredondamento   [\c int]            Tipo de arredondamento:
                                                negativo => para baixo;
                                                zero => arredondamento
                                                4/5;
                                                positivo => para cima.
    \param zero_se_vazio_ou_nulo    [\c bool]   Se \a carecters for
                                                \c None ou \c '',
                                                retorna zero se \c True
                                                ou \c caracteres se
                                                \c False.
    \return                         [\c str]    Caracteres representando
                                                o número real formatado
                                                nas regras de
                                                agrupamento e separador
                                                decimal da localização
                                                atual, de acordo com os
                                                parâmetros passados.
    """
    mascara = '%%%s%dd' % (preenchimento, tamanho)
    return locale.format(mascara, inteiro(caracteres, arredondamento,
                                          zero_se_vazio_ou_nulo), True,
                         not len(locale.localeconv()['grouping']))


def formatar_real(caracteres, casas=2, tamanho=0,
                  preenchimento='', arredondamento=0, moeda=False,
                  moeda_internacional=False, moeda_lateral=True,
                  zero_se_vazio_ou_nulo=True):
    r"""\brief Formata um númer rela de acordo com as regras de
              agrupamento da localização atual.
    \param caracteres       [\c str/int/float]  Caracteres ou número a
                                                ser formatado em real.
    \param casas            [c\ int]            Casas decimais
                                                significativas onde será
                                                aplicado arredondamento.
    \param tamanho          [\c int]            Tamanho mínimo do campo
                                                retornado.
    \param preenchimento    [\c str]            Preencimento do campo
                                                retornado, podendo ser
                                                '0' ou ''.
    \param arredondamento   [\c int]            Tipo de arredondamento:
                                                negativo => para baixo;
                                                zero => arredondamento
                                                4/5;
                                                positivo => para cima.
    \param moeda            [\c bool]           Se coloca ou não o
                                                símbolo de moeda
                                                corrente.
    \param moeda_internacional  [\c bool]       Se coloca ou não o
                                                símbolo de moeda
                                                internacional corrente.
    \param moeda_lateral    [\c bool]           Se o símbolo de moeda
                                                fica alinhado mais à
                                                borda, dependendo do
                                                \a tamanho passado. Caso
                                                \c False ou o \a tamanho
                                                passado menor que a
                                                quantidade de
                                                caracteres, a moeda
                                                ficará junto ao número
                                                respeitando a
                                                configuração local.
    \param zero_se_vazio_ou_nulo    [\c bool]   Se \a carecters for
                                                \c None ou \c '',
                                                retorna zero se \c True
                                                ou \c caracteres se
                                                \c False.
    \return                         [\c str]    Caracteres representando
                                                o número real formatado
                                                nas regras de
                                                agrupamento e separador
                                                decimal da localização
                                                atual, de acordo com os
                                                parâmetros passados.
    """
    mascara = '%%%s%d.%df' % (preenchimento, tamanho, casas)
    if not moeda and not moeda_internacional:
        formatado = locale.format(mascara, real(caracteres, casas,
                                  arredondamento, zero_se_vazio_ou_nulo), True,
                                  not len(locale.localeconv()['grouping']))
    else:
        # if p_cs_precedes/n_cs_precedes
        # if moeda and not moeda_internacional:
        # sem_preenchimento = formatado.lstrip(' ' + preenchimento)
        pass

    return formatado


def modulo_11(digitos, max=9, min=2, retorno=('0', '0'),
              soma=0, pesos=None, modulo=11, complemento=True,
              reduzir=False, zero_para='0'):
    r"""\brief Módulo 11 - cálculo do módulo 11 (ou outro) com parâmetros
       configuráveis.

    Esta função faz o cálculo da soma da multiplicação de cada dígito,
    de trás para frente, por min a max (padrão 2 a 9) ou pesos,
    respectivamente, retornando o complemento do resto da divisão desta
    soma por \c modulo (padrão 11), sendo que é possível passar uma
    lista de pesos, valor da soma inicial e uma lista dos caracteres de
    retorno quando o  resultado for 10 ou 11 (ou mais caso o módulo seja
    maior que 11), onde o primeiro elemento da lista é para resultado
    10, o segundo para 11, e assim por diante.

    \param digitos  [\c str/int]    Dígitos a serem fornecidos para se
                                    calcular o módulo destes.
    \param max      [\c int]        Valor máximo que o multiplicador
                                    para cálculo do módulo pode assumir,
                                    utilizado se \a peso for \c None.
                                    Padrão 9.
    \param min      [\c int]        Valor mínimo que o multiplicador
                                    para cálculo do módulo pode assumir,
                                    utilizado se \a peso for \c None.
                                    Padrão 2.
    \param retorno  [\c lista(str)] Lista de caracteres retornados
                                    quando o resultado for 10, 11, 12,
                                    e assim por diante, dependendo do
                                    módulo. Padrão ('0', '0').
    \param soma     [\c int]        Valor inicial da soma. Padrão 0.
    \param pesos    [\c lista(int)] Lista de pesos utilizados para
                                    calcular a soma, sendo que se for
                                    \c None será utilizado a faixa de
                                    \a min a \a max. Repare que o
                                    primeiro peso (correspondente a
                                    \a min) será aplicado ao último
                                    dígito, assim pode ser que seja
                                    necessário passar os pesos de forma
                                    inversar ou colocar \c [::-1] após a
                                    lista de pesos quando chamar a
                                    função. Padrão \c None.
    \param modulo   [\c int]        Valor a ser utilizado para cálculo
                                    do módulo. Padrão 11.
    \param compelmento  [\c bool]   Se retorna o complemento. Caso
                                    contrário retorna o resto. Padrão
                                    \c True.
    \param reuzir  [\c bool]        Se True, reduz o produto de cada
                                    elemento a um dígito.
    \return         [\c str]        O caracter correspondente ao cálculo
                                    do módulo.
    """
    if not digitos:
        return None
    digitos = somente_digitos(digitos)[::-1]            # Filtra apenas os dígitos e os inverte
    if pesos:                                           # Caso sejam fornecidos os pesos a operar
        pos_peso = 0                                      # posicionado no primeiro peso
        for digito in digitos:                            # Para cada dígito em digitos
            produto = int(digito) * pesos[pos_peso]         # Multiplica o dígito, tranformado em inteiro, pelo peso correspondente e o adiciona em soma
            if reduzir:
                while produto > 9:
                    produto = sum([int(x) for x in str(produto)])
            soma += produto
            if pos_peso == len(pesos):  # Se for o último peso, volta para o primeiro
                pos_peso = 0
            else:                       # Senão soma-se 1 a posição do peso
                pos_peso += 1
    else:                                               # Caso não sejam fornecidos os pesos a operar, trabalha com valores entre min e max
        mult = min                                        # Multiplicador inicial em min (este vai até max e volta a min)
        for digito in digitos:                            # Para cada dígito em digitos
            produto = int(digito) * mult                    # Multiplica o dígito, tranformado em inteiro, pelo multiplicador e o adiciona em soma
            if reduzir:
                while produto > 9:
                    produto = sum([int(x) for x in str(produto)])
            soma += produto
            if mult == max:  # Se o multiplicador for max, volta para min
                mult = min
            else:            # Senão soma-se 1 a este
                mult += 1
    resto_11 = soma % modulo                            # Resto da divisão da soma por 11
    if complemento:                                     # Se for pedido o complemento
        complemento_11 = modulo - resto_11                # Complento do resto por 11, isto é, o que falta para chegar a 11
    else:                                               # Se não for pedido o complemento
        complemento_11 = resto_11                         # Utiliza o resto por 11 para fazer o retorno
    if complemento_11 == 0:                             # Se for zero
        return zero_para                                  # Retorna o valor definido
    if complemento_11 > 9:                              # Se o complemento for maior que 9, isto é, dois dígitos
        return retorno[complemento_11-10]                 # Retorna o valor correspondente passado no parâmetro retorno da função, padrão '0'
    return str(complemento_11)                          # Retorna o complemento como caracter


def nulo_para_zero(valor):
    r"""\brief Retorna zero em \c float ser o valor for \c None ou o próprio \a valor caso contrário.

    \param valor    [\c untype]  Valor a ser analisado.
    \return         [\c untype]  0.0 (zero \c float) se valor for \c None ou o \a valor caso contrário.
    """
    if not valor:
        return 0.0
    return valor


def validar_cpf(cpf):
    r"""\brief Verifica a validade de um CPF informado.

    Verifica a validade de um CPF, sendo que elimina caracteres extras,
    considerando apenas os dígitos, completando com zeros à esquerda se necessário.
    Também emite avisos caso encontre algumas divergência.

    \param cpf  [\c str/int]    CPF a analisar.
    \return     [\c tupla]      Lista com 4 elementos:
                    1) \c True se validado e \c False caso contrário.
                    2) Dígitos do CPF esperado.
                    3) Avisos.
                    4) Dígitos do CPF fornecido que foram analisados.
    """
    if not cpf or cpf == '':
        return (False, '', ('CPF não informado.',), cpf)
    avisos = []
    digitos_cpf = somente_digitos(cpf)
    if len(digitos_cpf) != len(str(cpf)):  # CPF fornecido com algo além dos dígitos, analisando formatação...
        if len(str(cpf)) != 14:
            avisos += ['CPF mal formatado: esperado tamanho de 14 caracteres.']
        elif not (cpf[3] == cpf[7] == '.' and cpf[11] == '-'):
            avisos += ['CPF mal formatado: esperado `.´ nas posições 4 e 8 e `-´ na 12.']
    if len(digitos_cpf) != 11:
        avisos += ['CPF com poucos dígitos, completado com zeros à esquerda.']
        digitos_cpf = ('00000000000' + digitos_cpf)[-11:]
    dv1 = modulo_11(digitos_cpf[:9], 11)
    dv2 = modulo_11(digitos_cpf[:9] + dv1, 11)
    cpf_esperado = digitos_cpf[:9] + dv1 + dv2
    verificado = (cpf_esperado == digitos_cpf)
    if not verificado:
        avisos += ['CPF inválido: dígitos verificadores não conferem.']
    return (verificado, cpf_esperado, avisos[1:], digitos_cpf)


def formatar_cpf(cpf):
    r"""\brief Formata o CPF informado.

    Considerando apenas os dígitos, colocar um ponto entre cada 3 dos 9
    dígitos iniciais, um traço e os dois dígitos verificadores.
    Também completa com zeros à se faltar e retorna dígitos extras, se
    houver, logo após os dígitos verificadores.

    \param cpf  [\c str/int]    CPF a formatar.
    \return     [\c str]        CPF formatado.
    """
    digitos = ('00000000000' + somente_digitos(cpf))[-11:]
    return digitos[:3] + '.' + digitos[3:6] + '.' + digitos[6:9] + '-' + digitos[9:]


def validar_cnpj(cnpj):
    r"""\brief Verifica a validade do CNPJ informado.

    Verifica a validade de um CNPJ, sendo que elimina caracteres extras,
    considerando apenas os dígitos, completando com zeros à esquerda se necessário.
    Também emite avisos caso encontre algumas divergência.

    \param cnpj  [\c str/int]    CNPJ a analisar.
    \return      [\c tupla]      Lista com 4 elementos:
                    1) \c True se validado e \c False caso contrário.
                    2) Dígitos do CNPJ esperado.
                    3) Avisos.
                    4) Dígitos do CNPJ fornecido que foram analisados.
    """
    if not cnpj or cnpj == '':
        return (False, '', ('CNPJ não informado.',), cnpj)
    avisos = []
    digitos_cnpj = somente_digitos(cnpj)
    # CNPJ fornecido com algo além dos dígitos, analisando formatação...
    if len(digitos_cnpj) != len(str(cnpj)):
        if len(str(cnpj)) != 19:
            avisos += ['CNPJ mal formatado:'
                       ' esperado tamanho de 14 caracteres.']
        elif not (cnpj[2] == cnpj[6] == '.'
                  and cnpj[10] == '/' and cnpj[15] == '-'):
            avisos += ['CNPJ mal formatado: esperado `.´ nas posições 4 e 8'
                       ' e `-´ na 12.']
    if len(digitos_cnpj) != 14:
        avisos += ['CNPJ com poucos dígitos, completado com zeros à esquerda.']
        digitos_cnpj = ('00000000000000' + digitos_cnpj)[-14:]
    dv1 = modulo_11(digitos_cnpj[:12])
    dv2 = modulo_11(digitos_cnpj[:12] + dv1)
    cnpj_esperado = digitos_cnpj[:12] + dv1 + dv2
    verificado = (cnpj_esperado == digitos_cnpj)
    if not verificado:
        avisos += ['CNPJ inválido: dígitos verificadores não conferem.']
    return (verificado, cnpj_esperado, tuple(avisos), digitos_cnpj)


def formatar_cnpj(cnpj):
    r"""\brief Formata o CNPJ informado.

    Considerando apenas os dígitos, colocar um ponto após o 2º dígito e entre
    cada 3 dos 6 dígitos seguintes, uma barra seguida dos 4 dígitos de
    nº de unidade, um traço e os dois dígitos verificadores.
    Também completa com zeros à se faltar e retorna dígitos extras, se
    houver, logo após os dígitos verificadores.

    \param cnpj [\c str/int]    CNPJ a formatar.
    \return     [\c str]        CNPJ formatado.
    """
    digitos = ('00000000000000' + somente_digitos(cnpj))[-14:]
    return (digitos[:2] + '.' + digitos[2:5] + '.' +
            digitos[5:8] + '/' + digitos[8:12] + '-' + digitos[12:])


def DV1_MG(digitos):
    r"""\brief Cálculo do 1º dígito verificador de Minas Gerais (MG).

    Insere-se '0' entre os 3º e 4º dígitos, multica-se cada dígito por
    1 e 2 sucessivamente, juntando os resultados numa lista de dígitos,
    depois soma-se os dígitos desta lista e retorna o complemento do
    resto da divisão desta soma por 10.

    \param digitos      [\c str/int] 11 dígitos da IE de MG.
    \return             [\c str] 1º dígito verificador.
    """
    if not digitos:
        return None
    digitos = somente_digitos(digitos)
    digitos = digitos[:3] + '0' + digitos[3:]
    lista = ''
    mult = 1
    for digito in digitos:
        lista += str(int(digito) * mult)
        mult += 1 - (mult == 2) * 2
    soma = 0
    for digito in lista:
        soma += int(digito)
    if not soma % 10:
        return '0'
    return str(10 - soma % 10)


def DV_RR(digitos):
    r"""\brief Cálculo do dígito verificador de Roraima (RR).

    Esta função faz o cálculo da soma da multiplicação de cada dígito
    pela sua posição, retornando o resto da divisão desta soma por 9.

    \param digitos  [\c str/int]    Dígitos a serem fornecidos para se
                                    calcular o DV de RR.
    \return         [\c str]        Caracter correspondente ao DV de RR.
    """
    if not digitos:
        return None
    digitos = somente_digitos(digitos)
    mult = 1
    soma = 0
    for digito in digitos:
        soma += int(digito) * mult
        mult += 1
    return str(soma % 9)


ufs = ('AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
       'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
       'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO')
digitos = {'AC': 13, 'AL':  9, 'AP':  9, 'AM':  9, 'BA':  9,
           'CE':  9, 'DF': 13, 'ES':  9, 'GO':  9, 'MA':  9,
           'MT': 11, 'MS':  9, 'MG': 13, 'PA':  9, 'PB':  9,
           'PR': 10, 'PE':  9, 'PI':  9, 'RJ':  8, 'RN': 10,
           'RS': 10, 'RO': 14, 'RR':  9, 'SC':  9, 'SP': 12,
           'SE':  9, 'TO':  9}
fixo_inicial = {'AC': None,
                'AL': ('24',),
                'AP': ('03',),
                'AM': None,
                'BA': None,
                'CE': None,
                'DF': ('07',),
                'ES': None,
                'GO': ('10', '11', '15'),
                'MA': None,
                'MT': None,
                'MS': ('2',),
                'MG': None,
                'PA': ('15',),
                'PB': None,
                'PR': None,
                'PE': None,
                'PI': None,
                'RJ': None,
                'RN': ('20',),
                'RS': None,
                'RO': None,
                'RR': ('24',),
                'SC': ('25',),
                'SP': None,
                'SE': ('27',),
                'TO': ('29',)}
formatacao = {'AC': (('.', 2), ('.', 6), ('/', 10), ('-', 14)),
              'AL': (('.', 2), ('.', 6), ('-', 10)),
              'AP': (('.', 2), ('.', 6), ('-', 10)),
              'AM': (('.', 2), ('.', 6), ('-', 10)),
              'BA': (('.', 3), ('.', 7)),
              'CE': (('.', 2), ('.', 6), ('-', 10)),
              'DF': (('.', 2), ('.', 9), ('-', 13)),
              'ES': (('.', 2), ('.', 6), ('-', 10)),
              'GO': (('.', 2), ('.', 6), ('-', 10)),
              'MA': (('.', 2), ('.', 6), ('-', 10)),
              'MT': (('.', 2), ('.', 6), ('-', 10)),
              'MS': (('.', 2), ('.', 6), ('-', 10)),
              'MG': (('.', 2), ('.', 6), ('.', 10), ('-', 13)),
              'PA': (('.', 2), ('.', 6), ('-', 10)),
              'PB': (('.', 2), ('.', 6), ('-', 10)),
              'PR': (('.', 2), ('.', 6), ('-', 10)),
              'PE': (('.', 1), ('.', 5), ('-', 9)),
              'PI': (('.', 2), ('.', 6), ('-', 10)),
              'RJ': (('.', 2), ('.', 6), ('-', 10)),
              'RN': (('.', 2), ('.', 6), ('-', 10)),
              'RS': (('/', 3),),
              'RO': (('.', 1), ('.', 5), ('.', 9), ('.', 13), ('-', 17)),
              'RR': (('.', 2), ('.', 6), ('-', 10)),
              'SC': (('.', 3), ('.', 7)),
              'SP': (('.', 3), ('.', 7), ('.', 11)),
              'SE': (('.', 2), ('.', 6), ('-', 10)),
              'TO': (('.', 2), ('.', 6), ('-', 10))}


def validar_ie(ie, uf):
    r"""\brief Verifica a validade da Inscrição Estadual para a UF
              informada.

    \param ie   [\c str/int]    Inscrição Estadual a analisar.
    \param uf   [\c str/int]    Unidade Federativa a qual pertence a IE.
    \return      [\c tupla]      Lista com 4 elementos:
                    1) \c True se validado e \c False caso contrário.
                    2) Dígitos da IE esperada.
                    3) Avisos.
                    4) Dígitos da IE fornecido que foram analisados.

    Veja as regras em http://www.sintegra.gov.br/insc_est.html,
                               http://www.sintegra.gov.br/Verific8.doc e
                        http://www.pfe.fazenda.sp.gov.br/consist_ie.shtm
    \param Acre(AC)                 01.004.823/001-12 - 13 dígitos, módulo 11.
    \param Alagoas(AL)              24XNNNNND - 9 dígitos, 24 fixo, X em [0,3,5,7,8], N é dígito, D por módulo 11.
    \param Amapá(AP)                03NNNNNND - 9 dígitos, 03 fixo, N é dígito, D por módulo 11 (11=d, soma=p), onde p=5 e d=0 para 03000001 a 03017000, p=9 e d=1 para 03017001 a 03019022 e p=0 e d=0 para 03019023 em diante.
    \param Amazonas(AM)             99.999.999-9 - 9 dígitos, módulo 11
    \param Bahia(BA)                Mudou para xxx.xxx.xxx || 612345-57 - 8 dígitos, módulo 10 se iniciar por [0,1,2,3,4,5,8] e módulo 11 caso contrário, calculando e 2º DV antes
    \param Ceará(CE)                06000001-5 - 9 dígitos, módulo 11.
    \param Distrito_Federal(DF)     07.300001.001-09 - 13 dígitos, 07 fixo, módulo 11.
    \param Espírito_Santo(ES)       99.999.999-0 - 9 dígitos, módulo 11.
    \param Goiás(GO)                10.987.654-7 - 9 dígitos, 2 primeiros em [10,11,15], módulo 11.
    \param Maranhão(MA)             12000038-5 - 9 dígitos, módulo 11.
    \param Mato_Grosso(MT)          0013000001-9 - 11 dígitos, módulo 11.
    \param Mato_Grosso_do_Sul(MS)   2NNNNNNN-D - 9 dígitos, 2 fixo, módulo 11.
    \param Minas_Gerais(MG)         062.307.904/0081 - 13 dígitos, 3 município, 6 código, 2 ordem de estabelecimento, 1º DV por DV1_MG (inserindo '0' entre o 3º e o 4º dígitos), e 2º DV por módulo 11 com max=11.
    \param Pará(PA)                 15-999999-5 - 9 dígitos, 15 fixo, módulo 11.
    \param Paraíba(PB)              06.000.001-5 - 9 dígitos, módulo 11.
    \param Paraná(PR)               NNN.NNNNN-DD - 10 dígitos, módulo 11 com max=7.
    \param Pernambuco(PE)           0321418-40 - 9 dígitos, módulo 11. Obs.: antigamente 18.1.001.0000004-9, por módulo 11, mas depois o 9 volta para 1, não implementado.
    \param Piauí(PI)                01234567-9 - 9 dígitos, módulo 11.
    \param Rio_de_Janeiro(RJ)       99.999.99-3 - 8 dígitos, módulo 11 com max=7.
    \param Rio_Grande_do_Norte(RN)  20.040.040-1(9 dígitos) ou 20.0.040.040-0(10 dígitos) - 20 fixo, módulo 11 com max=10.
    \param Rio_Grande_do_Sul(RS)    224/365879-2 - 10 dígitos, 3 dígitos do município, módulo 11.
    \param Rondônia(RO)             0000000062521-3 - 14 dígitos, módulo 11. Obs.: antes de 01/08/2000 era, 101.62521-3 - 3 dígitos do município, módulo 11 dos outros 5 dígitos.
    \param Roraima(RR)              24.008266-8 - 9 dígitos, 24 fixo, DV_RR (~ módulo 9).
    \param Santa_Catarina(SC)       251.040.852 - 9 dígitos, 25 fixo, último dígito é módulo 11.
    \param São_Paulo(SP)            110.042.490.114 - 12 dígitos, 9º e 12º dígitos verificadores => 9º: resto por 11 dos 8 primeiros dígitos com os pesos [1,3,4,5,6,7,8,10] da esquerda para a direita (inverso do princípio do módulo 11, usa [::-1]); 12º: resto por 11 dos 11 dígitos anteriores com max=10. Obs.: São Paulo não tem mais IE de produtor.
    \param Sergipe(SE)              27.123.456-3 - 9 dígitos, 27 fixo, módulo 11.
    \param Tocantins(TO)            29.01.022783-6 - 11 dígitos, 29 fixo, 3º e 4º em [01,02,03,99], módulo 11.
    """
    uf = uf.upper()
    if uf not in ufs:
        return (False, '', ('UF `' + uf + '´não encontrada. Deveria ser uma entre: ' + ', '.join(ufs)[::-1].replace(',', 'uo ', 1)[::-1],), ie)
    if not ie or ie == '':
        return (False, '', ('Inscrição Estadual não informada.', ), ie)
    if ie == 'ISENTO':
        return (True, 'ISENTO', '', ie)
    digitos_ie = somente_digitos(ie)
    if not int(digitos_ie):
        return (False, '', ('Inscrição Estadual inválida por não conter dígitos.', ), ie)
    avisos = []
    if uf == 'TO' and len(digitos_ie) == 11:
        if digitos_ie[2:4] not in ('01', '02', '03', '99'):
            return (False, '', ('Inscrição Estadual inválida por não conter 01, 02, 03 ou 99 nos 3º e 4º dígitos.', ), ie)
        digitos_ie = digitos_ie[:2] + digitos_ie[4:]
    if len(str(ie)) > len(digitos_ie):
        if len(str(ie)) == digitos[uf] + len(formatacao[uf]):
            divergencias = ''
            for caracter, posicao in formatacao[uf]:
                if ie[posicao] != caracter:
                    divergencias += 'esperado ' + caracter + ' e encontrado ' + ie[posicao] + ' na posição ' + str(posicao) + '; '
            if divergencias != '':
                avisos += ['IE mal formatada: ' + divergencias[:-2] + '.']
        else:
            avisos += ['IE mal formatado: esperado tamanho de ' + str(digitos[uf] + len(formatacao[uf])) + ' caracteres para ' + uf + ', mas encontrado ' + str(len(str(ie))) + '.']
    if len(digitos_ie) > digitos[uf]:
        avisos += ['IE com muitos dígitos: esperado ' + str(digitos[uf]) + ' dígitos e encontrado ' + str(len(digitos_ie)) + '.']
        return (False, '', avisos, digitos_ie)
    if len(digitos_ie) < digitos[uf] - (uf == 'RN'):  # RN pode aceitar 9 dígitos
        if ie[0] != 'P':
            avisos += ['IE com poucos dígitos: esperado ' + str(digitos[uf]) + ' digitos e encontrado ' + str(len(digitos_ie)) + ', completando com zeros à esquerda.']
            digitos_ie = ('0' * digitos[uf] + digitos_ie)[-digitos[uf]:]
    if fixo_inicial[uf]:
        if digitos_ie[:len(fixo_inicial[uf][0])] not in fixo_inicial[uf]:
            esperado = ', '.join(fixo_inicial[uf])[::-1].replace(',', 'uo ', 1)[::-1]
            avisos += ['Dígitos iniciais não conferem para ' + uf + ': econtrado ' + digitos_ie[:len(fixo_inicial[uf][0])] + ', mas esperado ' + esperado + '.']
    if uf in ('AC', 'DF', 'PE'):
        dv1 = modulo_11(digitos_ie[:-2])
        dv2 = modulo_11(digitos_ie[:-2] + dv1)
        ie_esperada = digitos_ie[:-2] + dv1 + dv2
    elif uf in ('RO'):
        dv = modulo_11(digitos_ie[:-1], retorno=('0', '1'))
        ie_esperada = digitos_ie[:-1] + dv
    elif uf in ('AL', 'AM', 'CE', 'ES', 'GO', 'MA', 'MT', 'MS', 'PA', 'PB', 'PI', 'RN', 'SC', 'SE', 'TO', 'RS'):
        dv = modulo_11(digitos_ie[:-1])
        ie_esperada = digitos_ie[:-1] + dv
    elif uf == 'AP':
        if int(digitos_ie[:-1]) <= 3017000:
            dv = modulo_11(digitos_ie[:8], soma=5)
        elif int(digitos_ie[:-1]) <= 3019022:
            dv = modulo_11(digitos_ie[:-1], soma=9, resto=('0', '1'))
        else:
            dv = modulo_11(digitos_ie[:-1])
        ie_esperada = digitos_ie[:-1] + dv
    elif uf == 'BA':
        if digitos_ie[1] in ('0', '1', '2', '3', '4', '5', '8'):
            dv2 = modulo_11(digitos_ie[:-2], modulo=10)
            dv1 = modulo_11(digitos_ie[:-2] + dv2, modulo=10)
        else:
            dv2 = modulo_11(digitos_ie[:-2])
            dv1 = modulo_11(digitos_ie[:-2] + dv2)
        ie_esperada = digitos_ie[:-2] + dv1 + dv2
    elif uf == 'PR':
        dv1 = modulo_11(digitos_ie[:-2], max=7)
        dv2 = modulo_11(digitos_ie[:-2] + dv1, max=7)
        ie_esperada = digitos_ie[:-2] + dv1 + dv2
    elif uf == 'RJ':
        dv = modulo_11(digitos_ie[:-1], max=7)
        ie_esperada = digitos_ie[:-1] + dv
    elif uf == 'RR':
        dv = DV_RR(digitos_ie[:-1])
        ie_esperada = digitos_ie[:-1] + dv
    elif uf == 'SP':
        dv1 = modulo_11(digitos_ie[:8], pesos=[1, 3, 4, 5, 6, 7, 8, 10][::-1], complemento=False)
        dv2 = modulo_11(digitos_ie[:8] + dv1 + digitos_ie[9:11], max=10, complemento=False)
        ie_esperada = digitos_ie[:8] + dv1 + digitos_ie[9:11] + dv2
    elif uf == 'MG':
        if ie[0] == 'P':
            ie_esperada = 'PR' + digitos_ie
        else:
            dv1 = DV1_MG(digitos_ie[:-2])
            dv2 = modulo_11(digitos_ie[:-2] + dv1, max=11)
            ie_esperada = digitos_ie[:-2] + dv1 + dv2
    else:
        ie_esperada = ''
    verificado = (ie_esperada[:2] == 'PR' or ie_esperada == digitos_ie)
    if not verificado:
        avisos += ['IE inválida: dígitos verificadores não conferem. (' + formatar_ie(ie_esperada, uf) + ')']
    return (verificado, ie_esperada, tuple(avisos), digitos_ie)

    '''
    dv1 = modulo_11(digitos_cnpj[:12])
    dv2 = modulo_11(digitos_cnpj[:12] + dv1)
    cnpj_esperado = digitos_cnpj[:12] + dv1 + dv2
    verificado = (cnpj_esperado == digitos_cnpj)
    if not verificado:
        avisos += ' CNPJ inválido: dígitos verificadores não conferem'
    return (verificado, cnpj_esperado, avisos[1:], digitos_cnpj)
    '''


def formatar_ie(ie, uf):
    r"""\brief Formata a Inscrição Estadual informada.

    Considerando apenas os dígitos, colocar um ponto após o 2º dígito e entre cada 3 dos 6
    dígitos seguintes, uma barra seguida dos 4 dígitos de nº de unidade,
    um traço e os dois dígitos verificadores.
    Também completa com zeros à se faltar e retorna dígitos extras, se
    houver, logo após os dígitos verificadores.

    \param ie   [\c str/int]    Inscrição Estadual a formatar.
    \param uf   [\c str/int]    Unidade Federativa a qual pertence a IE.
    \return     [\c str]        IE formatada.
    """
    uf = uf.upper()
    if uf not in ufs:
        return ''
    digitos_ie = somente_digitos(ie)
    digitos_ie = ('0' * digitos[uf] + digitos_ie)[-digitos[uf]:]
    formatado = ''
    posicao_anterior = 0
    contador = 0
    for caracter, posicao_atual in formatacao[uf]:
        formatado += digitos_ie[posicao_anterior:posicao_atual - contador] + caracter
        posicao_anterior = posicao_atual - contador
        contador += 1
    formatado += digitos_ie[posicao_anterior:]
    return formatado


def validar_rg(rg, uf):
    r"""\brief Para fazer.
    """
    pass


def formatar_rg(rg, uf):
    r"""\brief Para fazer.
    """
    pass


def enviar_email(servidor, remetente, senha, destinatarios, assunto=None, texto=None, html_ou_arquivo_html=None, conteudo=None,
                 nome_da_maquina_local=None, confirmar_recebimento=True, arquivos_anexos=None, alias=None,
                 seguranca=None, arquivo_chave=None, arquivo_certificado=None, timeout=10):
    # Nome da máquina local
    if not nome_da_maquina_local:
        nome_da_maquina_local = 'localhost.localdomain'
    # Servidor e porta, porta 465 padrão para SSL/TLS e 587 para outra segurança
    if seguranca:
        seguranca = seguranca.upper()
    servidor, porta = (servidor.strip() + (':465' if seguranca == 'SSL/TLS' else ':587')).split(':')[:2]
    porta = int(porta)
    # Se não especificada a segurança, está será SSL/TLS para porta 465 e Nenhuma para outras portas
    if not seguranca:
        seguranca = 'SSL/TLS' if porta == 465 else None
    # Se a segurança for SSL/TLS, inicia conexão SSL, senão conexão normal
    if seguranca == 'SSL/TLS':
        conexao = smtplib.SMTP_SSL(servidor, porta, nome_da_maquina_local, arquivo_chave, arquivo_certificado, timeout)
    else:
        conexao = smtplib.SMTP(servidor, porta, nome_da_maquina_local, timeout)
        # Se a segurança for STARTTLS, inicia troca de certificado
        if seguranca == 'STARTTLS':
            conexao.starttls()
    # Autenticar no servidor SMTP, se não tiver senha não autentica
    if senha and senha.strip():
        remetente_autenticacao = re.sub(r'.*<(.*)>', r'\1', remetente)
        conexao.login(remetente_autenticacao, senha)
    # Coloca um texto e html básicos caso não seja especificado o texto e nem o html
    if conteudo:
        pass
    elif not texto and not html_ou_arquivo_html:
        texto = 'Corpo da mensagem não especificado.'
        html = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html lang="pt-br">
    <head>
        <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
        <meta content="Junior Polegato, Claudio" name="author" />
        <title>Enviando e-mail utilizando Python</title>
    </head>
    <body>
        <h1>Corpo da mensagem não especificado.</h1>
    </body>
</html>
'''
    elif texto:
        html = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html lang="pt-br">
    <head>
        <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
        <meta content="Junior Polegato, Claudio" name="author" />
        <title>Enviando e-mail utilizando Python</title>
    </head>
    <body>
        ''' + texto.replace('\r', '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br/>\n').replace('  ', '&nbsp; ') + '''
    </body>
</html>
'''
    else:
        if html_ou_arquivo_html[0] != '<':
            arquivo_html = open(html_ou_arquivo_html)
            html = arquivo_html.read()
            arquivo_html.close()
        else:
            html = html_ou_arquivo_html
        # Extrair o corpo da mensagem html
        texto = re.sub(r'.*<body>(.*)</body>.*', r'\1', html.replace('\n', ''))
        # Trocar negrito no modo html por * no modo texto
        texto = re.sub(r'<b>|</b>', r'*', texto)
        # Trocar itálico no modo html por / no modo texto
        texto = re.sub(r'<i>|</i>', r'/', texto)
        # Trocar sublinhado no modo html por _ no modo texto
        texto = re.sub(r'<u>|</u>', r'_', texto)
        # Identificar quebras de linha no html e colocar no modo texto
        texto = re.sub(r'<br>|<br.*/>|<p>|</p>|<h.>|</h.>', r'\n', texto)
        # Ignorar as marcações html
        texto = re.sub(r'<[^>]*>', r'', texto)
        # Substituir vários espaços e tabulações juntos por um espaço só
        re.sub(r'[ \t][ \t]*', r' ', texto)
        # Eliminar o espaço residual depois de uma quebra de linha
        texto = texto.replace('\n ', '\n')
        # Eliminar o espaço residual antes de uma quebra de linha
        texto = texto.replace(' \n', '\n')
        # Trocar o &nbsp; por espaço, &gt; por >, &lt; por <, &quote; por ", &#39; por ' e &amp; por &
        texto = texto.replace('&nbsp;', ' ').replace('&gt;', '>').replace('&lt;', '<').replace('&quote;', '"').replace('&#39;', "'").replace('&amp;', '&')
    # Fuso horário no formato RFC 822
    fuso = datetime.datetime.now() - datetime.datetime.utcnow()
    fuso = int(fuso.days * 24 * 60 + (fuso.seconds + fuso.microseconds / 1000000.) / 60.)
    fuso = '%+03d%02d' % (fuso / 60, fuso % 60)
    locale.setlocale(locale.LC_ALL, 'C')
    data = 'Date: ' + datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:%S ') + fuso + '\r\n'
    locale.setlocale(locale.LC_ALL, '')

    de = alias if alias else remetente

    if not confirmar_recebimento:
        confirmacao = ''
    elif confirmar_recebimento is True:
        confirmacao = 'Disposition-Notification-To: ' + de + '\r\n'
    else:
        confirmacao = 'Disposition-Notification-To: ' + confirmar_recebimento + '\r\n'

    # Compor a mensagem com o cabeçalho, texto, html e arquivos em anexo
    boundary = (conteudo.split("\n", 1)[0].strip()[2:] if conteudo and conteudo[:2] == "--"
                else "SnVuaW9yIFBvbGVnYXRvIG14")
    cabecalho = (confirmacao +
                 data +
                 'From: ' + de + '\r\n'
                 'User-Agent: EnvMail - Junior Polegato - v0.2 - Python\r\n'
                 'MIME-Version: 1.0\r\n'
                 'To: ' + ',\r\n    '.join(destinatarios) + '\r\n'
                 'Subject: ' + assunto + '\r\n'
                 'Content-Type: multipart/' +
                 ('mixed' if arquivos_anexos else 'alternative') + ';\r\n'
                 '    boundary="' + boundary + '"\r\n'
                 '\r\n')
    texto_html = conteudo if conteudo else (
        'This is a multi-part message in MIME format.\r\n'
        '--' + boundary + '\r\n'
        'Content-Type: multipart/alternative;\r\n'
        '    boundary="' + boundary + 'X"\r\n'
        '\r\n'
        '--' + boundary + 'X\r\n'
        'Content-Type: text/plain; charset=UTF-8; format=flowed\r\n'
        'Content-Transfer-Encoding: 8bit\r\n'
        '\r\n'
        + texto + '\r\n'
        '\r\n'
        '--' + boundary + 'X\r\n'
        'Content-Type: text/html; charset=UTF-8\r\n'
        'Content-Transfer-Encoding: 7bit\r\n'
        '\r\n'
        + html + '\r\n'
        '\r\n'
        '--' + boundary + 'X--\r\n')
    # Aqui vem os anexos em base64
    mimetypes.init()
    if arquivos_anexos:
        anexos = []
        for anexo in arquivos_anexos:
            if isinstance(anexo, (list, tuple)):
                anexo, conteudo = anexo
            else:
                with open(anexo) as arquivo:
                    conteudo = arquivo.read()
            tipo = mimetypes.guess_type(anexo)
            if not tipo[0]:
                tipo = ('application/binary', None)
            # print "Anexando:", anexo, " - ", tipo[0]
            # print conteudo
            # print base64.encodestring(conteudo)
            anexos += ['--' + boundary + '\r\n'
                       'Content-Type: ' + tipo[0] + ';\r\n'
                       '    name="' + re.sub(r'.*/', r'', anexo) + '"\r\n'
                       'Content-Transfer-Encoding: base64\r\n'
                       '\r\n'
                       + base64.encodestring(conteudo)]
        anexos = '\r\n'.join(anexos) + '--' + boundary + '--\r\n'
    else:
        anexos = '--' + boundary + '--\r\n'

    # Enviar a mensagem
    # print 'Enviando...'
    conexao.sendmail(remetente, destinatarios, cabecalho + texto_html + anexos)
    # Terminar a conexão
    # print 'Terminando...'
    conexao.quit()


def varrer_mg():
    print '\n\n\n\n\n\n-------------------------------------------------------------------\n\n\n'
    import cx_Oracle as oracle
    conexao = oracle.connect('usuario/senha@banco')
    cursor = conexao.cursor()
    UF = 'MG'
    cursor.execute("select cod_entidade, razao_social, cnpj, inscr_estadual from entidade where pessoa = 'J' and substr(regiao, 1, 2) = '" + UF + "'")
    entidades = cursor.fetchall()
    print '\n\nCNPJ - Jurídica\n'
    erros = 0
    for entidade in entidades:
        resultado = validar_cnpj(entidade[2])
        if not resultado[0]:
            erros += 1
            print formatar_inteiro(erros, tamanho=4) + ': ' + ' ' * (18 - len(str(entidade[2]))) + str(entidade[2]) + ' - ' + formatar_inteiro(entidade[0], tamanho=5) + ' - ' + entidade[1]

    print '\n\nIE - Jurídica\n'
    erros = 0
    for entidade in entidades:
        resultado = validar_ie(entidade[3], UF)
        if not resultado[0]:
            erros += 1
            print formatar_inteiro(erros, tamanho=4) + ': ' + ' ' * (18 - len(str(entidade[3]))) + str(entidade[3]) + ' - ' + formatar_inteiro(entidade[0], tamanho=5) + ' - ' + entidade[1]

    cursor.execute("select cod_entidade, razao_social, cpf, rg from entidade where pessoa = 'F' and substr(regiao, 1, 2) = '" + UF + "'")
    entidades = cursor.fetchall()
    print '\n\nCPF - Física\n'
    erros = 0
    for entidade in entidades:
        resultado = validar_cpf(entidade[2])
        if not resultado[0]:
            erros += 1
            print formatar_inteiro(erros, tamanho=4) + ': ' + ' ' * (18 - len(str(entidade[2]))) + str(entidade[2]) + ' - ' + formatar_inteiro(entidade[0], tamanho=5) + ' - ' + entidade[1]

    cursor.execute("select cod_entidade, razao_social, cpf from entidade where pessoa = 'P' and substr(regiao, 1, 2) = '" + UF + "'")
    entidades = cursor.fetchall()
    print '\n\nCPF - Produtor\n'
    erros = 0
    for entidade in entidades:
        resultado = validar_cpf(entidade[2])
        if not resultado[0]:
            erros += 1
            print formatar_inteiro(erros, tamanho=4) + ': ' + ' ' * (18 - len(str(entidade[2]))) + str(entidade[2]) + ' - ' + formatar_inteiro(entidade[0], tamanho=5) + ' - ' + entidade[1]

    cursor.execute("select cod_entidade, razao_social, cnpj from entidade where pessoa = 'P' and (cnpj is not null or cnpj <> '' or cpf is null or cpf = '') and substr(regiao, 1, 2) = '" + UF + "'")
    entidades = cursor.fetchall()
    print '\n\nCNPJ - Produtor\n'
    erros = 0
    for entidade in entidades:
        resultado = validar_cnpj(entidade[2])
        if not resultado[0]:
            erros += 1
            print formatar_inteiro(erros, tamanho=4) + ': ' + ' ' * (18 - len(str(entidade[2]))) + str(entidade[2]) + ' - ' + formatar_inteiro(entidade[0], tamanho=5) + ' - ' + entidade[1]

    cursor.execute("select cod_entidade, razao_social, inscr_estadual from entidade where pessoa = 'P' and (inscr_estadual is not null or rg is null) and substr(regiao, 1, 2) = '" + UF + "'")
    entidades = cursor.fetchall()
    print '\n\nIE - Produtor\n'
    erros = 0
    for entidade in entidades:
        avisos = ''
        if entidade[2][:2] != 'PR':
            avisos = 'Deve iniciar com PR. '
        digitos = somente_digitos(entidade[2])
        if len(digitos) != 7:
            if len(digitos) != 13:
                avisos += 'Deve ter 7 dígitos no formato PR123/1234.'
            else:
                resultado = validar_ie(entidade[2], UF)
                if not resultado[0]:
                    erros += 1
                    print formatar_inteiro(erros, tamanho=4) + ': ' + ' ' * (18 - len(str(entidade[2]))) + str(entidade[2]) + ' - ' + formatar_inteiro(entidade[0], tamanho=5) + ' - ' + entidade[1]
                continue
        else:
            pass
            # cursor.execute("update entidade set inscr_estadual = 'PR" + digitos[:3] + '/' + digitos[3:] + "' where cod_entidade = " + str(entidade[0]))
            # cursor.execute("commit")
        if avisos != '':
            erros += 1
            print formatar_inteiro(erros, tamanho=4) + ': ' + ' ' * (18 - len(str(entidade[2]))) + str(entidade[2]) + ' - ' + formatar_inteiro(entidade[0], tamanho=5) + ' - ' + entidade[1] + ' => ' + avisos

    cursor.execute("select cod_entidade, razao_social, rg from entidade where pessoa = 'P' and inscr_estadual is null and substr(regiao, 1, 2) = '" + UF + "'")
    entidades = cursor.fetchall()
    print '\n\nIE - Produtor encontrada no RG, colocar no lugar correto\n'
    erros = 0
    for entidade in entidades:
        avisos = ''
        if entidade[2][:2] != 'PR':
            avisos = 'Deve iniciar com PR. '
        if len(somente_digitos(entidade[2])) == 7:
            pass
        else:
            avisos += 'Deve ter 7 dígitos no formato PR123/1234.'
        if avisos != '':
            erros += 1
            print formatar_inteiro(erros, tamanho=4) + ': ' + ' ' * (18 - len(str(entidade[2]))) + str(entidade[2]) + ' - ' + formatar_inteiro(entidade[0], tamanho=5) + ' - ' + entidade[1] + ' => ' + avisos


def varrer_sp():
    print '\n\n\n\n\n\n-------------------------------------------------------------------\n\n\n'
    import cx_Oracle as oracle
    conexao = oracle.connect('usuario/senha@banco')
    cursor = conexao.cursor()
    UF = 'SP'
    '''
    cursor.execute("select cod_entidade, razao_social, cnpj, inscr_estadual from entidade where pessoa = 'J' and substr(regiao, 1, 2) = '" + UF + "'")
    entidades = cursor.fetchall()
    print '\n\nCNPJ - Jurídica\n'
    erros = 0
    for entidade in entidades:
        resultado = validar_cnpj(entidade[2])
        if not resultado[0]:
            erros += 1
            print formatar_inteiro(erros, tamanho=4) + ': ' + ' ' * (18 - len(str(entidade[2]))) + str(entidade[2]) + ' - ' + formatar_inteiro(entidade[0], tamanho=5) + ' - ' + entidade[1]

    print '\n\nIE - Jurídica\n'
    erros = 0
    for entidade in entidades:
        resultado = validar_ie(entidade[3], UF)
        if not resultado[0]:
            erros += 1
            print formatar_inteiro(erros, tamanho=4) + ': ' + ' ' * (18 - len(str(entidade[3]))) + str(entidade[3]) + ' - ' + formatar_inteiro(entidade[0], tamanho=5) + ' - ' + entidade[1]

    cursor.execute("select cod_entidade, razao_social, cpf, rg from entidade where pessoa = 'F' and razao_social is not null and substr(regiao, 1, 2) = '" + UF + "'")
    entidades = cursor.fetchall()
    print '\n\nCPF - Física\n'
    erros = 0
    for entidade in entidades:
        resultado = validar_cpf(entidade[2])
        if not resultado[0]:
            erros += 1
            print formatar_inteiro(erros, tamanho=4) + ': ' + ' ' * (18 - len(str(entidade[2]))) + str(entidade[2]) + ' - ' + formatar_inteiro(entidade[0], tamanho=5) + ' - ' + entidade[1]

    cursor.execute("select cod_entidade, razao_social, cpf from entidade where pessoa = 'P' and substr(regiao, 1, 2) = '" + UF + "'")
    entidades = cursor.fetchall()
    print '\n\nCPF - Produtor\n'
    erros = 0
    for entidade in entidades:
        resultado = validar_cpf(entidade[2])
        if not resultado[0]:
            erros += 1
            print formatar_inteiro(erros, tamanho=4) + ': ' + ' ' * (18 - len(str(entidade[2]))) + str(entidade[2]) + ' - ' + formatar_inteiro(entidade[0], tamanho=5) + ' - ' + entidade[1]

    cursor.execute("select cod_entidade, razao_social, cnpj from entidade where pessoa = 'P' and (cnpj is not null or cnpj <> '' or cpf is null or cpf = '') and substr(regiao, 1, 2) = '" + UF + "'")
    entidades = cursor.fetchall()
    print '\n\nCNPJ - Produtor\n'
    erros = 0
    for entidade in entidades:
        resultado = validar_cnpj(entidade[2])
        if not resultado[0]:
            erros += 1
            print formatar_inteiro(erros, tamanho=4) + ': ' + ' ' * (18 - len(str(entidade[2]))) + str(entidade[2]) + ' - ' + formatar_inteiro(entidade[0], tamanho=5) + ' - ' + entidade[1]
    '''
    cursor.execute("select cod_entidade, razao_social, inscr_estadual from entidade where pessoa = 'P' and (inscr_estadual is not null or rg is null) and substr(regiao, 1, 2) = '" + UF + "'")
    entidades = cursor.fetchall()
    print '\n\nIE - Produtor - Deve ser IE normal\n'
    erros = 0
    for entidade in entidades:
        resultado = validar_ie(entidade[2], UF)
        if not resultado[0]:
            erros += 1
            print formatar_inteiro(erros, tamanho=4) + ': ' + ' ' * (18 - len(str(entidade[2]))) + str(entidade[2]) + ' - ' + formatar_inteiro(entidade[0], tamanho=5) + ' - ' + entidade[1]

    cursor.execute("select cod_entidade, razao_social, rg from entidade where pessoa = 'P' and inscr_estadual is null and substr(regiao, 1, 2) = '" + UF + "'")
    entidades = cursor.fetchall()
    print '\n\nIE - Produtor encontrada no RG, colocar no lugar correto - Deve ser IE normal\n'
    erros = 0
    for entidade in entidades:
        resultado = validar_ie(entidade[3], UF)
        if not resultado[0]:
            erros += 1
            print formatar_inteiro(erros, tamanho=4) + ': ' + ' ' * (18 - len(str(entidade[3]))) + str(entidade[3]) + ' - ' + formatar_inteiro(entidade[0], tamanho=5) + ' - ' + entidade[1]


# Converting and formating numbers e boolean values
CURRENCY = -1
BOOL_STRINGS = (('True', 'Yes', 'Y', _('True'), _('Yes'), _('T'), _('Y'), '1'), ('False', 'No', 'N', _('False'), _('No'), _('F'), _('N'), '0'))
DATE = 0
TIME = 1
DATE_TIME = 2
MONTH = 3
HOURS = 4
DAYS_HOURS = 5
HOLLERITH = 6
HOURS_MIN = 7
DAYS_HOURS_MIN = 8

# Julian Day delta from "-4713-11-24 12:00:00" to "0001-01-01 00:00:00"
JD = 1721425.5
JDTD = datetime.timedelta(JD)

try:  # Try to identify date and time formats via nl_langinfo
    TIME_FORMAT = locale.nl_langinfo(locale.T_FMT)
    DATE_FORMAT = re.sub('[^%a-zA-Z]', '/', locale.nl_langinfo(locale.D_FMT))
except Exception:  # If fail, like on Windows, try to discovery via strftime("%x")
    dh = datetime.datetime(2013, 12, 31, 11, 10, 30, 40)
    TIME_FORMAT = dh.strftime("%X").replace('11', '%H').replace('10', '%M').replace('30', '%S').replace('40', '%F')
    DATE_FORMAT = dh.strftime("%x").replace('2013', '%Y').replace('13', '%y').replace('12', '%m').replace('31', '%d')
    DATE_FORMAT = re.sub('[^%a-zA-Z]', '/', DATE_FORMAT)

# Create timezone - use: tz.localize(<datetime>)
try:
    import tzlocal
    tz = tzlocal.get_localzone()
except Exception:
    try:
        import pytz
        if os.path.exists('/etc/timezone'):
            tz = pytz.timezone(open('/etc/timezone').read().strip())
        else:
            tz = pytz.timezone('America/Sao_Paulo')
    except Exception:
        class America_Sao_Paulo_3(datetime.tzinfo):
            def __repr__(self):
                return 'America/Sao_Paulo'

            def tzname(self, dt):
                return '-03'

            def utcoffset(self, dt):
                return datetime.timedelta(-1, 75600)

            def dst(self, dt):
                return datetime.timedelta(0)

            def localize(self, dt):
                return dt.replace(tzinfo=self)
        tz = America_Sao_Paulo_3()


# Fix strftime < 1990
def strftime(date, format):
    if type(date) != datetime.time and date.year < 1900:
        year = date.year
        date = date.replace(year=9999)
        formated = date.strftime(format)
        if '9999' in formated:
            return formated.replace('9999', '%04i' % year)
        return formated.replace('99', '%02i' % (year % 100))
    return date.strftime(format)


def convert_and_format(content, return_type, decimals=locale.localeconv()['frac_digits'], bool_formated=(_('Y'), _('N')), bool_strings=BOOL_STRINGS):
    _("""Convert content into return_type and format it, returning a tuple
       within converted value (return_type) and fomated value (string).
       This function just accept int, bool, float and str in content and return_type.
       content is the content to be converted and formated.
       return_type is the type to convert content.
       decimals is valid just for float return type, specifying fracts digits or, if negative, currency formatation.
       bool_formated is valid just to bool return type, specifying a tuple with 2 strings, 'False' and 'True' by default.
    """)

    # Verifying type of content
    if content is None:
        content = ""
    elif type(content) not in (int, long, bool, float, str, unicode, datetime.date, datetime.time, datetime.datetime, datetime.timedelta):
        raise TypeError(_('Invalid argument "content" of type `%s´. Expected int, long, bool, float, str, date, time or datetime.') % (type(content).__name__,))

    # Pole types
    pole_type = None
    if type(return_type) in (str, unicode):
        if return_type not in tipos:
            raise TypeError(_('Invalid argument "return_type" like a value. Expected int, long, bool, float, str, date, time or datetime.'))
        tipo, tamanho, casas, cxopc, caracteres, mascara, padrao, alteravel, alinhamento = tipos[return_type]
        pole_type = return_type
        return_type = python_tipos[tipo]
        decimals = casas

    # Verifying type of return_type
    if type(return_type) != type and return_type not in (datetime.datetime, datetime.date, datetime.time, datetime.timedelta):
        raise TypeError(_('Invalid argument "return_type" like a value. Expected int, long, bool, float, str, date, time or datetime.'))

    # Verifying type of return_type
    if return_type not in (int, long, bool, float, str, unicode, datetime.date, datetime.time, datetime.datetime, datetime.timedelta):
        raise TypeError(_('Invalid argument "return_type" of type `%s´. Expected int, long, bool, float, str, date, time or datetime.') % (str(return_type).split("'")[1],))

    # Verifying type of decimals
    if return_type in (float, datetime.date, datetime.time, datetime.datetime, datetime.timedelta) and type(decimals) != int:
        raise TypeError(_('Invalid argument "decimals" of type `%s´. Expected int.') % (type(decimals).__name__,))

    # Verifying bool formated strings
    if return_type == bool:
        if type(bool_formated) not in (tuple, list):
            raise TypeError(_('Invalid argument "bool_formated" of type `%s´. Expected tuple or list.') % (type(bool_formated).__name__,))
        if len(bool_formated) != 2 or type(bool_formated[0]) not in (str, unicode) or type(bool_formated[1]) not in (str, unicode):
            raise ValueError(_('Invalid argument "bool_formated" specification `%s´. Expected a tuple or list within 2 strings.') % (repr(bool_formated),))
        if type(bool_strings) not in (tuple, list):
            raise TypeError(_('Invalid argument "bool_strings" of type `%s´. Expected tuple or list.') % (type(bool_strings).__name__,))
        if len(bool_strings) != 2 or type(bool_strings[0]) not in (tuple, list) or type(bool_strings[1]) not in (tuple, list):
            raise ValueError(_('Invalid argument "bool_strings" specification `%s´. Expected a tuple or list within 2 tuples or lists.') % (repr(bool_strings),))
        if len(bool_strings) != 2 or type(bool_strings[0]) not in (tuple, list) or type(bool_strings[1]) not in (tuple, list):
            raise ValueError(_('Invalid argument "bool_strings" specification `%s´. Expected a tuple or list within 2 tuples or lists.') % (repr(bool_strings),))
        if [s for s in bool_strings[0] + bool_strings[1] if type(s) not in (str, unicode)]:
            raise ValueError(_('Invalid argument "bool_strings" specification `%s´. Expected a tuple or list within 2 tuples or lists of strings.') % (repr(bool_strings),))

    # Adapting mascara to fmt for strftime
    if pole_type and isinstance(mascara, (str, unicode)):
        fmt = (mascara.replace('yyyy', '%Y').replace('yy', '%y').
               replace('mm', '%m').replace('dd', '%d').replace('z', '%z').
               replace('hh', '%H').replace('nn', '%M').replace('ss', '%S'))
        if 'T' not in fmt and ' ' not in fmt:
            if return_type == datetime.time:
                fmt = DATE_FORMAT + ' ' + fmt
            else:
                fmt += ' ' + TIME_FORMAT
    else:
        fmt = DATE_FORMAT + ' ' + TIME_FORMAT

    # Converting date and/or time content
    if type(content) in (datetime.datetime, datetime.date, datetime.time, datetime.timedelta) and return_type != datetime.timedelta:
        if return_type == bool:
            raise TypeError(_('Invalid return_type of type `bool´ when datetime content was specified.'))
        if return_type == datetime.date and type(content) == datetime.time:
            raise TypeError(_('Invalid return_type of type `date´ when `time´ content was specified.'))
        if return_type == datetime.time and type(content) == datetime.date:
            raise TypeError(_('Invalid return_type of type `time´ when `date´ content was specified.'))
        if return_type not in (int, long, float, datetime.timedelta):
            if return_type in (datetime.datetime, datetime.date) and decimals == MONTH:
                value = return_type(content.year, content.month, 1)
                if fmt[1] in ('Y', 'y'):
                    formated = strftime(value, fmt.split(' ')[0].split('T')[0][:5])
                else:
                    formated = strftime(value, fmt.split(' ')[0].split('T')[0][-5:])
            elif return_type == datetime.date or return_type == datetime.datetime and decimals == DATE:
                value = return_type(content.year, content.month, content.day)
                formated = strftime(value, fmt.split(' ')[0].split('T')[0])
            elif return_type == datetime.time or return_type == datetime.datetime and decimals in (TIME, HOURS, DAYS_HOURS, HOURS_MIN, DAYS_HOURS_MIN):
                if return_type == datetime.time:
                    value = datetime.time(content.hour, content.minute, content.second, content.microsecond, tzinfo=content.tzinfo)
                else:
                    value = datetime.datetime(1, 1, 1, content.hour, content.minute, content.second, content.microsecond, tzinfo=content.tzinfo)
                tfmt = fmt.split(' ')[1] if ' ' in fmt else fmt.split('T')[1]
                formated = strftime(content, tfmt)
                if decimals in (HOURS_MIN, DAYS_HOURS_MIN):
                    formated = ':'.join(formated.split(':')[:2])
            elif decimals in (HOURS, DAYS_HOURS, HOURS_MIN, DAYS_HOURS_MIN):
                if return_type == datetime.time:
                    value = datetime.time(content.hour, content.minute, content.second, content.microsecond)
                elif type(content) == datetime.time:
                    value = datetime.datetime(1, 1, 1, content.hour, content.minute, content.second, content.microsecond)
                else:
                    value = content
                if type(content) == datetime.time:
                    content = datetime.timedelta(hours=content.hour, minutes=content.minute, seconds=content.second, microseconds=content.microsecond)
                else:
                    content -= datetime.datetime(1, 1, 1)
                    content += JDTD
                formated = convert_and_format(content, datetime.timedelta, decimals)[1]
            else:
                if type(content) == datetime.time:
                    value = datetime.datetime(1, 1, 1, content.hour, content.minute, content.second, content.microsecond)
                elif type(content) == datetime.date:
                    value = datetime.datetime(content.year, content.month, content.day)
                else:
                    value = content
                formated = strftime(value, fmt)
            if formated[-1:] == ':':  # timezone
                formated = formated[:-3] + ':' + formated[-3:-1]
            if return_type == str:
                return (formated, formated)
            return [value, formated]
        if type(content) == datetime.date:
            delta = datetime.datetime(content.year, content.month, content.day) - datetime.datetime(1, 1, 1) + JDTD
        elif type(content) == datetime.timedelta:
            delta = content + JDTD
        elif type(content) == datetime.time:
            delta = datetime.datetime(1, 1, 1, content.hour, content.minute, content.second, content.microsecond) - datetime.datetime(1, 1, 1) + JDTD
        else:
            delta = content - datetime.datetime(1, 1, 1, tzinfo=content.tzinfo) + JDTD
        if return_type == datetime.timedelta:
            content = delta
        elif return_type == int:
            content = (delta + datetime.timedelta(.5)).days
        else:
            content = delta.days + (delta.seconds + delta.microseconds / 1000000.) / 86400  # (24*60*60)

    # Formating date and/or time outputs
    if return_type in (datetime.datetime, datetime.date, datetime.time):
        first = fmt[1]
        if type(content) in (str, unicode):  # vide locale format with locale.nl_langinfo(locale.D_FMT)
            content = content.strip()
            if not content:
                return [return_type(0) if return_type == datetime.time
                        else return_type(1, 1, 1), '']
            now = datetime.datetime.now()
            if ' ' in content:
                date, hour = content.split(' ', 1)
            elif 'T' in content:
                date, hour = content.split('T', 1)
            elif return_type == datetime.time or return_type == datetime.datetime and decimals in (TIME, HOURS, DAYS_HOURS, HOURS_MIN, DAYS_HOURS_MIN):
                hour = content
                date = ''
            else:
                date = content
                hour = ''
            date = re.sub('[^0-9]+', '/', date)
            hour = re.sub('[^0-9]+', ':', hour)
            year, mon, day = (1, 1, 1)
            if date.isdigit():
                if decimals == MONTH:
                    date = date[:6 if 'Y' in fmt else 4]
                    day = 1
                    if first in 'Yy':
                        mon = int(date[-2:])
                        year = date[:-2] if len(date) > 2 else now.year
                    else:
                        mon = int(date[:2])
                        year = date[2:] if len(date) > 2 else now.year
                else:
                    date = date[:8 if 'Y' in fmt else 6]
                    if first in 'Yy':
                        day = int(date[-2:])
                        mon = int(date[-4:-2]) if len(date) > 2 else now.month
                        year = date[:-4] if len(date) > 4 else now.year
                    else:
                        if first == 'm':
                            day = int(date[2:4] if len(date) > 2 else date[:2])
                            mon = int(date[:2]) if len(date) > 2 else now.month
                        else:
                            day = int(date[:2])
                            mon = (int(date[2:4]) if len(date) > 2
                                   else now.month)
                        year = date[4:] if len(date) > 4 else now.year
            elif len(date) > 0:
                date = date.split('/')
                if decimals == MONTH:
                    date = date[:2]
                    day = 1
                    if first in 'Yy':
                        mon = int(date[-1])
                        year = date[0] if len(date) > 1 else now.year
                    else:
                        mon = int(date[0])
                        year = date[1] if len(date) > 1 else now.year
                else:
                    date = date[:3]
                    if first in 'Yy':
                        day = int(date[-1])
                        mon = int(date[-2]) if len(date) > 1 else now.month
                        year = date[-3] if len(date) > 2 else now.year
                    else:
                        if first == 'm':
                            day = int(date[1] if len(date) > 1 else date[0])
                            mon = int(date[0]) if len(date) > 1 else now.month
                        else:
                            day = int(date[0])
                            mon = int(date[1]) if len(date) > 1 else now.month
                        year = date[2] if len(date) > 2 else now.year
            if type(year) in (str, unicode):
                x = int(10 ** len(year))
                year = now.year // x * x + int(year)
            if day > 31:
                day = 31
            elif day == 0:
                day = 1
            if mon > 12:
                mon = 12
            elif mon == 0:
                mon = 1
            h = m = s = 0
            if hour.isdigit():
                h = int(hour[:2])
                if len(hour) > 2:
                    m = int(hour[2:4])
                    if len(hour) > 4:
                        s = int(hour[4:6])
            elif len(hour) > 0:
                hour = hour.split(':')
                h = int(hour[0])
                m = int(hour[1])
                if len(hour) > 2:
                    s = int(hour[2])
            try:
                date = datetime.date(year, mon, day)
            except ValueError:
                try:
                    date = datetime.date(year, mon, day - 1)
                except ValueError:
                    try:
                        date = datetime.date(year, mon, day - 2)
                    except ValueError:
                        date = datetime.date(year, mon, day - 3)
            date = datetime.datetime(date.year, date.month, date.day, h, m, s)
            # delta = date - datetime.datetime(1, 1, 1)
            if decimals == MONTH and return_type in (datetime.datetime, datetime.date):
                if return_type == datetime.date:
                    date = date.date()
                if first in ('Y', 'y'):
                    return [date, strftime(date, fmt.split(' ')[0].split('T')[0][:5])]  # was delta.days
                return [date, strftime(date, fmt.split(' ')[0].split('T')[0][-5:])]  # was delta.days
            if return_type == datetime.date or return_type == datetime.datetime and decimals == 0:
                if return_type == datetime.date:
                    date = date.date()
                return [date, strftime(date, fmt.split(' ')[0].split('T')[0])]  # was delta.days
            # value = delta.days + (delta.seconds + delta.microseconds / 1000000.)/(24*60*60)
            if return_type == datetime.time or return_type == datetime.datetime and decimals in (TIME, HOURS, DAYS_HOURS, HOURS_MIN, DAYS_HOURS_MIN):
                if return_type == datetime.time:
                    date = date.time()
                tfmt = fmt.split(' ')[1] if ' ' in fmt else fmt.split('T')[1]
                formated = strftime(date, tfmt)
                if decimals in (HOURS_MIN, DAYS_HOURS_MIN):
                    formated = ':'.join(formated.split(':')[:2])
                return [date, formated]  # was value - int(value)
            # if return_type == datetime.datetime:
            return [date, strftime(date, fmt)]  # was value
        elif type(content) in (int, long, float, datetime.timedelta):
            if type(content) == datetime.timedelta:
                date = datetime.datetime(1, 1, 1) + (content - JDTD)
            else:
                d = int(content)
                s = int((content-d) * 86400)
                u = int(((content-d) * 86400 - s) * 1000000)
                date = datetime.datetime(1, 1, 1) + (datetime.timedelta(d, s, u) - JDTD)
            h = date.hour
            m = date.minute
            s = date.second
            if decimals == MONTH and return_type in (datetime.datetime, datetime.date):
                if return_type == datetime.date:
                    date = date.date()
                if first in ('Y', 'y'):
                    return [date, strftime(date, fmt.split(' ')[0].split('T')[0][:5])]
                return (date, strftime(date, fmt.split(' ')[0].split('T')[0][-5:]))
            if return_type == datetime.date or return_type == datetime.datetime and decimals == DATE:
                if return_type == datetime.date:
                    date = date.date()
                return [date, strftime(date, fmt.split(' ')[0].split('T')[0])]
            if return_type == datetime.time or return_type == datetime.datetime and decimals in (TIME, HOURS, DAYS_HOURS, HOURS_MIN, DAYS_HOURS_MIN):
                if return_type == datetime.time:
                    date = date.time()
                tfmt = fmt.split(' ')[1] if ' ' in fmt else fmt.split('T')[1]
                formated = strftime(date, tfmt)
                if decimals in (HOURS_MIN, DAYS_HOURS_MIN):
                    formated = ':'.join(formated.split(':')[:2])
                return [date, formated]
            # if return_type == datetime.datetime:
            return [date, strftime(date, fmt)]
        raise TypeError('Content type `' + str(type(content)).split("'")[1] + '´ can\'t be converted to datetime, date or time.')

    # Converting numeric content
    if type(content) in (int, long, bool, float):
        if return_type == int:
            value = int(round(content))
        elif return_type == long:
            value = long(round(content))
        else:
            value = return_type(content)

    # Converting str content with locale support
    elif return_type in (float, int, long):
        p, n = content.find('+'), content.find('-')
        decimal = locale.localeconv()['decimal_point']
        content = re.sub('[^0-9%s]' % decimal, '', content)
        i = content.find(decimal) + 1
        content = content[:i] + content[i:].replace(decimal, '')
        if not content or content == 'decimal':
            return [-sys.maxint-1 if return_type in (int, long)
                    else float('-inf'), '']
        signal = '+0' if n == -1 or p > -1 and p < n else '-0'
        content = signal + content
        value = 0. if not content else locale.atof(content)
        if return_type != float:
            value = return_type(round(value))
    elif return_type == bool:
        bs_up = [[i.upper() for i in bool_strings[0]], [i.upper() for i in bool_strings[1]]]
        if content.upper() in bs_up[0] + bs_up[1]:
            value = (content.upper() in bs_up[0])
            return [value, content]
        else:
            value = bool(locale.atof(content)) if content else False
    else:
        value = content  # .strip()  # Retirar espaços é uma boa?

    # Formating Pole Type
    if pole_type:
        formated = formatar(content, pole_type)

    # Formating with locale support
    elif return_type == datetime.timedelta:
        if value and isinstance(value, (str, unicode)):
            neg = value[0] == '-' * -1
            if ' ' in value:
                days, value = value[-neg:].split(' ', 1)
                days = neg * int(days)
                value = [neg * int(y) for y in (value + ':00:00').split(':')]
            else:
                days = 0
                value = [neg * int(y)
                         for y in (value[-neg:] + ':00:00').split(':')]
                hours, minutes, seconds = value[:3]
            value = datetime.timedelta(days=days, hours=hours,
                                       minutes=minutes, seconds=seconds)
        else:
            if not value:
                value = datetime.timedelta(0)
            seconds = value.days * 86400 + value.seconds
            neg = -1 if seconds < 0 else 1
            seconds *= neg
            days = seconds / 86400
            seconds %= 86400
            hours = seconds / 3600
            minutes = (seconds % 3600) / 60
            seconds %= 60
        if decimals == DAYS_HOURS:
            formated = '%i %02i:%02i:%02i' % (days, hours, minutes, seconds)
        elif decimals == DAYS_HOURS_MIN:
            formated = '%i %02i:%02i' % (days, hours, minutes)
        elif decimals == HOURS_MIN:
            formated = '%02i:%02i' % (days * 24 + hours, minutes)
        else:
            formated = '%02i:%02i:%02i' % (days * 24 + hours, minutes, seconds)
        if neg == -1:
            formated = '-' + formated
    elif return_type == float:
        if decimals < 0:
            formated = locale.currency(value, True, True)
        else:
            formated = locale.format('%.' + str(decimals) + 'f', value, True, True)
    elif return_type in (int, long):
        formated = locale.format('%i', value, True, True)
    elif return_type == bool:
        formated = bool_formated[1 - value]
    else:
        formated = value

    # Returning value and formated string
    return [value, formated]


cf = convert_and_format
VALUE = 0
STRING = 1


def add_days(date, days):
    return date + datetime.timedelta(days)


def add_months(date, months):
    day = date.day
    month = (date.month + months) % 12
    if month == 0:
        month = 12
    year = date.year + (date.month + months - 1) / 12
    if month in (4, 6, 9, 11) and day > 30:
        return date.replace(year=year, month=month, day=30)
    if month == 2 and day > 28:
        try:
            return date.replace(year=year, month=month, day=29)
        except ValueError:
            return date.replace(year=year, month=month, day=28)
    return date.replace(year=year, month=month)


def last_day(date):
    if isinstance(date, datetime.datetime):
        return_type = datetime.datetime
    else:
        return_type = datetime.date
        date = convert_and_format(date, return_type)[0]
    if date.month in (1, 3, 5, 7, 8, 10, 12):
        date = date.replace(day=31)
    elif date.month in (4, 6, 9, 11):
        date = date.replace(day=30)
    else:
        try:
            date = date.replace(day=29)
        except ValueError:
            date = date.replace(day=28)
    return date


def get_printers(server='localhost'):
    printers = []
    if sys.platform == 'cli':
        PoleLog.log(_('It is not possible get printers from %s plataform or operating system.' % sys.platform))
    else:
        import os
        import subprocess
        # chose an implementation, depending on os
        if os.name == 'posix':
            printers = [line.split()[0] for line in subprocess.Popen("lpstat -h '%s' -a" % server, shell=True, bufsize=1024, stdout=subprocess.PIPE).stdout.read().strip().split('\n')]
            try:
                default = subprocess.Popen("lpstat -h '%s' -d" % server, shell=True, bufsize=1024, stdout=subprocess.PIPE).stdout.read().strip().split()[-1]
                printers.remove(default)
                printers.insert(0, default)
            except Exception:
                pass
        elif os.name == 'nt':  # sys.platform == 'win32':
            PoleLog.log(_('It is not possible get printers from %s plataform or operating system.' % os.name))
        elif os.name == 'java':
            PoleLog.log(_('It is not possible get printers from %s plataform or operating system.' % os.name))
        else:
            PoleLog.log(_('It is not possible get printers from %s plataform or operating system.' % os.name))
    return printers


def print_file(printer, file, title=None, server='localhost', raw=False):
    if title is None:
        title = file.rsplit('/', 1)[-1]
    return print_str(printer, open(file).read(), title, server, raw)


def print_str(printer, string, title=None, server='localhost', raw=True):
    if sys.platform == 'cli':
        PoleLog.log(_('It is not possible get printers from %s plataform or operating system.' % sys.platform))
    else:
        import os
        import subprocess
        if title is None:
            title = 'Desconhecido'
        # chose an implementation, depending on os
        if os.name == 'posix':
            process = subprocess.Popen("lp -h '%s' -d '%s' -t '%s'%s" % (server, printer, title, ('', ' -o raw')[raw]), shell=True, bufsize=1024, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            process.stdin.write(string)
            process.stdin.close()
            return (process.stdout.read(), process.stderr.read())
        elif os.name == 'nt':  # sys.platform == 'win32':
            PoleLog.log(_('It is not possible get printers from %s plataform or operating system.' % os.name))
        elif os.name == 'java':
            PoleLog.log(_('It is not possible get printers from %s plataform or operating system.' % os.name))
        else:
            PoleLog.log(_('It is not possible get printers from %s plataform or operating system.' % os.name))
    return None


# Possíveis caracters a digitar
cs = {
    "acentuados"       : "ãàáâéêíõóôúüçäëïöñèìòùîûýÿåæ"
                         "ÃÀÁÂÉÊÍÕÓÔÚÜÇÄËÏÖÑÈÌÒÙÎÛÝŸÅÆªº",
    "desacentuados"    : "aaaaeeiooouucaeioneiouiuyyaa"
                         "AAAAEEIOOOUUCAEIONEIOUIUYYAAao",
    "letras maiúsculas": "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                         "ÃÀÁÂÉÊÍÕÓÔÚÜÇÄËÏÖÑÈÌÒÙÎÛÝŸÅÆ",
    "letras minúsculas": "abcdefghijklmnopqrstuvwxyz"
                         "ãàáâéêíõóôúüçäëïöñèìòùîûýÿåæ",
    "letras"           : "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                         "ÃÀÁÂÉÊÍÕÓÔÚÜÇÄËÏÖÑÈÌÒÙÎÛÝŸÅÆ"
                         "abcdefghijklmnopqrstuvwxyz"
                         "ãàáâéêíõóôúüçäëïöñèìòùîûýÿåæ",
    "letras e números" : "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                         "ÃÀÁÂÉÊÍÕÓÔÚÜÇÄËÏÖÑÈÌÒÙÎÛÝŸÅÆ"
                         "abcdefghijklmnopqrstuvwxyz"
                         "ãàáâéêíõóôúüçäëïöñèìòùîûýÿåæ0123456789",
    "números"          : "0123456789",
    "rg"               : "0123456789-.xX",
    "data"             : "0123456789/hHdDsSmMaA",
    "hora"             : "0123456789:aAhHmMsSdD",
    "data e hora"      : "0123456789/:hHdDsSmMaA",
    "url"              : "abcdefghijklmnopqrstuvwxyz@./:_-?&\\0123456789"
                         "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "email"            : "abcdefghijklmnopqrstuvwxyz@._-0123456789"
                         "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "nome"             : "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                         "ÃÀÁÂÉÊÍÕÓÔÚÜÇÄËÏÖÑÈÌÒÙÎÛÝŸÅÆ"
                         "abcdefghijklmnopqrstuvwxyz"
                         "ãàáâéêíõóôúüçäëïöñèìòùîûýÿåæ ",
    "razão social"     : "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                         "ÃÀÁÂÉÊÍÕÓÔÚÜÇÄËÏÖÑÈÌÒÙÎÛÝŸÅÆ"
                         "abcdefghijklmnopqrstuvwxyz"
                         "ãàáâéêíõóôúüçäëïöñèìòùîûýÿåæ 0123456789.,&_-",
    "ordenação"        : "#$&()[]{}<«»>^*/\\:+-±=~_`'\",;.!?|@¼½¾°¹²³ªº%"
                         "0123456789AaÀàÁáÂâÃãÄäÅåÆæBbCcÇçDdEeÈèÉéÊêËëFfGgHh"
                         "IiÌìÍíÎîÏïJjKkLlMmNnÑñOoÒòÓóÔôÕõÖöPpQqRrSsTt"
                         "UuÙùÚúÛûÜüVvWwXxYyÝýŸÿZz"
}

# Opções a escolher
ops = {
    "Estado Civil"   : [["Cód.", "Est.Civil"], ["1", "Amaziado"],
                        ["2", "Casado"], ["3", "Desquitado"],
                        ["4", "Divorciado"], ["5", "Separado"],
                        ["6", "Solteiro"], ["7", "Viúvo"]],
    "Estados"        : [["Sigla", "Extenso"], ['AC', 'Acre'],
                        ['AL', 'Alagoas'], ['AM', 'Amazonas'], ['AP', 'Amapá'],
                        ['BA', 'Bahia'], ['CE', 'Ceará'],
                        ['DF', 'Distrito Federal'], ['ES', 'Espírito Santo'],
                        ['EX', 'Exterior'], ['GO', 'Goiás'], ['MA', 'Maranhão'],
                        ['MG', 'Minas Gerais'], ['MS', 'Mato Grosso do Sul'],
                        ['MT', 'Mato Grosso'], ['PA', 'Pará'],
                        ['PB', 'Paraíba'], ['PE', 'Pernambuco'],
                        ['PI', 'Piauí'], ['PR', 'Paraná'],
                        ['RJ', 'Rio de Janeiro'],
                        ['RN', 'Rio Grande do Norte'], ['RO', 'Rondônia'],
                        ['RR', 'Roraima'], ['RS', 'Rio Grande do Sul'],
                        ['SC', 'Santa Catarina'], ['SE', 'Sergipe'],
                        ['SP', 'São Paulo'], ['TO', 'Tocantins']],
    "Pele"           : [["Cód.", "Cor"], ["1", "Amarela"], ["2", "Branca"],
                        ["3", "Negra"], ["4", "Parda"], ["5", "Vermelha"]],
    "Excelência"     : [["Cód.", "Excelência"], ["5", "Excelente"],
                        ["4", "Bom"], ["3", "Razoável"],
                        ["2", "Ruim"], ["1", "Péssimo"]],
    "Pertinência"    : [["Cód.", "Pertinência"], ["0", "Sem"], ["1", "Pouco"],
                        ["2", "Moderado"], ["3", "Muito"]],
    "Sexo"           : [["S", "Sexo"], ["M", "Masculino"], ["F", "Feminino"]],
    "Semana"         : [["Abrev.", "Num.", "Extenso"], ["Dom", "1", "Domingo"],
                        ["Seg", "2", "Segunda"], ["Ter", "3", "Terça"],
                        ["Qua", "4", "Quarta"], ["Qui", "5", "Quinta"],
                        ["Sex", "6", "Sexta"], ["Sáb", "7", "Sábado"]],
    "Mês"            : [["Abrev.", "Num.", "Extenso"],
                        ["Jan", "01", "Janeiro"], ["Fev", "02", "Fevereiro"],
                        ["Mar", "03", "Março"], ["Abr", "04", "Abril"],
                        ["Mai", "05", "Maio"], ["Jun", "06", "Junho"],
                        ["Jul", "07", "Julho"], ["Ago", "08", "Agosto"],
                        ["Set", "09", "Setembro"], ["Out", "10", "Outubro"],
                        ["Nov", "11", "Novembro"], ["Dez", "12", "Dezembro"]],
    "Sim ou Não"     : [["O", "Opc."], ["S", "Sim"], ["N", "Não"]],
    "Pessoa"         : [["P", "Pessoa"], ["F", "Física"], ["J", "Jurídica"],
                        ["P", "Produtor"]],
    "Tipo Logradouro": [["Tipo", "Descrição"], [" ", "Nulo"], ["A", "Área"],
                        ["AC", "Acesso"], ["ACAMP", "Acampamento"],
                        ["AD", "Adro"], ["AE", "Área Especial"],
                        ["AER", "Aeroporto"], ["AL", "Alameda"],
                        ["ART", "Artéria"], ["AT", "Alto"], ["ATL", "Atalho"],
                        ["AV", "Avenida"], ["AV-CONT", "Avenida Contorno"],
                        ["BAL", "Balneário"], ["BC", "Beco"],
                        ["BCO", "Buraco"], ["BELV", "Belvedere"],
                        ["BL", "Bloco"], ["BLO", "Balão"], ["BSQ", "Bosque"],
                        ["BVD", "Boulevard"], ["BX", "Baixa"], ["C", "Cais"],
                        ["CALC", "Calcada"], ["CAM", "Caminho"],
                        ["CAN", "Canal"], ["CHAP", "Chácara"],
                        ["CHAP", "Chapadão"], ["CIRC", "Circular"],
                        ["CJ", "Conjunto"], ["CMP-VR", "Complexo Viário"],
                        ["COL", "Colônia"], ["COND", "Condomínio"],
                        ["COR", "Corredor"], ["CPO", "Campo"],
                        ["CRG", "Córrego"], ["CXP", "Caixa Postal"],
                        ["DSC", "Descida"], ["DSV", "Desvio"],
                        ["DT", "Distrito"], ["ENT-PART", "Entrada Particular"],
                        ["EQ", "Entre Quadra"], ["ESC", "Escada"],
                        ["ESP", "Esplanada"], ["EST", "Estrada"],
                        ["ESTC", "Estacionamento"],
                        ["EST-MUN", "Estrada Municipal"], ["ETC", "Estação"],
                        ["ETD", "Estádio"], ["ETN", "Estância"],
                        ["EVD", "Elevada"], ["FAV", "Favela"],
                        ["FAZ", "Fazenda"], ["FER", "Ferrovia"],
                        ["FNT", "Fonte"], ["FRA", "Feira"],
                        ["FTE", "Forte"], ["GAL", "Galeria"],
                        ["GJA", "Granja"], ["HAB", "Habitacional"],
                        ["IA", "Ilha"], ["JD", "Jardim"], ["JDE", "Jardinete"],
                        ["LD", "Ladeira"], ["LG ", "Lago"], ["LGA", "Lagoa"],
                        ["LOT", "Loteamento"], ["LRG", "Largo"],
                        ["MNA", "Marina"], ["MOD", "Modulo"], ["MRO", "Morro"],
                        ["MTE", "Monte"], ["NUC", "Núcleo"],
                        ["PAR", "Paralela"], ["PAS", "Passeio"],
                        ["PAT", "Pátio"], ["PC", "Praça"],
                        ["PC-ESP", "Praça de Esportes"], ["PDA", "Parada"],
                        ["PDO", "Paradouro"], ["PNT", "Ponta"],
                        ["PR", "Praia"], ["PRL", "Prolongamento"],
                        ["PRQ", "Parque"], ["PSA", "Passarela"],
                        ["PSC-SUB", "Passagem Subterrânea"],
                        ["PSG", "Passagem"], ["PTE", "Ponte"],
                        ["PTO", "Porto"], ["Q", "Quadra"], ["QTA", "Quinta"],
                        ["QTAS", "Quinta"], ["R", "Rua"], ["RAM", "Ramal"],
                        ["REC", "Recanto"], ["RER", "Retiro"],
                        ["RES", "Residencial"], ["RET", "Reta"],
                        ["R-LIG", "Rua de Ligação"], ["RMP", "Rampa"],
                        ["ROD", "Rodovia"], ["ROD-AN", "Rodo Anel"],
                        ["ROT", "Rótula"], ["R-PED", "Rua de Pedestre"],
                        ["RTN", "Retorno"], ["RTT", "Rotatória"],
                        ["SIT", "Sítio"], ["SRV", "Servidão"],
                        ["ST", "Setor"], ["SUB", "Subida"],
                        ["TCH", "Trincheira"], ["TER", "Terminal"],
                        ["TRV", "Trecho"], ["TRV", "Trevo"], ["TUN", "Túnel"],
                        ["TV", "Travessa"], ["TV-PART", "Travessa Particular"],
                        ["UNID", "Unidade"], ["V", "Via"],
                        ["V-AC", "Via de Acesso"], ["VAL", "Vala"],
                        ["VD", "Viaduto"], ["VER", "Vereda"],
                        ["V-EVD", "Via Elevado"], ["V-EXP", "Via Expressa"],
                        ["VL", "Vila"], ["VLA", "Viela"], ["VLE", "Vale"],
                        ["V-PED", "Via de Pedestre"], ["VRTE", "Variante"],
                        ["ZIG-ZAG", "Zigue-Zague"]],
    "Clima"          : [["Clima"], ["Chuva"], ["Geada"], ["Nublado"],
                        ["Sol"], ["Tempestade"]],
    "Crédito Débito" : [["C/D", "Descrição"],
                        ["C", "Crédito"], ["D", "Débito"]],
    "Consistência"   : [["Campo Importado"], ["Diferente"], ["Entre"],
                        ["Maior ou igual a"], ["Maior que"],
                        ["Menor ou igual a"], ["Menor que"],
                        ["No conjunto"], ["Sem"]],
}

# Possíveis tipos para os bancos de dados
python_tipos = [None  , str       , None  , long     , None  , None  , float   , None  , None  , datetime.date, datetime.time, datetime.datetime, bool     , None  , long]
mysql_tipos  = [''    , 'varchar' , ''    , 'integer', ''    , ''    , 'float' , ''    , ''    , 'date'       , 'time'       , 'datetime'       , 'char'   , ''    , 'integer']
ora_tipos    = [''    , 'varchar2', ''    , 'number' , ''    , ''    , 'number', ''    , ''    , 'date'       , 'date'       , 'date'           , 'char'   , ''    , 'number']
sqlite_tipos = ['null', 'text'    , 'null', 'integer', 'null', 'null', 'real'  , 'null', 'null', 'real'       , 'real'       , 'real'           , 'integer', 'null', 'integer']


def mascara_dinheiro(casas=None, localization='',
                     internacional=False, negativo=True):
    if localization != '':
        locale.setlocale(locale.LC_ALL, localization)
    localx = locale.localeconv()
    if localization != '':
        locale.setlocale(locale.LC_ALL, '')
    moeda = (localx['int_curr_symbol'] if internacional
             else localx['currency_symbol'])
    spp = ' ' * localx['p_sep_by_space']
    spn = ' ' * localx['n_sep_by_space']
    ps = localx['positive_sign']
    ns = localx['negative_sign']
    if casas and type(casas) == int:
        casas = '0' * casas
    else:
        casas = '0' * (localx['int_frac_digits'] if internacional
                       else localx['frac_digits'])
    if negativo:
        return (moeda + spp + ps + "0." + casas + ",;" +
                moeda + spn + ns + "0." + casas + ",;" +
                moeda + spp + ps + "0." + casas)
    return (moeda + spp + ps + "0." + casas + ",;" +
            moeda + spp + ps + "0." + casas + ",;" +
            moeda + spp + ps + "0." + casas)


# Tipos
fd = local['frac_digits']
fs = '0.' + '0' * fd
dp = local['decimal_point']
T = namedtuple('Tipo', 'tipo tamanho casas combo caracteres mascara'
                       ' padrao alteravel alinhamento')

tipos = {
    # Nome                                          Tipo    Tamanho Casas  CxOpç  Caracteres                    Máscara 0 => obrigatório    # => opcional                       Padrao  Alterável Alinhamento
    "CEP"                                     : T(     1,         8,    0, False, cs["números"]               , "00'.'000-000;00'.'000-000;#"                                  ,     1, 0,        100),
    "CFOP"                                    : T(     1,         4,    0, False, cs["números"] + '.'         , ""                                                             ,     1, 1,        100),
    "CNPJ"                                    : T(     1,        14,    0, False, cs["números"]               , "00'.'000'.'000/0000-00;00'.'000'.'000/0000-00;#"              ,     1, 0,        100),
    "CNPJ Números"                            : T(     1,        14,    0, False, cs["números"]               , "00000000000000;00000000000000;#"                              ,     1, 0,        100),
    "Clima"                                   : T(     1,        10,    0,  True, ""                          , ops["Clima"]                                                   ,     1, 0,          0),
    "CNH"                                     : T(     1,        11,    0, False, cs["números"]               , "00000000000,;00000000000,;#"                                  ,     1, 0,        100),
    "Cód. Barras"                             : T(     1,       128,    0, False, ""                          , ""                                                             ,     1, 1,        100),
    "Cód. Barras EAN13"                       : T(     1,        13,    0, False, cs["números"]               , "0000000000000;0000000000000;#"                                ,     1, 0,        100),
    "CPF"                                     : T(     1,        11,    0, False, cs["números"]               , "000'.'000'.'000-00;000'.'000'.'000-00;#"                      ,     1, 0,        100),
    "CPF Números"                             : T(     1,        11,    0, False, cs["números"]               , "00000000000;00000000000;00000000000"                          ,     1, 0,        100),
    "Crédito ou Débito"                       : T(     1,         1,    0,  True, ""                          , ops["Crédito Débito"]                                          ,     1, 0,         50),
    "Data"                                    : T(     9,        10,    0, False, cs["data"]                  , "dd/mm/yyyy"                                                   ,     1, 0,         50),
    "Data 2"                                  : T(     9,         8,    0, False, cs["data"]                  , "dd/mm/yy"                                                     ,     1, 0,         50),
    "Data e Hora"                             : T(    11,        19,    2, False, cs["data e hora"]           , "dd/mm/yyyy hh:nn:ss"                                          ,     1, 0,         50),
    "Data e Hora 2"                           : T(    11,        19,    2, False, cs["data e hora"]           , "dd/mm/yyyy hh:nn"                                             ,     1, 0,         50),
    "Data 2 e Hora"                           : T(    11,        17,    2, False, cs["data e hora"]           , "dd/mm/yy hh:nn:ss"                                            ,     1, 0,         50),
    "Data 2 e Hora 2"                         : T(    11,        17,    2, False, cs["data e hora"]           , "dd/mm/yy hh:nn"                                               ,     1, 0,         50),
    "Data e Hora Zona"                        : T(    11,        19,    2, False, cs["data e hora"]           , "dd/mm/yyyy hh:nn:ss z"                                        ,     1, 0,         50),
    "Data e Hora 2 Zona"                      : T(    11,        19,    2, False, cs["data e hora"]           , "dd/mm/yyyy hh:nn z"                                           ,     1, 0,         50),
    "Data 2 e Hora Zona"                      : T(    11,        17,    2, False, cs["data e hora"]           , "dd/mm/yy hh:nn:ss z"                                          ,     1, 0,         50),
    "Data 2 e Hora 2 Zona"                    : T(    11,        17,    2, False, cs["data e hora"]           , "dd/mm/yy hh:nn z"                                             ,     1, 0,         50),
    "Data SPED"                               : T(     9,         8,    0, False, cs["data"]                  , "ddmmyyyy"                                                     ,     1, 0,         50),
    "Data 2 SPED"                             : T(     9,         6,    0, False, cs["data"]                  , "ddmmyy"                                                       ,     1, 0,         50),
    "Data e Hora SPED"                        : T(    11,        14,    2, False, cs["data e hora"]           , "ddmmyyyyhhnnss"                                               ,     1, 0,         50),
    "Data e Hora 2 SPED"                      : T(    11,        14,    2, False, cs["data e hora"]           , "ddmmyyyyhhnn"                                                 ,     1, 0,         50),
    "Data 2 e Hora SPED"                      : T(    11,        12,    2, False, cs["data e hora"]           , "ddmmyyhhnnss"                                                 ,     1, 0,         50),
    "Data 2 e Hora 2 SPED"                    : T(    11,        12,    2, False, cs["data e hora"]           , "ddmmyyhhnn"                                                   ,     1, 0,         50),
    "Data XML"                                : T(     9,        10,    0, False, cs["data"]                  , "yyyy-mm-dd"                                                   ,     1, 0,         50),
    "Data 2 XML"                              : T(     9,         8,    0, False, cs["data"]                  , "yy-mm-dd"                                                     ,     1, 0,         50),
    "Data e Hora XML"                         : T(    11,        19,    2, False, cs["data e hora"] + 'T'     , "yyyy-mm-ddThh:nn:ss"                                          ,     1, 0,         50),
    "Data e Hora 2 XML"                       : T(    11,        19,    2, False, cs["data e hora"] + 'T'     , "yyyy-mm-ddThh:nn"                                             ,     1, 0,         50),
    "Data 2 e Hora XML"                       : T(    11,        17,    2, False, cs["data e hora"] + 'T'     , "yy-mm-ddThh:nn:ss"                                            ,     1, 0,         50),
    "Data 2 e Hora 2 XML"                     : T(    11,        17,    2, False, cs["data e hora"] + 'T'     , "yy-mm-ddThh:nn"                                               ,     1, 0,         50),
    "Data e Hora Zona XML"                    : T(    11,        19,    2, False, cs["data e hora"] + 'T'     , "yyyy-mm-ddThh:nn:ssz:"                                        ,     1, 0,         50),
    "Data e Hora 2 Zona XML"                  : T(    11,        19,    2, False, cs["data e hora"] + 'T'     , "yyyy-mm-ddThh:nnz:"                                           ,     1, 0,         50),
    "Data 2 e Hora Zona XML"                  : T(    11,        17,    2, False, cs["data e hora"] + 'T'     , "yy-mm-ddThh:nn:ssz:"                                          ,     1, 0,         50),
    "Data 2 e Hora 2 Zona XML"                : T(    11,        17,    2, False, cs["data e hora"] + 'T'     , "yy-mm-ddThh:nnz:"                                             ,     1, 0,         50),
    "Dinheiro"                                : T(     6,        14,    0, False, cs["números"] + dp + '+-'   , mascara_dinheiro()                                             ,     1, 0,        100),
    "Dinheiro 1"                              : T(     6,        14,    1, False, cs["números"] + dp + '+-'   , mascara_dinheiro(1)                                            ,     1, 0,        100),
    "Dinheiro 2"                              : T(     6,        14,    2, False, cs["números"] + dp + '+-'   , mascara_dinheiro(2)                                            ,     1, 0,        100),
    "Dinheiro 3"                              : T(     6,        14,    3, False, cs["números"] + dp + '+-'   , mascara_dinheiro(3)                                            ,     1, 0,        100),
    "Dinheiro 4"                              : T(     6,        14,    4, False, cs["números"] + dp + '+-'   , mascara_dinheiro(4)                                            ,     1, 0,        100),
    "Dinheiro 5"                              : T(     6,        14,    5, False, cs["números"] + dp + '+-'   , mascara_dinheiro(5)                                            ,     1, 0,        100),
    "Dinheiro Positivo"                       : T(     6,        14,    0, False, cs["números"] + dp          , mascara_dinheiro(negativo=False)                               ,     1, 0,        100),
    "Dinheiro 1 Positivo"                     : T(     6,        14,    1, False, cs["números"] + dp          , mascara_dinheiro(1, negativo=False)                            ,     1, 0,        100),
    "Dinheiro 2 Positivo"                     : T(     6,        14,    2, False, cs["números"] + dp          , mascara_dinheiro(2, negativo=False)                            ,     1, 0,        100),
    "Dinheiro 3 Positivo"                     : T(     6,        14,    3, False, cs["números"] + dp          , mascara_dinheiro(3, negativo=False)                            ,     1, 0,        100),
    "Dinheiro 4 Positivo"                     : T(     6,        14,    4, False, cs["números"] + dp          , mascara_dinheiro(4, negativo=False)                            ,     1, 0,        100),
    "Dinheiro 5 Positivo"                     : T(     6,        14,    5, False, cs["números"] + dp          , mascara_dinheiro(5, negativo=False)                            ,     1, 0,        100),
    "EAN-13 formatado"                        : T(     1,        11,    0, False, cs["números"]               , "000'.'00000'.'00'.'000-0;000'.'00000'.'00'.'000-0;"           ,     1, 0,        100),
    "E-mail"                                  : T(     1,        60,    0, False, cs["email"]                 , "lower @=1"                                                    ,     1, 1,          0),
    "Estado"                                  : T(     1,        19,    0,  True, ""                          , ops["Estados"]                                                 ,    26, 0,         50),
    "Estado Civil"                            : T(     1,        10,    0,  True, ""                          , ops["Estado Civil"]                                            ,     1, 0,         50),
    "Excelência"                              : T(     1,        13,    0,  True, ""                          , ops["Excelência"]                                              ,     1, 0,         50),
    "Histórico"                               : T(     1,       256,    0, False, ""                          , ""                                                             ,     1, 1,          0),
    "Hora"                                    : T(    10,         8,    1, False, cs["hora"]                  , "hh:nn:ss"                                                     ,     1, 0,         50),
    "Hora Zona"                               : T(    10,         8,    1, False, cs["hora"]                  , "hh:nn:ssz"                                                    ,     1, 0,         50),
    "Hora XML"                                : T(    10,         8,    1, False, cs["hora"]                  , "hhnn"                                                         ,     1, 0,         50),
    "Inscrição Estadual SP"                   : T(     1,        12,    0, False, cs["números"]               , "000'.'000'.'000'.'000;000'.'000'.'000'.'000;ISENTO"           ,     1, 0,        100),
    "Inteiro"                                 : T(     3,        12,    0, False, cs["números"] + "-+"        , "0,;-0,;0"                                                     ,     1, 1,        100),
    "Inteiro 2"                               : T(     3,        12,    0, False, cs["números"] + "-+"        , "00,;-00,;00"                                                  ,     1, 1,        100),
    "Inteiro 3"                               : T(     3,        12,    0, False, cs["números"] + "-+"        , "000,;-000,;000"                                               ,     1, 1,        100),
    "Inteiro Positivo"                        : T(     3,        12,    0, False, cs["números"]               , "0,;0,;0"                                                      ,     1, 1,        100),
    "Inteiro 2 Positivo"                      : T(     3,        12,    0, False, cs["números"]               , "00,;00,;00"                                                   ,     1, 1,        100),
    "Inteiro 3 Positivo"                      : T(     3,        12,    0, False, cs["números"]               , "000,;000,;000"                                                ,     1, 1,        100),
    "Letras"                                  : T(     1,       256,    0, False, cs["letras"]                , "normalize"                                                    ,     1, 1,          0),
    "Letras e Espaços"                        : T(     1,       256,    0, False, cs["nome"]                  , "normalize"                                                    ,     1, 1,          0),
    "Letras e Números"                        : T(     1,       256,    0, False, cs["letras e números"]      , "normalize"                                                    ,     1, 1,          0),
    "Letras Números e Espaços"                : T(     1,       256,    0, False, cs["letras e números"] + " ", "normalize"                                                    ,     1, 1,          0),
    "Letras Números e _"                      : T(     1,       256,    0, False, cs["letras e números"] + "_", "normalize"                                                    ,     1, 1,          0),
    "Livre"                                   : T(     1,       256,    0, False, ""                          , "normalize"                                                    ,     1, 1,          0),
    "Letras Mai"                              : T(     1,       256,    0, False, cs["letras"]                , "upper normalize"                                              ,     1, 1,          0),
    "Letras Mai e Espaços"                    : T(     1,       256,    0, False, cs["nome"]                  , "upper normalize"                                              ,     1, 1,          0),
    "Letras Mai e Números"                    : T(     1,       256,    0, False, cs["letras e números"]      , "upper normalize"                                              ,     1, 1,          0),
    "Letras Mai Números e Espaços"            : T(     1,       256,    0, False, cs["letras e números"] + " ", "upper normalize"                                              ,     1, 1,          0),
    "Letras Mai Números e _"                  : T(     1,       256,    0, False, cs["letras e números"] + "_", "upper normalize"                                              ,     1, 1,          0),
    "Letras Min"                              : T(     1,       256,    0, False, cs["letras"]                , "lower normalize"                                              ,     1, 1,          0),
    "Letras Min e Espaços"                    : T(     1,       256,    0, False, cs["nome"]                  , "lower normalize"                                              ,     1, 1,          0),
    "Letras Min e Números"                    : T(     1,       256,    0, False, cs["letras e números"]      , "lower normalize"                                              ,     1, 1,          0),
    "Letras Min Números e Espaços"            : T(     1,       256,    0, False, cs["letras e números"] + " ", "lower normalize"                                              ,     1, 1,          0),
    "Letras Min Números e _"                  : T(     1,       256,    0, False, cs["letras e números"] + "_", "lower normalize"                                              ,     1, 1,          0),
    "Livre Mai"                               : T(     1,       256,    0, False, ""                          , "upper normalize"                                              ,     1, 1,          0),
    "Letras Acentuadas"                       : T(     1,       256,    0, False, cs["letras"]                , ""                                                             ,     1, 1,          0),
    "Letras Acentuadas e Espaços"             : T(     1,       256,    0, False, cs["nome"]                  , ""                                                             ,     1, 1,          0),
    "Letras Acentuadas e Números"             : T(     1,       256,    0, False, cs["letras e números"]      , ""                                                             ,     1, 1,          0),
    "Letras Acentuadas Números e Espaços"     : T(     1,       256,    0, False, cs["letras e números"] + " ", ""                                                             ,     1, 1,          0),
    "Livre Acentuado"                         : T(     1,       256,    0, False, ""                          , ""                                                             ,     1, 1,          0),
    "Letras Mai Acentuadas"                   : T(     1,       256,    0, False, cs["letras"]                , "upper"                                                        ,     1, 1,          0),
    "Letras Mai Acentuadas e Espaços"         : T(     1,       256,    0, False, cs["nome"]                  , "upper"                                                        ,     1, 1,          0),
    "Letras Mai Acentuadas e Números"         : T(     1,       256,    0, False, cs["letras e números"]      , "upper"                                                        ,     1, 1,          0),
    "Letras Mai Acentuadas Números e Espaços" : T(     1,       256,    0, False, cs["letras e números"] + " ", "upper"                                                        ,     1, 1,          0),
    "Livre Mai Acentuado"                     : T(     1,       256,    0, False, ""                          , "upper"                                                        ,     1, 1,          0),
    "Números"                                 : T(     1,       256,    0, False, cs["números"]               , ""                                                             ,     1, 1,        100),
    "Números e Espaços"                       : T(     1,       256,    0, False, cs["números"] + " "         , ""                                                             ,     1, 1,        100),
    "Números e Vírgulas"                      : T(     1,       256,    0, False, cs["números"] + ","         , ""                                                             ,     1, 1,        100),
    "Números e Pontos"                        : T(     1,       256,    0, False, cs["números"] + "."         , ""                                                             ,     1, 1,        100),
    "Números e Traços"                        : T(     1,       256,    0, False, cs["números"] + "-"         , ""                                                             ,     1, 1,        100),
    "Números e Barras"                        : T(     1,       256,    0, False, cs["números"] + "/"         , ""                                                             ,     1, 1,        100),
    "Números Pontos e Traços"                 : T(     1,       256,    0, False, cs["números"] + ".-"        , ""                                                             ,     1, 1,        100),
    "Números Pontos e Barras"                 : T(     1,       256,    0, False, cs["números"] + "./"        , ""                                                             ,     1, 1,        100),
    "Números Pontos Traços e Barras"          : T(     1,       256,    0, False, cs["números"] + ".-/"       , ""                                                             ,     1, 1,        100),
    "Mês"                                     : T(     1,         9,    0,  True, ""                          , ops["Mês"]                                                     ,     1, 0,         50),
    "Mês e Ano"                               : T(     9,         7,    3, False, cs["data"]                  , "mm/yyyy"                                                      ,     1, 0,         50),
    "Mês e Ano 2"                             : T(     9,         5,    3, False, cs["data"]                  , "mm/yy"                                                        ,     1, 0,         50),
    "Mês e Ano XML"                           : T(     9,         7,    3, False, cs["data"]                  , "yyyy-mm"                                                      ,     1, 0,         50),
    "Mês e Ano 2 XML"                         : T(     9,         5,    3, False, cs["data"]                  , "yy-mm"                                                        ,     1, 0,         50),
    "Pele"                                    : T(     1,         8,    0,  True, ""                          , ops["Pele"]                                                    ,     1, 0,         50),
    "Pertinência"                             : T(     1,        11,    0,  True, ""                          , ops["Pertinência"]                                             ,     1, 0,         50),
    "Pessoa"                                  : T(     1,         8,    0,  True, ""                          , ops["Pessoa"]                                                  ,     1, 0,         50),
    "PIS"                                     : T(     1,        11,    0, False, cs["números"]               , "000'.'00000'.'00-0;000'.'00000'.'00-0;000'.'00000'.'00-0"     ,     1, 0,        100),
    "PIS Números"                             : T(     1,        11,    0, False, cs["números"]               , "00000000000;00000000000;00000000000"                          ,     1, 0,        100),
    "Porcentagem"                             : T(     6,        14,    0,  True, cs["números"] + dp + '+-'   , "0%,;-0%,;0%"                                                  ,     1, 0,        100),
    "Porcentagem 1"                           : T(     6,        14,    1, False, cs["números"] + dp + '+-'   , "0.0%,;-0.0%,;0.0%"                                            ,     1, 0,        100),
    "Porcentagem 2"                           : T(     6,        14,    2, False, cs["números"] + dp + '+-'   , "0.00%,;-0.00%,;0.00%"                                         ,     1, 0,        100),
    "Porcentagem 3"                           : T(     6,        14,    3, False, cs["números"] + dp + '+-'   , "0.000%,;-0.000%,;0.000%"                                      ,     1, 0,        100),
    "Porcentagem 4"                           : T(     6,        14,    4, False, cs["números"] + dp + '+-'   , "0.0000%,;-0.0000%,;0.0000%"                                   ,     1, 0,        100),
    "Porcentagem 5"                           : T(     6,        14,    5, False, cs["números"] + dp + '+-'   , "0.00000%,;-0.00000%,;0.00000%"                                ,     1, 0,        100),
    "Porcentagem 6"                           : T(     6,        14,    6, False, cs["números"] + dp + '+-'   , "0.000000%,;-0.000000%,;0.000000%"                             ,     1, 0,        100),
    "Porcentagem Positivo"                    : T(     6,        14,    0,  True, cs["números"] + dp          , "0%,;0%,;0%"                                                   ,     1, 0,        100),
    "Porcentagem 1 Positivo"                  : T(     6,        14,    1, False, cs["números"] + dp          , "0.0%,;0.0%,;0.0%"                                             ,     1, 0,        100),
    "Porcentagem 2 Positivo"                  : T(     6,        14,    2, False, cs["números"] + dp          , "0.00%,;0.00%,;0.00%"                                          ,     1, 0,        100),
    "Porcentagem 3 Positivo"                  : T(     6,        14,    3, False, cs["números"] + dp          , "0.000%,;0.000%,;0.000%"                                       ,     1, 0,        100),
    "Porcentagem 4 Positivo"                  : T(     6,        14,    4, False, cs["números"] + dp          , "0.0000%,;0.0000%,;0.0000%"                                    ,     1, 0,        100),
    "Porcentagem 5 Positivo"                  : T(     6,        14,    5, False, cs["números"] + dp          , "0.00000%,;0.00000%,;0.00000%"                                 ,     1, 0,        100),
    "Porcentagem 6 Positivo"                  : T(     6,        14,    6, False, cs["números"] + dp          , "0.000000%,;0.000000%,;0.000000%0.000000%"                     ,     1, 0,        100),
    "Quebrado"                                : T(     6,        14,    0, False, cs["números"] + dp + '+-'   , "0.##############,;-0.##############,;0"                       ,     1, 3,        100),
    "Quebrado 1"                              : T(     6,        14,    1, False, cs["números"] + dp + '+-'   , "0.0,;-0.0,;0.0"                                               ,     1, 3,        100),
    "Quebrado 2"                              : T(     6,        14,    2, False, cs["números"] + dp + '+-'   , "0.00,;-0.00,;0.00"                                            ,     1, 3,        100),
    "Quebrado 3"                              : T(     6,        14,    3, False, cs["números"] + dp + '+-'   , "0.000,;-0.000,;0.000"                                         ,     1, 3,        100),
    "Quebrado 4"                              : T(     6,        14,    4, False, cs["números"] + dp + '+-'   , "0.0000,;-0.0000,;0.0000"                                      ,     1, 3,        100),
    "Quebrado 5"                              : T(     6,        14,    5, False, cs["números"] + dp + '+-'   , "0.00000,;-0.00000,;0.00000"                                   ,     1, 3,        100),
    "Quebrado 6"                              : T(     6,        14,    6, False, cs["números"] + dp + '+-'   , "0.000000,;-0.000000,;0.000000"                                ,     1, 3,        100),
    "Quebrado Positivo"                       : T(     6,        14,    0, False, cs["números"] + dp          , "0.##############,;-0.##############,;#"                       ,     1, 3,        100),
    "Quebrado 1 Positivo"                     : T(     6,        14,    1, False, cs["números"] + dp          , "0.0,;0.0,;0.0"                                                ,     1, 3,        100),
    "Quebrado 2 Positivo"                     : T(     6,        14,    2, False, cs["números"] + dp          , "0.00,;0.00,;0.00"                                             ,     1, 3,        100),
    "Quebrado 3 Positivo"                     : T(     6,        14,    3, False, cs["números"] + dp          , "0.000,;0.000,;0.000"                                          ,     1, 3,        100),
    "Quebrado 4 Positivo"                     : T(     6,        14,    4, False, cs["números"] + dp          , "0.0000,;0.0000,;0.0000"                                       ,     1, 3,        100),
    "Quebrado 5 Positivo"                     : T(     6,        14,    5, False, cs["números"] + dp          , "0.00000,;0.00000,;0.00000"                                    ,     1, 3,        100),
    "Quebrado 6 Positivo"                     : T(     6,        14,    6, False, cs["números"] + dp          , "0.000000,;0.000000,;0.000000"                                 ,     1, 3,        100),
    "RG"                                      : T(     1,        20,    0, False, cs["rg"]                    , "upper .<3 -<2 X<2"                                            ,     1, 1,        100),
    "Semana"                                  : T(     1,         7,    0,  True, ""                          , ops["Semana"]                                                  ,     1, 0,          0),
    "Seqüencial"                              : T(    14,        12,    0, False, cs["números"]               , "0,;0,;0"                                                      ,     1, 0,        100),
    "Sexo"                                    : T(     1,         1,    0,  True, ""                          , ops["Sexo"]                                                    ,     1, 0,         50),
    "Sexo Sigla"                              : T(     1,         1,    0,  True, ""                          , [x[:1] for x in ops["Sexo"]]                                   ,     1, 0,         50),
    "Sexo Extenso"                            : T(     1,         9,    0,  True, ""                          , [x[1:] for x in ops["Sexo"]]                                   ,     1, 0,         50),
    "Sim ou Não"                              : T(    12,         1,    0,  True, ""                          , ops["Sim ou Não"]                                              ,     1, 0,         50),
    "Telefone"                                : T(     1,        12,    0, False, cs["números"]               , "00(00)0000-0000;00(00)0000-0000;#"                            ,     1, 0,        100),
    "Celular"                                 : T(     1,        13,    0, False, cs["números"]               , "00(00)00000-0000;00(00)00000-0000;#"                          ,     1, 0,        100),
    "Tipo Logradouro"                         : T(     1,       256,    0,  True, ""                          , ops["Tipo Logradouro"]                                         ,     1, 0,        100),
    "Título"                                  : T(     1,       256,    0, False, cs["razão social"]          , "capital normalize"                                            ,     1, 0,          0),
    "UF"                                      : T(     1,         2,    0,  True, ""                          , [x[:1] for x in ops["Estados"]]                                ,    26, 0,         50),
    "Nome"                                    : T(     1,       256,    0, False, cs["nome"]                  , "capital normalize"                                            ,     1, 0,          0),
    "Razão Social"                            : T(     1,       256,    0, False, cs["razão social"]          , "capital normalize"                                            ,     1, 0,          0),
    "Título Mai"                              : T(     1,       256,    0, False, cs["razão social"]          , "upper normalize"                                              ,     1, 0,          0),
    "Nome Mai"                                : T(     1,       256,    0, False, cs["nome"]                  , "upper normalize"                                              ,     1, 0,          0),
    "Nome Min"                                : T(     1,       256,    0, False, cs["nome"]                  , "lower normalize"                                              ,     1, 0,          0),
    "Razão Social Mai"                        : T(     1,       256,    0, False, cs["razão social"]          , "upper normalize"                                              ,     1, 0,          0),
    "Título Acentuado"                        : T(     1,       256,    0, False, cs["razão social"]          , "capital"                                                      ,     1, 0,          0),
    "Nome Acentuado"                          : T(     1,       256,    0, False, cs["nome"]                  , "capital"                                                      ,     1, 0,          0),
    "Razão Social Acentuada"                  : T(     1,       256,    0, False, cs["razão social"]          , "capital"                                                      ,     1, 0,          0),
    "Título Mai Acentuado"                    : T(     1,       256,    0, False, cs["razão social"]          , "upper"                                                        ,     1, 0,          0),
    "Nome Mai Acentuado"                      : T(     1,       256,    0, False, cs["nome"]                  , "upper"                                                        ,     1, 0,          0),
    "Razão Social Mai Acentuada"              : T(     1,       256,    0, False, cs["razão social"]          , "upper"                                                        ,     1, 0,          0),
    "URL"                                     : T(     1,       256,    0, False, cs["url"]                   , "lower"                                                        ,     1, 1,          0),

    "num"                                     : T(     1,       256,    0, False, cs["números"]               , ""                                                             ,     1, 1,        100),
    "int"                                     : T(     3,        12,    0, False, cs["números"] + "-+"        , "0,;-0,;0"                                                     ,     1, 1,        100),
    "long"                                    : T(     3,        12,    0, False, cs["números"] + "-+"        , "0,;-0,;0"                                                     ,     1, 1,        100),
    "float"                                   : T(     6,        14,   fd, False, cs["números"] + dp + '+-'   , "{0},;-{0},;{0}".format(fs)                                    ,     1, 3,        100),
}

def new_float_type(tx):
    if tx[:5] == "float":
        try:
            decimals = int(tx[5:])
        except Exception:
            decimals = local['frac_digits']
        tx = 'float' + str(decimals)
        if tx not in tipos:
            fs = '0.' + '0' * decimals
            tipos[tx] = T(6, 14, decimals, False,
                          cs["números"] + dp + '+-',
                          "{0},;-{0},;{0}".format(fs), 1, 3, 100)
    return tx

# Try to add dolars, if can't get via locale, set $0.00, with comma thousand separator
try:
    dolares = {
        "Dólar"                               : T(     6,        14,    0, False, cs["números"] + '.+-'       , mascara_dinheiro(localization='en_US.UTF-8')                   ,     1, 0,        100),
        "Dólar 1"                             : T(     6,        14,    1, False, cs["números"] + '.+-'       , mascara_dinheiro(1, localization='en_US.UTF-8')                ,     1, 0,        100),
        "Dólar 2"                             : T(     6,        14,    2, False, cs["números"] + '.+-'       , mascara_dinheiro(2, localization='en_US.UTF-8')                ,     1, 0,        100),
        "Dólar 3"                             : T(     6,        14,    3, False, cs["números"] + '.+-'       , mascara_dinheiro(3, localization='en_US.UTF-8')                ,     1, 0,        100),
        "Dólar 4"                             : T(     6,        14,    4, False, cs["números"] + '.+-'       , mascara_dinheiro(4, localization='en_US.UTF-8')                ,     1, 0,        100),
        "Dólar 5"                             : T(     6,        14,    5, False, cs["números"] + '.+-'       , mascara_dinheiro(5, localization='en_US.UTF-8')                ,     1, 0,        100),
        "Dólar Positivo"                      : T(     6,        14,    0, False, cs["números"] + '.'         , mascara_dinheiro(localization='en_US.UTF-8', negativo=False)   ,     1, 0,        100),
        "Dólar 1 Positivo"                    : T(     6,        14,    1, False, cs["números"] + '.'         , mascara_dinheiro(1, localization='en_US.UTF-8', negativo=False),     1, 0,        100),
        "Dólar 2 Positivo"                    : T(     6,        14,    2, False, cs["números"] + '.'         , mascara_dinheiro(2, localization='en_US.UTF-8', negativo=False),     1, 0,        100),
        "Dólar 3 Positivo"                    : T(     6,        14,    3, False, cs["números"] + '.'         , mascara_dinheiro(3, localization='en_US.UTF-8', negativo=False),     1, 0,        100),
        "Dólar 4 Positivo"                    : T(     6,        14,    4, False, cs["números"] + '.'         , mascara_dinheiro(4, localization='en_US.UTF-8', negativo=False),     1, 0,        100),
        "Dólar 5 Positivo"                    : T(     6,        14,    5, False, cs["números"] + '.'         , mascara_dinheiro(5, localization='en_US.UTF-8', negativo=False),     1, 0,        100),
    }
except Exception:
    dolares = {
        "Dólar"                               : T(     6,        14,    0, False, cs["números"] + '.+-'       , '$0.00,;$-0.00,;$0.00'                                         ,     1, 0,        100),
        "Dólar 1"                             : T(     6,        14,    1, False, cs["números"] + '.+-'       , '$0.0,;$-0.0,;$0.0'                                            ,     1, 0,        100),
        "Dólar 2"                             : T(     6,        14,    2, False, cs["números"] + '.+-'       , '$0.00,;$-0.00,;$0.00'                                         ,     1, 0,        100),
        "Dólar 3"                             : T(     6,        14,    3, False, cs["números"] + '.+-'       , '$0.000,;$-0.000,;$0.000'                                      ,     1, 0,        100),
        "Dólar 4"                             : T(     6,        14,    4, False, cs["números"] + '.+-'       , '$0.0000,;$-0.0000,;$0.0000'                                   ,     1, 0,        100),
        "Dólar 5"                             : T(     6,        14,    5, False, cs["números"] + '.+-'       , '$0.00000,;$-0.00000,;$0.00000'                                ,     1, 0,        100),
        "Dólar Positivo"                      : T(     6,        14,    0, False, cs["números"] + '.'         , '$0.00,;$0.00,;$0.00'                                          ,     1, 0,        100),
        "Dólar 1 Positivo"                    : T(     6,        14,    1, False, cs["números"] + '.'         , '$0.0,;$0.0,;$0.0'                                             ,     1, 0,        100),
        "Dólar 2 Positivo"                    : T(     6,        14,    2, False, cs["números"] + '.'         , '$0.00,;$0.00,;$0.00'                                          ,     1, 0,        100),
        "Dólar 3 Positivo"                    : T(     6,        14,    3, False, cs["números"] + '.'         , '$0.000,;$0.000,;$0.000'                                       ,     1, 0,        100),
        "Dólar 4 Positivo"                    : T(     6,        14,    4, False, cs["números"] + '.'         , '$0.0000,;$0.0000,;$0.0000'                                    ,     1, 0,        100),
        "Dólar 5 Positivo"                    : T(     6,        14,    5, False, cs["números"] + '.'         , '$0.00000,;$0.00000,;$0.00000'                                 ,     1, 0,        100),
    }
for nome, config in dolares.items():
    tipos[nome] = config


def capitalize(text):
    excecoes = ((u'A', u'a'), (u'À', u'à'), (u'Ao', u'ao'),
                (u'Até', u'até'), (u'Com', u'com'), (u'Da', u'da'),
                (u'De', u'de'), (u'Do', u'do'), (u'Duma', u'duma'),
                (u'Dum', u'dum'), (u'E', u'e'), (u'É', u'é'),
                (u'Em', u'em'), (u'Num', u'num'), (u'Numa', u'numa'),
                (u'O', u'o'), (u'Ó', u'ó'), (u'Para', u'para'),
                (u'Por', u'por'), (u'Sem', u'sem'), (u'Sob', u'sob'),
                (u'Mas', u'mas')
                # Preposições excluídas por bom senso _meu_
                # u'ante', u'antes', u'após', u'contra', u'desde',
                # u'entre', u'perante', u'sobre', u'trás'
                )
    if not isinstance(text, unicode):
        text = str(text).decode('utf-8')
    text = text.title()
    for capital, normal in excecoes:
        text = text[0] + re.sub(r'(\W)%s(\W)' % capital,
                                r'\1%s\2' % normal, text[1:])
        if text.endswith(capital):
            text = text[:-len(capital)] + normal
    return text


def formatar(dados, tipo_pole):
    # print 'formatar', dados, tipo_pole
    if tipo_pole == 'Telefone':
        dados = somente_digitos(dados)
        dados = '551600000000'[:12 - len(dados)] + dados
    elif tipo_pole == 'Celular':
        dados = somente_digitos(dados)
        dados = '5516000000000'[:13 - len(dados)] + dados
    (tipo, tamanho, casas, cxopc, caracteres,
     mascara, padrao, alteravel, alinhamento) = tipos[tipo_pole]
    # print "tipo:", tipo, python_tipos[tipo]
    # print "tamanho:", tamanho
    # print "casas:", casas
    # print "cxopc:", cxopc
    # print "caracteres:", caracteres
    # print "mascara:", mascara
    # print "padrao:", padrao
    # print "alteravel:", alteravel
    # print "alinhamento:", alinhamento
    # print 'antes:', repr(dados)
    dados = convert_and_format(dados, python_tipos[tipo], casas)[1]
    # print 'depois:', repr(dados)
    if len(mascara) > 0 and mascara.count(';') > 1:
        p, n, z = mascara.split(';')[:3]
        # print 'p, n, z', p, n, z
        decimal = local['mon_decimal_point']
        # Retirar caracteres não numéricos, não decimal e não -
        numero = re.sub('[^0-9' + decimal + '-]', '', dados).lstrip('0')
        # Se não tem número retorna o zero
        if numero == '':
            if z == '#':
                return ''
            return z
        # Negativo se o primeiro caractere for -
        negativo = numero[0] == '-'
        # Escolher a máscara positiva ou negativa de acordo com o número
        mascara = n if negativo else p
        # Retirar todos os -
        numero = numero.replace('-', '')
        # Deixar apenas 1 ponto decimal
        n = numero.count(decimal)
        if n > 1:
            numero = numero[::-1].replace(decimal, '', n - 1)[::-1]
        # Se não tem número retorna o zero
        if numero == '' or numero == decimal:
            if z == '#':
                return ''
            return z.replace('.', decimal)
        # Verificar se tem , na máscara que siginifica fazer agrupamento
        agrupado = ',' in mascara
        # Retirar as , da máscara em como tratar os escapes '.', '0', '#' e ','
        # para voltá-los no fim
        mascara = (mascara.replace("'.'", "\x00").replace("'0'", "\x01").
                   replace("'#'", "\x02").replace("','", '\x03').
                   replace(',', ''))
        # Verificar se tem . na máscara que siginifica ponto decimal
        if '.' in mascara:
            # Separa a parte inteira da real no primeiro ponto
            masc_int, masc_real = mascara.split('.', 1)
            # Tirar pontos extras na parte real
            masc_real.replace('.', '')
            # Calcular o número de casas decimais contando 0 e # da parte real
            casas = masc_real.count('0') + masc_real.count('#')
            # Formatar o número de acordo com o padrão local
            numero = cf(numero, float, casas)[1]
        else:
            # Caso não tenha parte real, a inteira fica com a máscara toda
            masc_int = mascara
            masc_real = ''  # parte real vazia
            casas = 0  # sem casas decimais
            # Formatar o número de acordo com o padrão local
            numero = cf(numero, long)[1]
        # Retirar o agrupamento se não pedido pela máscara
        group = local['mon_thousands_sep']
        if not agrupado:
            numero = numero.replace(group, '')
        # Separa o número em parte inteira e parte real pelo ponto decimal
        if casas:
            num_int, num_real = numero.split(decimal)
        else:
            num_int = numero
            num_real = ''
        # Complementar a parte inteira do número com zeros até
        # o número de posicões da máscara
        num_int = '0' + '0' * (masc_int.count('0') + masc_int.count('#') -
                               len(num_int.replace(group, ''))) + num_int
        # Compor a parte inteira do resultado subustituir 0 e # da parte
        # inteira da máscara pelo número correspondente no número formatado,
        # copiando a parte da máscara que não for 0 nem #,
        # da direita para a esquerda
        i = -1
        dados = ''
        j = len(masc_int)
        while j > 0:
            j -= 1
            c = masc_int[j]
            if c == '0':
                dados += num_int[i]
                i -= 1
                if num_int[i] == group:
                    dados += num_int[i]
                    i -= 1
            elif c == '#':
                if num_int[i] != '0':
                    dados += num_int[i]
                elif sum(map(lambda x: int(x), num_int[0:i])) != 0:
                    dados += num_int[i]
                i -= 1
                if num_int[i] == group:
                    dados += num_int[i]
                    i -= 1
            else:
                dados += c
            if c in ('0', '#') and ('#' not in masc_int[:j]
                                    and '0' not in masc_int[:j]):
                dados += num_int[1:i + 1][::-1]
        # Termina de compor a parte inteira de com os dígitos restantes e
        # inverte os dígitos/carateres formados acima
        dados = (num_int[1:] if i == -1 else '') + dados[::-1]
        # No caso de ter casas decimais, faz paraticamente o mesmo tratamento
        # acima, com a ressalva de obrigatoriedade de zeros à esquerda
        if casas:
            dados2 = ''
            i = -1
            obrigatorio = False
            for c in masc_real[::-1]:
                if c == '0':
                    obrigatorio = True
                    dados2 += num_real[i]
                    i -= 1
                elif c == '#':
                    if num_real[i] != '0' or obrigatorio:
                        obrigatorio = True
                        dados2 += num_real[i]
                    i -= 1
                else:
                    dados2 += c
            dados += decimal + dados2[::-1]
        # Termina fazendo com que voltem os caracteres escapados anteriormente
        dados = (dados.replace('\x00', '.').replace('\x01', '0').
                 replace('\x02', '#').replace('\x03', ','))

    # Tratamento de string
    if type(dados) == str:
        dados = dados.decode('utf-8')
    if "normalize" in mascara:
        dados = normalize(dados)
    if "upper" in mascara:
        dados = dados.upper()
    elif "lower" in mascara:
        dados = dados.lower()
    elif "capital" in mascara:
        capitalize(dados)
    return dados


def exclusive_name_columns(columns, lower=True):
    columns_temp = [c.lower() if lower else c for c in columns]
    columns = []
    while columns_temp:
        new_col_name = columns_temp.pop(0)
        if new_col_name in columns:
            col = new_col_name + '_'
            n = 1
            new_col_name += '_1'
            while new_col_name in columns_temp + columns:
                n += 1
                new_col_name = col + str(n)
        columns.append(new_col_name)
    return columns


def fetchdict(cur, one=False, ordered=True, lower=False):
    columns = exclusive_name_columns(zip(*cur.description)[0], lower)
    Dict = OrderedDict if ordered else dict
    if one:
        row = cur.fetchone()
        return Dict(zip(columns, row)) if row else None
    return [Dict(zip(columns, reg)) for reg in cur]


def cursordict(cur, one=False, ordered=True, lower=False):
    columns = exclusive_name_columns(zip(*cur.description)[0], lower)
    Dict = OrderedDict if ordered else dict
    for row in cur:
        yield Dict(zip(columns, row))


def fetchtupleone(cur):
    columns = exclusive_name_columns(zip(*cur.description)[0])
    Row = namedtuple('Row', columns)
    row = cur.fetchone()
    return Row._make(row) if row else None


def fetchtuple(cur):
    columns = exclusive_name_columns(zip(*cur.description)[0])
    Row = namedtuple('Row', columns)
    return [Row._make(row) for row in cur]


def cursortuple(cur):
    columns = exclusive_name_columns(zip(*cur.description)[0])
    Row = namedtuple('Row', columns)
    for row in cur:
        yield Row._make(row)


def md5(data):
    hash_processor = hashlib.md5()
    hash_processor.update(data)
    return hash_processor.hexdigest()


def make_pwd_hash(pwd, user=None):
    if user:
        return md5(md5(user) + 'bf43cbd322d104864ce08fa9ddf0749e' + md5(pwd))
    return md5(pwd)


def sql_like(value):
    return '%{}%'.format('%'.join(value.split()))


def sql_in(values):
    return ', '.join([':id%d' % n for (n, v) in enumerate(values)])


def sql_in_kwargs(values):
    return {'id%d' % k: v for (k, v) in enumerate(values)}


def truncate(value):
    return float(Decimal(value).quantize(Decimal('0.01'), rounding=ROUND_DOWN))


def get_name_of_month(today, date):
    current_month = datetime.datetime(today.year, today.month, 1)
    name = ''

    if date < current_month:
        name = (datetime.datetime.strftime(date, '%Y_') +
                string.capitalize(datetime.datetime.strftime(date, '%B')))

    return name


def get_danfe_path(rootdir, key, today, emit_date):
    subfolder = get_name_of_month(today, emit_date)
    return os.path.join(rootdir, subfolder, 'PDF', key + '.pdf')


def first_day(date):
    return convert_and_format(date, datetime.date, MONTH)[0]


WEEKINDEX = {'SEG': 0, 'TER': 1, 'QUA': 2,
             'QUI': 3, 'SEX': 4, 'SAB': 5, 'DOM': 6}


def due_date(dtstart, days):
    return [dtstart + relativedelta(days=day) for day in days]


def due_date_to_nearest_monthday(dtstart, days, monthday):
    return [min(rrule(MONTHLY,
                      bymonthday=monthday,
                      dtstart=day - relativedelta(days=30),
                      until=day + relativedelta(days=30)),
                key=lambda x: abs(x - day))
            for day in due_date(dtstart, days)]


def due_date_to_nearest_weekday(dtstart, days, weekdays=WEEKINDEX.keys()):
    return [min(rrule(WEEKLY,
                      byweekday=[WEEKINDEX.get(d, 0) for d in weekdays],
                      dtstart=day - relativedelta(weeks=1),
                      until=day + relativedelta(weeks=1)),
                key=lambda x: abs(x - day))
            for day in due_date(dtstart, days)]


def due_date_to_next_weekday(dtstart, days, weekdays=WEEKINDEX.keys()):
    return [rrule(WEEKLY,
                  byweekday=[WEEKINDEX.get(d, 0) for d in weekdays],
                  count=1,
                  dtstart=day)[0]
            for day in due_date(dtstart, days)]


def slug(text):
    return re.sub(r'\W+', '_', normalize(text)).lower()


def slug_uppercase(text):
    return re.sub(r'([a-z])([A-Z])', r'\1_\2',
                  re.sub(r'\W', '_', normalize(text))).lower()


def space_uppercase(string, normalized=False, lower=False):
    if normalized:
        string = normalize(string)
    string = re.sub(r'([a-z])([A-Z])', r'\1 \2', string)
    return string.lower() if lower else string


def split_uppercase(string):
    return re.sub(r'([a-z])([A-Z])', r'\1 \2', string)


def normalize(text):
    if not isinstance(text, unicode):
        text = str(text).decode('utf-8')
    return unicodedata.normalize('NFKD', text.replace(u'Æ', u'AE').
                                 replace(u'æ', u'ae').replace(u'ª', u'a.').
                                 replace(u'º', u'.')).encode('ascii', 'ignore')


def float_sped(valor):
    if valor:
        try:
            return ("%0.2f" % float(str(valor))).replace('.', ',')
        except Exception:
            return str(valor).strip().replace('.', ',')
    return '0,00'


def xml_str(xml):
    return str(xml).strip().upper()


def xml_float(xml):
    xml = str(xml)
    if xml:
        return float(xml)
    return 0.


def xml_data(xml):
    # 2014-03-31T17:04:21
    dh = [int(x) for x in re.split('[-T :]', str(xml))]
    if len(dh) > 3:
        return datetime.datetime(*dh)
    return datetime.date(*dh)


UNKNOW = 0
LINUX = 1
WINDOWS = 2
OSX = 3
OS2 = 4
RISC = 5
ATHE = 6


def platform():
    platform = sys.platform.lower()
    if platform.startswith('linux'):
        return LINUX
    if platform.startswith('win32') or platform.starswith('cygwin'):
        return WINDOWS
    if platform.startswith('darwin'):
        return OSX
    if platform.startswith('os2'):
        return OS2
    if platform.startswith('risc'):
        return RISC
    if platform.startswith('athe'):
        return ATHE
    return UNKNOW


def crc16(data):
    USL = 0xFFFF  # unsigned short limit (16 bits)
    crc = USL
    for d in data:
        x = crc >> 8 ^ ord(d)
        x ^= x >> 4
        crc = (crc << 8 & USL) ^ (x << 12 & USL) ^ (x << 5 & USL) ^ (x & USL)
    return "%04x" % crc


def printf(*args):
    print ' '.join(str(x) for x in args)
    sys.stdout.flush()


class cached_property(object):
    """ A property that is only computed once per instance and then replaces
        itself with an ordinary attribute. Deleting the attribute resets the
        property.

        Source: https://github.com/bottlepy/bottle
                      /commit/fa7733e075da0d790d809aa3d2f53071897e6f76
        """

    def __init__(self, func):
        self.__doc__ = getattr(func, '__doc__')
        self.func = func

    def __get__(self, obj, cls):
        if obj is None:
            return self
        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value


class str_property(object):
    def __init__(self, func):
        self.__doc__ = getattr(func, '__doc__')
        self.func = func

    def __get__(self, obj, cls):
        if obj is None:
            return self
        value = obj.__dict__[self.func.__name__] = xml_str(self.func(obj))
        return value


class float_property(object):
    def __init__(self, func):
        self.__doc__ = getattr(func, '__doc__')
        self.func = func

    def __get__(self, obj, cls):
        if obj is None:
            return self
        value = obj.__dict__[self.func.__name__] = xml_float(self.func(obj))
        return value


class int_property(object):
    def __init__(self, func):
        self.__doc__ = getattr(func, '__doc__')
        self.func = func

    def __get__(self, obj, cls):
        if obj is None:
            return self
        value = obj.__dict__[self.func.__name__] = int(
            xml_float(self.func(obj)))
        return value


class ErrorList(Exception):

    def __init__(self, msg, error_list):
        self.msg = msg
        self.error_list = error_list

    def __str__(self):
        return ('{}\n\n{}'.format(self.msg, '\n\n'.join(self.error_list)))
