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
import os
import StringIO
import xml.parsers.expat

# Módulo feito por Junior Polegato em CPython para assinar XML
try:
    import PoleXmlSec
except ImportError as err:
    print "Problemas ao importar o módulo PoleXmlSec: " + str(err)

# Constantes
MARCA_XML = '<?xml version="1.0" encoding="utf-8"?>'
FILHOS = 0
FILHO = -1
TEXTO = -2
RAIZ = -3
PAI = -4
NOME = -5
ATRIBUTOS = -6


# Classe XML
class XML(object):
    def __init__(self, nome=None, pai=None):
        # print '__init__', nome, pai
        self.__filhos = []
        self.__xmls = []
        self.__atributos = []
        self.__valores = []
        self.__re = None
        self.__nome = nome
        self.__pai = pai

    def __posicionar(self, filho, i):
        # print '__posicionar', filho, i
        procura = self.__filhos
        retorno = self.__xmls
        todos = filho is None or filho == ''
        if i == 0 or abs(i) > (len(procura) if todos
                               else procura.count(filho)):
            raise ValueError("%iº `%s´ não encontrado em `%s´!" %
                             (i, filho, self.__nome))
        if todos:
            return retorno[i - 1]
        if i < 0:
            i = -i
            procura = procura[::-1]
            retorno = retorno[::-1]
        j = -1
        while i:
            j = procura.index(filho, j + 1)
            i -= 1
        return retorno[j]

    def __desmembrar(self, valor):
        # print '__desmembrar', valor
        if isinstance(valor, (tuple, list)):
            if len(valor) != 2 or type(valor[1]) != int:
                raise Exception("The set value must be a int position and"
                                " a value for this node.")
            valor, i = valor
        else:
            i = 1
        return valor, i

    def __getattribute__(self, filho):
        # print '__getattribute__', filho
        if filho[:6] == '_XML__' or filho == '__class__':
            return object.__getattribute__(self, filho)
        # print '__getattribute__', filho
        if filho not in self.__filhos:
            self.__filhos.append(filho)
            no = XML(filho, self)
            self.__xmls.append(no)
            return no
        return self.__xmls[self.__filhos.index(filho)]

    def __setattr__(self, filho, valor):
        # print '__setattr__', filho, valor
        if filho[:6] == '_XML__':
            object.__setattr__(self, filho, valor)
            return
        valor, i = self.__desmembrar(valor)
        if filho not in self.__filhos and i == 1:
            self.__filhos.append(filho)
            no = XML(filho, self)
            self.__xmls.append(no)
        else:
            no = self.__posicionar(filho, i)
        if isinstance(valor, XML):
            no.__filhos = valor.__filhos
            no.__xmls = valor.__xmls
            no.__atributos = valor.__atributos
            no.__valores = valor.__valores
        else:
            while '' in no.__filhos:
                i = no.__filhos.index('')
                del no.__filhos[i]
                del no.__xmls[i]
            if valor is not None:
                no.__filhos.insert(0, '')
                no.__xmls.insert(0, valor)

    def __delattr__(self, filho):
        # print '__delattr__', filho
        i = self.__filhos.index(filho)
        del self.__filhos[i]
        del self.__xmls[i]

    def __getitem__(self, atributo):
        # print '__getitem__', atributo
        if not isinstance(atributo, (str, unicode)):
            raise TypeError('Atributo de um nó XML precisa ser string.')
        if atributo not in self.__atributos:
            return None
        return self.__valores[self.__atributos.index(atributo)]

    def __delitem__(self, atributo):
        if not isinstance(atributo, (str, unicode)):
            raise TypeError('Atributo de um nó XML precisa ser string.')
        if atributo not in self.__atributos:
            raise TypeError('O valor None apaga um atributo,'
                            ' mas ele não existe. Atributo: %s' % atributo)
        del self.__valores[self.__atributos.index(atributo)]
        del self.__atributos[self.__atributos.index(atributo)]

    def __setitem__(self, atributo, valor):
        # print '__setitem__', atributo, valor
        if not isinstance(atributo, (str, unicode)):
            raise TypeError('Atributo de um nó XML precisa ser string.')
        if valor is None:
            if atributo not in self.__atributos:
                raise TypeError('O valor None apaga um atributo,'
                                ' mas ele não existe. Atributo: %s' % atributo)
            del self.__valores[self.__atributos.index(atributo)]
            del self.__atributos[self.__atributos.index(atributo)]
        elif atributo in self.__atributos:
            self.__valores[self.__atributos.index(atributo)] = valor
        else:
            self.__atributos.append(atributo)
            self.__valores.append(valor)

    def __add__(self, valor):
        # print "__add__", valor
        valor, i = self.__desmembrar(valor)
        no = self.__pai.__posicionar(self.__nome, i) if self.__pai else self
        if isinstance(valor, XML):
            no.__filhos += valor.__filhos
            no.__xmls += valor.__xmls
            no.__atributos += valor.__atributos
            no.__valores += valor.__valores
            for x in valor.__xmls:
                x.__pai = no
        else:
            no.__filhos.append('')
            no.__xmls.append(valor)
        return no

    def __sub__(self, nome):
        # print "__sub__", nome
        nome, i = self.__desmembrar(nome)
        no = self.__posicionar(nome, i)
        i = self.__xmls.index(no)
        del self.__filhos[i]
        del self.__xmls[i]
        return self

    def __del__(self):
        # print "__del__", self
        pass

    def __str__(self):
        # print '__str__', self.__nome
        return exportar(self, -1, 0, False)

    def __repr__(self):
        # print '__repr__', self.__nome
        return exportar(self)

    def __call__(self, filho=None, qual=0):
        '''Se filho for None, cria um novo nó e adiciona a estrutura,
               util para criar nós com mesmo nome.
           Se filho for int, retorna enésimo filho do nó pai;
               se 0, retorna quantos irmãos com este nome.
           Se filho for '' equivale a todos os filhos para uso
           com string abaixo:
           Se filho for string e qual for inteiro igual a 0,
               retorna quantos filhos com este nome tem.
           Se filho for string e qual for inteiro igual a -1 (FILHO),
               cria um novo filho e adiciona a estrutura,
               util para criar filhos com mesmo nome ou a partir de string.
           Se filho for string e qual for inteiro igual a -2 (TEXTO),
               adiciona um elemento texto ao elemento chamador.
           Se filho for string e qual for inteiro igual a -3 (RAIZ),
               cria uma cópia raiz do nó.
           Se filho for string e qual for inteiro maior que 0,
               retorna o nó requerido.
           Se filho for string e qual for inteiro maior que o número de filhos
               com este nome, levanta uma exceção.
        '''
        # print '__call__', type(filho), filho, qual
        if filho is None:
            self.__pai.__filhos.append(self.__nome)
            self.__pai.__xmls.append(XML(self.__nome, self.__pai))
            return self.__pai.__xmls[-1]
        if type(filho) == int:
            return self.__pai(self.__nome, filho)
        if not (isinstance(qual, int) and (isinstance(filho, (str, unicode)) or
                isinstance(filho, (tuple, list)) and qual == RAIZ)):
            raise TypeError('Filho e qual o filho precisam ser string e'
                            ' inteiro, respectivamente.')
        if qual == FILHO:
            if len(filho) == 0:
                raise ValueError('Filho precisa ser string com pelo menos um'
                                 ' caracter para criar um novo filho.')
            self.__filhos.append(filho)
            self.__xmls.append(XML(filho, self))
            return self.__xmls[-1]
        if qual == TEXTO:
            # if len(filho) == 0:
            #     raise ValueError('Filho precisa ser string com pelo menos um'
            #                      ' caracter para criar um novo filho.')
            self.__filhos.append('')
            self.__xmls.append(filho)
            return self
        if qual == RAIZ:
            filho, i = self.__desmembrar(filho)
            no = self.__posicionar(filho, i)
            retorno = XML()
            x = retorno(filho, FILHO)
            x += no
            for ns, valor in nss(no).items():
                x[ns] = valor
            return retorno
        if qual == 0:
            if filho == '':
                return len(self.__filhos)
            return self.__filhos.count(filho)
        if filho == '':
            if 0 < qual <= len(self.__filhos):
                return self.__xmls[qual - 1]
            if qual == NOME:
                return self.__nome
            if qual == PAI:
                return self.__pai
            if qual == ATRIBUTOS:
                return zip(self.__atributos, self.__valores)
            raise IndexError('Não encontrado o ' + str(qual) + 'º filho "' +
                             filho + '" dentre o(s) ' +
                             str(len(self.__filhos)) + ' filho(s) que o nó "' +
                             self.__nome + '" possui.')
        contador = qual
        n = 0
        for n, f in enumerate(self.__filhos):
            # print f, filho, f == filho, qual
            if f == filho:
                contador -= 1
                if contador == 0:
                    return self.__xmls[n]
        caminho = self.__nome
        atual = self.__pai
        while atual.__nome:
            caminho = atual.__nome + '.' + caminho
            atual = atual.__pai
        raise IndexError('Não encontrado o ' + str(qual) + 'º filho "' +
                         filho + '" dentre o(s) ' + str(n + 1) +
                         ' filho(s) que o nó "' + caminho +
                         '" possui. Ele possui ' + str(qual - contador) +
                         ' filho(s) com este nome.')

    def __lt__(self, valor):
        if isinstance(valor, XML):
            return str(self) < str(valor)
        return str(self) < valor

    def __le__(self, valor):
        if isinstance(valor, XML):
            return str(self) <= str(valor)
        return str(self) <= valor

    def __eq__(self, valor):
        if isinstance(valor, XML):
            return str(self) == str(valor)
        return str(self) == valor

    def __ne__(self, valor):
        if isinstance(valor, XML):
            return str(self) != str(valor)
        return str(self) != valor

    def __gt__(self, valor):
        if isinstance(valor, XML):
            return str(self) > str(valor)
        return str(self) > valor

    def __ge__(self, valor):
        if isinstance(valor, XML):
            return str(self) >= str(valor)
        return str(self) >= valor


