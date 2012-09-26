#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""PoleXML - Operações com XML em Python

Arquivo: PoleXML.py
Versão.: 0.1.0
Autor..: Claudio Polegato Junior
Data...: 25 Mar 2011

Copyright © 2011 - Claudio Polegato Junior <junior@juniorpolegato.com.br>
Todos os direitos reservados
"""

# Módulo para validação de XML e importação
import lxml.etree

# Módulo feito por Junior Polegato em CPython para assinar XML
try:
    import PoleXmlSec
except ImportError as err:
    print "Problemas ao importar o módulo PoleXmlSec: " + str(err)


# Constantes
MARCA_XML = '<?xml version="1.0" encoding="utf-8"?>'
#XML_ESCAPE = {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}
#XML_UNESCAPE = {'&amp;': '&', '&lt;': '<', '&gt;': '>', '&quot;': '"', '&#39;': "'"}
FILHO = -1
TEXTO = -2

# Classe XML
class XML(object):
    def __init__(self, nome = None, pai = None):
        #print '__init__', nome, pai
        self.__filhos = []
        self.__xmls = []
        self.__atributos = []
        self.__valores = []
        self.__re = None
        self.__nome = nome
        self.__pai = pai

    def __getattribute__(self, filho):
        #print '__getattribute__', filho
        if filho[:6] == '_XML__' or filho == '__class__':
            return object.__getattribute__(self, filho)
        #print '__getattribute__', filho
        if filho not in self.__filhos:
            self.__filhos.append(filho)
            self.__xmls.append(XML(filho, self))
            return self.__xmls[-1]
        return self.__xmls[self.__filhos.index(filho)]

    def __setattr__(self, filho, valor):
        #print '__setattr__', filho, valor
        if filho[:6] == '_XML__':
            object.__setattr__(self, filho, valor)
        else:
            if isinstance(valor, XML):
                object.__getattribute__(self, '__getattribute__')(filho).__filhos += valor.__filhos
                object.__getattribute__(self, '__getattribute__')(filho).__xmls += valor.__xmls
                object.__getattribute__(self, '__getattribute__')(filho).__atributos += valor.__atributos
                object.__getattribute__(self, '__getattribute__')(filho).__valores += valor.__valores
            else:
                object.__getattribute__(self, '__getattribute__')(filho).__filhos.append('')
                object.__getattribute__(self, '__getattribute__')(filho).__xmls.append(valor)

    def __getitem__(self, atributo):
        #print '__getitem__', atributo
        if type(atributo) != str:
            raise TypeError('Atributo de um nó XML precisa ser string.')
        if atributo not in self.__atributos:
            return None
        return self.__valores[self.__atributos.index(atributo)]

    def __setitem__(self, atributo, valor):
        #print '__setitem__', atributo, valor
        if type(atributo) != str:
            raise TypeError('Atributo de um nó XML precisa ser string.')
        if atributo in self.__atributos:
            self.__valores[self.__atributos.index(atributo)] = valor
        else:
            self.__atributos.append(atributo)
            self.__valores.append(valor)

    def __add__(self, valor):
        #print "__add__", valor
        if isinstance(valor, XML):
            self.__filhos += valor.__filhos
            self.__xmls += valor.__xmls
            self.__atributos += valor.__atributos
            self.__valores += valor.__valores
        else:
            self.__filhos.append('')
            self.__xmls.append(valor)

    def __del__(self, no_xml):
        print "__del__", no_xml

    def __str__(self):
        #print '__str__', self.__nome
        return exportar(self, -1, 0, False, True)

    def __repr__(self):
        #print '__repr__', self.__nome
        return exportar(self)

    def __call__(self, filho = None, qual = 0):
        '''Se filho for None, cria um novo nó e adiciona a estrutura, util para criar nós com mesmo nome.
           Se filho for int, retorna nº filho do nó pai.
           Se filho for '' equivale a todos os filho.
           Se filho for string e qual for inteiro igual a 0, retorna quantos filhos com este nome tem.
           Se filho for string e qual for inteiro igual a -1, cria um novo filho e adiciona a estrutura, util para criar filhos com mesmo nome ou a partir de string.
           Se filho for string e qual for inteiro igual a -2, adiciona um elemento texto ao elemento chamador.
           Se filho for string e qual for inteiro maior que 0, retorna o nó requerido.
           Se filho for string e qual for inteiro maior que o número de filhos com este nome, levanta uma exceção.
        '''
        #print '__call__', type(filho), filho, qual
        if filho == None:
            self.__pai.__filhos.append(self.__nome)
            self.__pai.__xmls.append(XML(self.__nome, self.__pai))
            return self.__pai.__xmls[-1]
        if type(filho) == int:
            return self.__pai(self.__nome, filho)
        if (type(filho) != str and type(filho) != unicode) or type(qual) != int:
            raise TypeError('Filho e qual o filho precisam ser string e inteiro, respectivamente.')
        if qual == FILHO:
            if len(filho) == 0:
                raise ValueError('Filho precisa ser string com pelo menos um caracter para criar um novo filho.')
            self.__filhos.append(filho)
            self.__xmls.append(XML(filho, self))
            return self.__xmls[-1]
        if qual == TEXTO:
            #if len(filho) == 0:
            #    raise ValueError('Filho precisa ser string com pelo menos um caracter para criar um novo filho.')
            self.__filhos.append('')
            self.__xmls.append(filho)
            return self
        if qual == 0:
            if filho == '':
                return len(self.__filhos)
            return self.__filhos.count(filho)
        if filho == '':
            if qual > len(self.__filhos):
                raise IndexError('Não encontrado o ' + str(qual) + 'º filho "' + filho + '" dentre o(s) ' + str(n + 1) + ' filho(s) que o nó "' + caminho + '" possui.')
            return self.__xmls[qual - 1]
        contador = qual
        for n, f in enumerate(self.__filhos):
            #print f, filho, f == filho, qual
            if f == filho:
                contador -= 1
                if contador == 0:
                    return self.__xmls[n]
        caminho = self.__nome
        atual = self.__pai
        while atual.__nome:
            caminho = atual.__nome + '.' + caminho
            atual = atual.__pai
        raise IndexError('Não encontrado o ' + str(qual) + 'º filho "' + filho + '" dentre o(s) ' + str(n + 1) + ' filho(s) que o nó "' + caminho + '" possui. Ele possui ' + str(qual - contador) + ' filho(s) com este nome.')

    def __lt__(self, valor):
        if isinstance(valor, XML):
            return exportar(self, -1, 0, False) < exportar(valor, -1, 0, False)
        return exportar(self, -1, 0, False) < valor

    def __le__(self, valor):
        if isinstance(valor, XML):
            return exportar(self, -1, 0, False) <= exportar(valor, -1, 0, False)
        return exportar(self, -1, 0, False) <= valor

    def __eq__(self, valor):
        if isinstance(valor, XML):
            return exportar(self, -1, 0, False) == exportar(valor, -1, 0, False)
        return exportar(self, -1, 0, False) == valor

    def __ne__(self, valor):
        if isinstance(valor, XML):
            return exportar(self, -1, 0, False) != exportar(valor, -1, 0, False)
        return exportar(self, -1, 0, False) != valor

    def __gt__(self, valor):
        if isinstance(valor, XML):
            return exportar(self, -1, 0, False) > exportar(valor, -1, 0, False)
        return exportar(self, -1, 0, False) > valor

    def __ge__(self, valor):
        if isinstance(valor, XML):
            return exportar(self, -1, 0, False) >= exportar(valor, -1, 0, False)
        return exportar(self, -1, 0, False) >= valor

def importar(xml):
    def _importar(pai, elemento):
        atual = pai(elemento.tag.split('}')[-1], FILHO)
        parent = elemento.getparent()
        if parent is not None:
            ns_pai = elemento.getparent().nsmap
        else:
            ns_pai = []
        for ns in elemento.nsmap:
            if ns in ns_pai and elemento.nsmap[ns] == ns_pai[ns]:
                continue
            if ns == None:
                atual['xmlns'] = unescape(elemento.nsmap[ns])
            else:
                atual['xmlns:' + ns] = unescape(elemento.nsmap[ns])
        for a in elemento.attrib:
            atual[a] = elemento.attrib[a]
        if elemento.text is not None:
            for texto in elemento.text.split('\n'):
                texto2 = unescape(texto)
                if len(texto2):
                    atual(texto2, TEXTO)
        for filho in elemento:
            _importar(atual, filho)
            if filho.tail is not None:
                for texto in filho.tail.split('\n'):
                    texto2 = unescape(texto)
                    if len(texto2):
                        atual(texto2, TEXTO)

    doc = lxml.etree.fromstring(str(xml))
    retorno = XML()
    _importar(retorno, doc)
    return retorno

def validar(xml, arquivo_xsd):
    '''Função que valida um XML usando lxml do Python via arquivo XSD'''
    # Carrega o esquema XML do arquivo XSD
    xsd = lxml.etree.XMLSchema(file = arquivo_xsd)
    # Converte o XML passado em XML do lxml
    xml = lxml.etree.fromstring(str(xml))
    # Verifica a validade do xml
    erros = []
    if not xsd(xml):
        # Caso tenha erros, cria uma lista de erros
        for erro in xsd.error_log:
            erros.append({
                'message'    : erro.message,
                'domain'     : erro.domain,
                'type'       : erro.type,
                'level'      : erro.level,
                'line'       : erro.line,
                'column'     : erro.column,
                'filename'   : erro.filename,
                'domain_name': erro.domain_name,
                'type_name'  : erro.type_name,
                'level_name' : erro.level_name
            })
    # Retorna os erros, sendo uma lista vazia caso não haja erros
    return erros

def assinar(xml, filho_assinatura, filho_id, atributo_id, arquivo_chave_pem, arquivo_certificado_pem):
    # Se não existir, criar estrutura para assinatura com o atributo_id informado
    if not filho_assinatura('Signature'):
        filho_assinatura.Signature['xmlns'] = "http://www.w3.org/2000/09/xmldsig#"
        filho_assinatura.Signature.SignedInfo.CanonicalizationMethod['Algorithm'] = "http://www.w3.org/TR/2001/REC-xml-c14n-20010315"
        filho_assinatura.Signature.SignedInfo.SignatureMethod['Algorithm'] = "http://www.w3.org/2000/09/xmldsig#rsa-sha1"
        if atributo_id is None or len(atributo_id) == 0:
            filho_assinatura.Signature.SignedInfo.Reference['URI'] = ''
        else:
            filho_assinatura.Signature.SignedInfo.Reference['URI'] = '#' + filho_id[atributo_id]
        filho_assinatura.Signature.SignedInfo.Reference.Transforms.Transform['Algorithm'] = "http://www.w3.org/2000/09/xmldsig#enveloped-signature"
        filho_assinatura.Signature.SignedInfo.Reference.Transforms.Transform()['Algorithm'] = "http://www.w3.org/TR/2001/REC-xml-c14n-20010315"
        filho_assinatura.Signature.SignedInfo.Reference.DigestMethod['Algorithm'] = "http://www.w3.org/2000/09/xmldsig#sha1"
        filho_assinatura.Signature.SignedInfo.Reference.DigestValue
        filho_assinatura.Signature.SignatureValue
        filho_assinatura.Signature.KeyInfo.X509Data.X509Certificate
    # Otimizar tamanho do XML tirando espaços extras e quebras de linha, salvando em um arquivo
    #open('/tmp/nao_assinado.xml', 'w').write(exportar(xml, -1))
    # Assinar o conteúdo do arquivo salvo acima e salvar o resultado em outro
    #import os
    #os.system('xmlsec1 sign --id-attr:' + atributo_id + ' ' + filho_id._XML__nome + ' --output /tmp/assinado.xml --privkey-pem ' + arquivo_chave_pem + ',' + arquivo_certificado_pem + ' /tmp/nao_assinado.xml')
    #del os
    # Recarregar o xml assinado e retorná-lo
    #return open('/tmp/assinado.xml').read().replace('\r', '').replace('\n', '')
    xml_assinado = PoleXmlSec.assinar(exportar(xml, -1), arquivo_chave_pem, arquivo_certificado_pem, atributo_id, filho_id._XML__nome)
    xml_assinado = xml_assinado.replace('\r', '').replace('\n', '')
    xml_assinado = importar(xml_assinado)
    caminho = ['Signature']
    pai = filho_assinatura
    while pai._XML__nome is not None:
        caminho.append(pai._XML__nome)
        pai = pai._XML__pai
    assinatura = xml_assinado
    for c in caminho[::-1]:
        assinatura = assinatura(c, 1)
    filho_assinatura.Signature.SignedInfo.Reference.DigestValue = assinatura.SignedInfo.Reference.DigestValue
    filho_assinatura.Signature.SignatureValue = assinatura.SignatureValue
    filho_assinatura.Signature.KeyInfo.X509Data.X509Certificate = assinatura.KeyInfo.X509Data.X509Certificate
    return xml

def escape(string):
    if type(string) == unicode:
        string = string.encode('utf-8')
    return str(string).strip().replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')
    #~ if type(string) != unicode:
        #~ string = str(string).decode('utf-8')
    #~ string = string.strip()
    #~ escapada = u''
    #~ for c, d in [(c, ord(c)) for c in string]:
        #~ if d > 126 or c == "'":
            #~ escapada += '&#' + str(d) + ';'
        #~ elif c in XML_ESCAPE:
            #~ escapada += XML_ESCAPE[c]
        #~ else:
            #~ escapada += c
    #~ return escapada.encode('utf-8')

def unescape(string):
    if type(string) == unicode:
        string = string.encode('utf-8')
    return str(string).strip().replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&#39;', "'")
    #~ if type(string) != unicode:
        #~ string = str(string).decode('utf-8')
    #~ string = string.strip()
    #~ unescapada = u''
    #~ p = 0
    #~ p2 = string.find('&', p)
    #~ while p2 != -1:
        #~ unescapada += string[p:p2]
        #~ p = string.find(';', p2 + 1) + 1
        #~ codigo = string[p2 : p]
        #~ if codigo[1] == '#':
            #~ unescapada += unichr(int(codigo[2:-1]))
        #~ elif codigo in XML_UNESCAPE:
            #~ unescapada += XML_UNESCAPE[codigo]
        #~ else:
            #~ raise ValueError('Valor precedido por "&" na string XML "' + string.encode('utf-8') + '", posição ' + str(p2 + 1) + ', não é válido!')
        #~ p2 = string.find('&', p)
    #~ unescapada += string[p:]
    #~ print string, '=>', unescapada
    #~ return unescapada.encode('utf-8')

def exportar(xml, endentacao = 4, nivel = 0, com_marca_xml = True, escapado = True):
    '''Exporta um XML com alguns ajustes, sendo que endentação negativa fica tudo numa linha só, sem quebra.'''
    def _exportar(xml, endentacao, nivel):
        if endentacao < 0:
            dente = ''
            quebra = ''
        else:
            dente = ' ' * endentacao * nivel
            quebra = '\n'
        conteudo = ''
        for nome_filho, xml_filho in zip(xml._XML__filhos, xml._XML__xmls):
            if xml_filho is None or (type(xml_filho) == str and xml_filho == ''):
                continue
            if isinstance(xml_filho, XML):
                atributos = ''
                ns = ''
                for atributo, valor in zip(xml_filho._XML__atributos, xml_filho._XML__valores):
                    if atributo == ':ns':
                        ns = valor + ':'
                    else:
                        atributos += ' ' + atributo + '="' + _escape(valor) + '"'
                netos = _exportar(xml_filho, endentacao, nivel + 1)
                if len(netos):
                    conteudo += dente + '<' + ns + nome_filho + atributos + '>' + (netos, quebra + netos + dente)[netos.count('<') > 0 or netos.count('\n') > 1] + '</' + ns + nome_filho + '>' + quebra
                else:
                    conteudo += dente + '<' + ns + nome_filho + atributos + '/>' + quebra
            else:
                if conteudo and endentacao < 0:
                    if conteudo[-1] == '>':
                        conteudo += _escape(xml_filho)
                    else:
                        conteudo += ' ' + _escape(xml_filho)
                else:
                    conteudo += dente + _escape(xml_filho) + quebra
        if conteudo.count('<') == 0 and conteudo.count('\n') == 1:
            return conteudo.strip()
        return conteudo

    if escapado:
        _escape = escape
    else:
        _escape = str
    if com_marca_xml:
        return ' ' * endentacao * nivel * (endentacao > 0) + MARCA_XML + '\n' * (endentacao > 0) + _exportar(xml, endentacao, nivel)
    return _exportar(xml, endentacao, nivel)