def importar(xml, html=False):
    def _importar(pai, elemento):
        # print 'type....:', type(elemento)
        # print 'elemento:', elemento
        # print 'tag.....:', elemento.tag
        # print 'nsmap...:', elemento.nsmap
        # print 'attrib..:', elemento.attrib

        if isinstance(elemento, lxml.etree._Comment):
            atual = pai('!--', FILHO)
        elif isinstance(elemento, lxml.etree._ProcessingInstruction):
            atual = pai('?xml', FILHO)
        else:
            atual = pai(elemento.tag.rsplit('}', 1)[-1], FILHO)

        parent = elemento.getparent()
        if parent is not None:
            ns_pai = elemento.getparent().nsmap
        else:
            ns_pai = []

        for ns in elemento.nsmap:
            if ns in ns_pai and elemento.nsmap[ns] == ns_pai[ns]:
                continue
            if ns is None:
                atual['xmlns'] = unescape(elemento.nsmap[ns])
            else:
                atual['xmlns:' + ns] = unescape(elemento.nsmap[ns])

        for a in elemento.attrib:
            if '}' in a:
                ns, nsa = a.rsplit('}', 1)
                nss = elemento.nsmap.items()
                ns = filter(lambda x: x[1] == ns[1:], nss)[0][0]
                nsa = "%s:%s" % (ns, nsa)
            else:
                nsa = a
            atual[nsa] = elemento.attrib[a]

        if (elemento.text is not None and not
                isinstance(elemento, lxml.etree._ProcessingInstruction)):
            for texto in elemento.text.split('\n'):
                texto2 = texto.strip()
                if len(texto2):
                    atual(texto2, TEXTO)

        for filho in elemento:
            _importar(atual, filho)
            if filho.tail is not None:
                for texto in filho.tail.split('\n'):
                    texto2 = unescape(texto)
                    if len(texto2):
                        atual(texto2, TEXTO)

    xml = str(xml).lstrip('\xef\xbb\xbf')
    if xml[0] != '<' and os.path.isfile(xml):
        xml = open(xml).read().lstrip('\xef\xbb\xbf')
    if xml[0] != '<':
        raise ValueError("Arquivo ou string XML inválido,"
                         " não iniciado por `<´.")
    retorno = XML()
    if html:
        parser = lxml.etree.HTMLParser()
        doc = lxml.etree.parse(StringIO.StringIO(xml), parser)
        _importar(retorno, doc.getroot())
    else:
        doc = lxml.etree.fromstring(xml)
        _importar(retorno, doc)
    return retorno


def validar(xml, arquivo_xsd):
    '''Função que valida um XML usando lxml do Python via arquivo XSD'''
    # Carrega o esquema XML do arquivo XSD
    xsd = lxml.etree.XMLSchema(file=arquivo_xsd)
    # Converte o XML passado em XML do lxml
    xml = lxml.etree.fromstring(str(xml))
    # Verifica a validade do xml
    erros = []
    if not xsd(xml):
        # Caso tenha erros, cria uma lista de erros
        for erro in xsd.error_log:
            erros.append({
                'message': erro.message,
                'domain': erro.domain,
                'type': erro.type,
                'level': erro.level,
                'line': erro.line,
                'column': erro.column,
                'filename': erro.filename,
                'domain_name': erro.domain_name,
                'type_name': erro.type_name,
                'level_name': erro.level_name
            })
    # Retorna os erros, sendo uma lista vazia caso não haja erros
    return erros


def assinar(filho_id, atributo_id,
            arquivo_chave_pem, arquivo_certificado_pem, metodo='sha1'):
    xml = filho_id
    while (xml._XML__pai):
        xml = xml._XML__pai
    no_assinatura = filho_id._XML__pai
    # Se não existir, criar estrutura de assinatura com o atributo_id informado
    if not no_assinatura('Signature'):
        no_assinatura.Signature['xmlns'] = "http://www.w3.org/2000/09/xmldsig#"
        SignedInfo = no_assinatura.Signature.SignedInfo
        SignedInfo.CanonicalizationMethod['Algorithm'] = (
            "http://www.w3.org/TR/2001/REC-xml-c14n-20010315")
        SignedInfo.SignatureMethod['Algorithm'] = (
            "http://www.w3.org/2000/09/xmldsig#rsa-sha1" if metodo == 'sha1'
            else "http://www.w3.org/2001/04/xmldsig-more#rsa-sha256")
        if atributo_id is None or len(atributo_id) == 0:
            no_assinatura.Signature.SignedInfo.Reference['URI'] = ''
        else:
            SignedInfo.Reference['URI'] = '#' + filho_id[atributo_id]
        SignedInfo.Reference.Transforms.Transform['Algorithm'] = (
            "http://www.w3.org/2000/09/xmldsig#enveloped-signature")
        SignedInfo.Reference.Transforms.Transform()['Algorithm'] = (
            "http://www.w3.org/TR/2001/REC-xml-c14n-20010315")
        SignedInfo.Reference.DigestMethod['Algorithm'] = (
            "http://www.w3.org/2000/09/xmldsig#sha1" if metodo == 'sha1'
            else "http://www.w3.org/2001/04/xmlenc#sha256")
        SignedInfo.Reference.DigestValue
        no_assinatura.Signature.SignatureValue
        no_assinatura.Signature.KeyInfo.X509Data.X509Certificate
    # Otimizar tamanho do XML tirando espaços extras e
    # quebras de linha, salvando em um arquivo
    # open('/tmp/nao_assinado.xml', 'w').write(exportar(xml, -1))
    # Assinar o conteúdo do arquivo salvo acima e salvar o resultado em outro
    # import os
    # os.system('xmlsec1 sign --id-attr:' + atributo_id + ' ' +
    #           filho_id._XML__nome +
    #           ' --output /tmp/assinado.xml --privkey-pem ' +
    #           arquivo_chave_pem + ',' +
    #           arquivo_certificado_pem + ' /tmp/nao_assinado.xml')
    # del os
    # Recarregar o xml assinado e retorná-lo
    # return (open('/tmp/assinado.xml').read().
    #         replace('\r', '').replace('\n', ''))
    xml_assinado = PoleXmlSec.sign(serializar(xml), arquivo_chave_pem,
                                   arquivo_certificado_pem, atributo_id,
                                   filho_id._XML__nome)
    xml_assinado = xml_assinado.replace('\r', '').replace('\n', '')
    xml_assinado = importar(xml_assinado)
    caminho = ['Signature']
    pai = no_assinatura
    while pai._XML__nome is not None:
        caminho.append(pai._XML__nome)
        pai = pai._XML__pai
    assinatura = xml_assinado
    for c in caminho[::-1]:
        assinatura = assinatura(c, 1)
    no_assinatura.Signature.SignedInfo.Reference.DigestValue = (
        assinatura.SignedInfo.Reference.DigestValue)
    no_assinatura.Signature.SignatureValue = assinatura.SignatureValue
    no_assinatura.Signature.KeyInfo.X509Data.X509Certificate = (
        assinatura.KeyInfo.X509Data.X509Certificate)
    return xml


def verificar_assinatura(filho_id, atributo_id, certificadoras=''):
    # certificadoras -> lista de arquivos e/ou diretório
    # separados por ponto e vígula (;)
    xml = filho_id
    while (xml._XML__pai):
        xml = xml._XML__pai
    return (PoleXmlSec.verify(serializar(xml),
            atributo_id, filho_id._XML__nome, certificadoras) == 1)


def escape(string):
    if type(string) == unicode:
        string = string.encode('utf-8')
    return (str(string).strip().replace('&', '&amp;').replace('<', '&lt;').
            replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;'))

# def unescape(string):
#     if type(string) == unicode:
#         string = string.encode('utf-8')
#     return (str(string).strip().replace('&amp;', '&').replace('&lt;', '<').
#            replace('&gt;', '>').replace('&quot;', '"').replace('&#39;', "'"))


def unescape(s):
    want_unicode = isinstance(s, unicode)
    if want_unicode:
        s = s.encode("utf-8")
    # the rest of this assumes that `s` is UTF-8
    list = []
    # create and initialize a parser object
    p = xml.parsers.expat.ParserCreate("utf-8")
    p.buffer_text = True
    p.returns_unicode = want_unicode
    p.CharacterDataHandler = list.append
    # parse the data wrapped in a dummy element
    # (needed so the "document" is well-formed)
    p.Parse("<e>", 0)
    p.Parse(s.strip(), 0)
    p.Parse("</e>", 1)
    # join the extracted strings and return
    return (u"" if want_unicode else "").join(list)


def nss(no):
    pai = no
    xml_nss = {}
    while pai:
        for atributo, valor in zip(pai._XML__atributos, pai._XML__valores):
            if atributo[:5] == 'xmlns' and atributo not in xml_nss:
                xml_nss[atributo] = valor
        pai = pai._XML__pai
    return xml_nss


def exportar(xml, endentacao=4, nivel=0,
             com_marca_xml=True, escapado=True, herdar_namespaces=True):
    '''Exporta um XML com alguns ajustes,
    sendo que endentação negativa fica tudo numa linha só, sem quebra.'''
    def _exportar(xml, endentacao, nivel):
        if endentacao < 0:
            dente = ''
            quebra = ''
        else:
            dente = ' ' * endentacao * nivel
            quebra = '\n'
        conteudo = ''
        for nome_filho, xml_filho in zip(xml._XML__filhos, xml._XML__xmls):
            if xml_filho is None or (isinstance(xml_filho, (str, unicode)) and
                                     xml_filho == ''):
                continue
            if isinstance(xml_filho, XML):
                atributos = ''
                ns = ''
                for atributo, valor in zip(xml_filho._XML__atributos,
                                           xml_filho._XML__valores):
                    if atributo == ':ns':
                        ns = valor + ':'
                    else:
                        atributos += (' ' + atributo + '="' +
                                      _escape(valor) + '"')
                netos = _exportar(xml_filho, endentacao, nivel + 1)
                if len(netos):
                    if nome_filho == '!--':
                        conteudo += dente + '<!-- ' + netos + ' -->' + quebra
                    else:
                        conteudo += (dente + '<' + ns + nome_filho +
                                     atributos + '>' +
                                     (netos, quebra + netos + dente)
                                     [netos.count('<') > 0 or
                                      netos.count('\n') > 1] +
                                     '</' + ns + nome_filho + '>' + quebra)
                else:
                    if nome_filho == '?xml':
                        conteudo += dente + '<?xml' + atributos + '?>' + quebra
                    else:
                        conteudo += (dente + '<' + ns + nome_filho +
                                     atributos + '/>' + quebra)
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
    xml_nss = nss(xml) if herdar_namespaces else {}
    exportado = _exportar(xml, endentacao, nivel)
    if xml_nss and exportado and exportado[0] == '<':
        p1 = exportado.find('>')
        p = min(p1, exportado.find(' ')) if ' ' in exportado else p1
        xml_nss = ''.join(' %s="%s"' % x for x in xml_nss.items()
                          if ' ' + x[0] + '=' not in exportado[p:p1])
        exportado = exportado[:p] + xml_nss + exportado[p:]
    if com_marca_xml:
        return (' ' * endentacao * nivel * (endentacao > 0) +
                MARCA_XML + '\n' * (endentacao > 0) + exportado)
    return exportado


def serializar(xml):
    return exportar(xml, -1)


def procurar(xml, nome_no, atributos=None, todos=False):
    if not isinstance(nome_no, (list, tuple, dict)):
        nome_no = [nome_no]
    retorno = []
    for nome_filho, xml_filho in zip(xml._XML__filhos, xml._XML__xmls):
        if nome_filho in nome_no:
            if not atributos:
                retorno.append(xml_filho)
                continue
            encontrados = 0
            for xatributo, xvalor in zip(xml_filho._XML__atributos,
                                         xml_filho._XML__valores):
                if isinstance(atributos, dict):
                    if (xatributo in atributos and
                            atributos[xatributo] == xvalor):
                        encontrados += 1
                        break
                elif isinstance(atributos[0], (list, tuple)):
                    if (xatributo, xvalor) in (tuple(x) for x in atributos):
                        encontrados += 1
                        break
                else:
                    if xatributo in atributos:
                        encontrados += 1
                        break
            if (todos and encontrados == len(atributos) or not
                    todos and encontrados):
                retorno.append(xml_filho)
        if isinstance(xml_filho, XML):
            retorno += procurar(xml_filho, nome_no, atributos)
    return retorno


complex_types = {}
grupo_escolha = 0


def add_attrs(dest, orig, filtro):
    pai = orig('', PAI)
    herdar = ['sequence']
    pai = (pai('', ATRIBUTOS) if pai('', NOME) in herdar
           else [])
    for a, v in orig('', ATRIBUTOS) + pai:
        if a in filtro:
            dest[a] = v


def _xsd_to_xml(xsd, xml, escolha=''):
    global grupo_escolha
    for num in range(1, xsd('', 0) + 1):
        filho = xsd('', num)
        if isinstance(filho, (str, unicode)):
            xml['texto'] = filho
            return
        nome = filho('', NOME)
        if nome in ['element', 'any', 'attribute']:
            nome_filho = (filho['name'] if filho['name']
                          else filho['ref'].rsplit(':', 1)[-1] if filho['ref']
                          else nome)
            if nome == 'attribute':
                nome_filho = '_' + nome_filho
            y = xml(nome_filho, FILHO)
            add_attrs(y, filho, ['minOccurs', 'maxOccurs', 'use'])
            if escolha:
                y['grpEscolha'] = escolha
            if filho['type']:
                type_name = filho['type'].rsplit(':', 1)[-1]
                y['tipo'] = type_name
                if type_name in complex_types:
                    assert complex_types[type_name], Exception(
                        "For type `" + xsd('', PAI)['name'] + "´ yet not found"
                        " the complex type: " + type_name)
                    y += importar('<x>'+str(complex_types[type_name])+'</x>').x
            _xsd_to_xml(filho, y)
            continue
        if nome == 'restriction':
            xml['tipo'] = filho['base'].rsplit(':', 1)[-1]
            enumeration = []
            for num_restr in range(1, filho('', 0) + 1):
                f_restr = filho('', num_restr)
                nome_restr = f_restr('', NOME)
                if nome_restr == 'enumeration':
                    enumeration.append(f_restr['value'])
                else:
                    xml[nome_restr] = f_restr['value']
            if enumeration:
                xml['enumeration'] = '|'.join(enumeration)
            continue
        if nome == 'choice':
            grupo_escolha += 1
            escolha = str(grupo_escolha)
        else:
            escolha = ''
        _xsd_to_xml(filho, xml, escolha)


def xsd_complex_types(xsd, debug=False):
    global complex_types
    lista = procurar(xsd, 'complexType', ['name'])
    complex_types.update({x['name']: None for x in lista})
    for complex_type in lista:
        # print complex_type['name']
        xml = XML()
        try:
            _xsd_to_xml(complex_type, xml)
            # print repr(xml)
            # print '-' * 100
            complex_types[complex_type['name']] = xml
        except Exception as e:
            if debug:
                print e
            del xml
            lista.append(complex_type)


def xsd_to_xml(xsd):
    if not isinstance(xsd, XML):
        xsd = importar(xsd)
    xsd_complex_types(xsd)
    root_name = xsd.schema.element['name']
    xml = XML()
    xml(root_name, FILHO)['xmlns'] = xsd.schema['targetNamespace']
    _xsd_to_xml(xsd.schema.element, xml(root_name, 1))
    return xml


def eliminar_vazios(xml):
    if not isinstance(xml, XML):
        return str(xml) == ''
    if not xml(''):
        return True
    for i in range(xml(''), 0, -1):
        remover = eliminar_vazios(xml('', i))
        if remover:
            xml - ('', i)
    return xml('') == 0
