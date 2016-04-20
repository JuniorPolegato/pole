#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""PoleNFe - Operações com Nota Fiscal Eletrônica em Python

Arquivo: PoleNFe.py
Versão.: 0.2.1
Autor..: Claudio Polegato Junior
Data...: 22 Mar 2011

Copyright © 2011 - Claudio Polegato Junior <junior@juniorpolegato.com.br>
Todos os direitos reservados
"""

# Módulo do sistema utilizados no programa
import os
import sys
import time
import datetime
import pytz

# Módulos SUDS utilizados no programa
import suds.client
import suds.xsd.doctor
import suds.xsd.sxbasic
import suds.transport.http
import suds.bindings.binding
from suds.sax.element import Element as E

# Debug
# import logging
# logging.basicConfig(level=logging.INFO)
# logging.getLogger('suds.client').setLevel(logging.DEBUG)

# Módulo feito por Junior Polegato em CPython para assinar XML
import PoleXML

# Net
import socket
import httplib
import urllib2
import ssl

# Conversão
import PoleUtil
cf = PoleUtil.convert_and_format

# Constantes
PRODUCAO = 1
HOMOLOGACAO = 2

UFS_IBGE = {
    'AC': '12', 'CE': '23', 'MG': '31', 'PE': '26', 'RO': '11', 'SP': '35',
    'AL': '27', 'DF': '53', 'MS': '50', 'PI': '22', 'RR': '14', 'TO': '17',
    'AM': '13', 'ES': '32', 'MT': '51', 'PR': '41', 'RS': '43', 'AN': '91',
    'AP': '16', 'GO': '52', 'PA': '15', 'RJ': '33', 'SC': '42',
    'BA': '29', 'MA': '21', 'PB': '25', 'RN': '24', 'SE': '28'}

UFS_SIGLAS = {'AC': 'Acre',               'PA': 'Pará',
              'AL': 'Alagoas',            'PB': 'Paraíba',
              'AM': 'Amazonas',           'PE': 'Pernambuco',
              'AP': 'Amapá',              'PI': 'Piauí',
              'BA': 'Bahia',              'PR': 'Paraná',
              'CE': 'Ceará',              'RJ': 'Rio de Janeiro',
              'DF': 'Distrito Federal',   'RN': 'Rio Grande do Norte',
              'ES': 'Espírito Santo',     'RO': 'Rondônia',
              'GO': 'Goiás',              'RR': 'Roraima',
              'MA': 'Maranhão',           'RS': 'Rio Grande do Sul',
              'MG': 'Minas Gerais',       'SC': 'Santa Catarina',
              'MS': 'Mato Grosso do Sul', 'SE': 'Sergipe',
              'MT': 'Mato Grosso',        'SP': 'São Paulo',
                                          'TO': 'Tocantins'}

# UF que utilizam a SVAN - Sefaz Virtual do Ambiente Nacional: MA, PA, PI
#
# UF que utilizam a SVRS - Sefaz Virtual do RS:
# - Para demais serviços relacionados com o sistema da NF-e: AC, AL, AP, DF,
#                                        ES, PB, RJ, RN, RO, RR, SC, SE, TO

SEFAZ = {'AC': 'SVRS',     'PA': 'SVAN',
         'AL': 'SVRS',     'PB': 'SVRS',
         'AM': 'AM',       'PE': 'PE',
         'AP': 'SVRS',     'PI': 'SVAN',
         'BA': 'BA',       'PR': 'PR',
         'CE': 'CE',       'RJ': 'SVRS',
         'DF': 'SVRS',     'RN': 'SVRS',
         'ES': 'SVRS',     'RO': 'SVRS',
         'GO': 'GO',       'RR': 'SVRS',
         'MA': 'SVAN',     'RS': 'RS',
         'MG': 'MG',       'SC': 'SVRS',
         'MS': 'MS',       'SE': 'SVRS',
         'MT': 'MT',       'SP': 'SP',
                           'TO': 'SVRS'}

# Não operacional para SVRS para UFs: AL, AP, DF, RJ, RO, RR, SE, TO
# Não operacional para SVAN para UFs: PA, PI
#
# UF que utilizam a SVRS - Sefaz Virtual do RS:
# - Para serviço de Consulta Cadastro: AC, RN, PB, SC

SEFAZ_CONSULTA = {'AC': 'SVRS',     'PA': 'SVAN',
                  'AL': 'SVRS',     'PB': 'SVRS',
                  'AM': 'AM',       'PE': 'PE',
                  'AP': 'SVRS',     'PI': 'SVAN',
                  'BA': 'BA',       'PR': 'PR',
                  'CE': 'CE',       'RJ': 'SVRS',
                  'DF': 'SVRS',     'RN': 'SVRS',
                  'ES': 'ES',       'RO': 'SVRS',
                  'GO': 'GO',       'RR': 'SVRS',
                  'MA': 'MA',       'RS': 'RS',
                  'MG': 'MG',       'SC': 'SVRS',
                  'MS': 'MS',       'SE': 'SVRS',
                  'MT': 'MT',       'SP': 'SP',
                                    'TO': 'SVRS'}

# Autorizadores em contingência:
# - UF que utilizam a SVC-AN - Sefaz Virtual de Contingência Ambiente Nacional:
#               AC, AL, AP, DF, ES, MG, PB, RJ, RN, RO, RR, RS, SC, SE, SP, TO
# - UF que utilizam a SVC-RS - Sefaz Virtual de Contingência Rio Grande do Sul:
#                                   AM, BA, CE, GO, MA, MS, MT, PA, PE, PI, PR

SEFAZ_CONTINGENCIA = {'AC': 'SVC-AN', 'AL': 'SVC-AN', 'AM': 'SVC-RS',
                      'AP': 'SVC-AN', 'BA': 'SVC-RS', 'CE': 'SVC-RS',
                      'DF': 'SVC-AN', 'ES': 'SVC-AN', 'GO': 'SVC-RS',
                      'MA': 'SVC-RS', 'MG': 'SVC-AN', 'MS': 'SVC-RS',
                      'MT': 'SVC-RS', 'PA': 'SVC-RS', 'PB': 'SVC-AN',
                      'PE': 'SVC-RS', 'PI': 'SVC-RS', 'PR': 'SVC-RS',
                      'RJ': 'SVC-AN', 'RN': 'SVC-AN', 'RO': 'SVC-AN',
                      'RR': 'SVC-AN', 'RS': 'SVC-AN', 'SC': 'SVC-AN',
                      'SE': 'SVC-AN', 'SP': 'SVC-AN', 'TO': 'SVC-AN'}

EVENTOS = {
    # 'Envento': ('Cód. Evento', 'xsd', evento maiúsculo, 'xsd de envio')
    'Carta de Correcao': ('110110', 'CCe', False,
                          'envCCe'),
    'Cancelamento': ('110111', 'eventoCancNFe', False,
                     'envEventoCancNFe'),
    'Confirmacao da Operacao': ('210200', 'confRecebto', True,
                                'envConfRecebto'),
    'Ciencia da Operacao': ('210210', 'confRecebto', True, 'envConfRecebto'),
    'Desconhecimento da Operacao': ('210220', 'confRecebto', True,
                                    'envConfRecebto'),
    'Operacao nao Realizada': ('210240', 'confRecebto', True,
                               'envConfRecebto')
}

TODAS = 0
SEM_CONFIRMACAO_MANIFESTACAO = 1
SEM_MANIFESTACAO = 2


def print_req(req):
    print req.__dict__
    # print 'req.add_data(data):', req.add_data(data)
    print 'req.get_method():', req.get_method()
    print 'req.has_data():', req.has_data()
    print 'req.get_data():', req.get_data()
    # print 'req.add_header(key, val):', req.add_header(key, val)
    # print ('req.add_unredirected_header(key, header):',
    #        req.add_unredirected_header(key, header)
    # print 'req.has_header(header):', req.has_header(header)
    print 'req.get_full_url():', req.get_full_url()
    print 'req.get_type():', req.get_type()
    print 'req.get_host():', req.get_host()
    print 'req.get_selector():', req.get_selector()
    # print ('req.get_header(header_name, default=None):',
    #        req.get_header(header_name, default=None)
    print 'req.header_items():', req.header_items()
    # print 'req.set_proxy(host, type):', req.set_proxy(host, type)
    print 'req.get_origin_req_host():', req.get_origin_req_host()
    print 'req.is_unverifiable():', req.is_unverifiable()


def test_ssl_connection():
    import socket
    import ssl
    import pprint

    cnpj = '11222333000101'
    home_cnpjs = '/home/junior/NFe/cnpjs/'
    key_file = '%s%s/certificado_digital/chave.pem' % (home_cnpjs, cnpj)
    cert_file = '%s%s/certificado_digital/certificado.pem' % (home_cnpjs, cnpj)
    ca_file = '/home/junior/NFe/certificadoras/certificadoras.crt'
    host = 'homologacao.nfe.fazenda.sp.gov.br'
    uri = '/nfeweb/services/nferecepcao2.asmx?wsdl'
    port = 443
    timeout = 90
    source_address = None

    s = socket.create_connection((host, port), timeout, source_address)
    ssl_sock = ssl.wrap_socket(s, key_file, cert_file,
                               ssl_version=ssl.PROTOCOL_SSLv3,
                               ca_certs=ca_file, cert_reqs=ssl.CERT_REQUIRED)

    print repr(ssl_sock.getpeername())
    print ssl_sock.cipher()
    print pprint.pformat(ssl_sock.getpeercert())

    # Set a simple HTTP request
    ssl_sock.write("GET %s HTTP/1.0\r\nHost: %s\r\n\r\n" % (uri, host))

    # Read chunks of data.
    data = ''
    chunk = ssl_sock.read()
    while chunk:
        data += chunk
        chunk = ssl_sock.read()
    print data

    # note that closing the SSLSocket will also close the underlying socket
    ssl_sock.close()

    raw_input('-' * 100)


# Classes para prover camada de transporte com conexão HTTPS/SSL
# Não suportada nativamente pelo Suds
# Inspirado em http://www.threepillarglobal.com/soap_client_auth
class HTTPSConnection(httplib.HTTPConnection):
    default_port = 443

    def __init__(self, host, port=None, key_file=None, cert_file=None,
                 strict=None, timeout=10,
                 source_address=None, ca_certs=None):
        httplib.HTTPConnection.__init__(self, host, port, strict, timeout,
                                        source_address)
        self.key_file = key_file
        self.cert_file = cert_file
        self.ca_certs = ca_certs

    def connect(self):
        sock = socket.create_connection((self.host, self.port), self.timeout,
                                        self.source_address)
        if self._tunnel_host:
            self.sock = sock
            self._tunnel()
        self.sock = ssl.wrap_socket(sock, self.key_file, self.cert_file,
                                    ssl_version=ssl.PROTOCOL_TLSv1,  # SSLv23,
                                    ca_certs=self.ca_certs,
                                    cert_reqs=ssl.CERT_REQUIRED)


class https_ssl(urllib2.HTTPSHandler):
    def __init__(self, key_file, cert_file, ca_file):
        urllib2.HTTPSHandler.__init__(self)
        self.key_file = key_file
        self.cert_file = cert_file
        self.ca_file = ca_file
        self.protocol = 2

    def https_open(self, req):
        return self.do_open(self.conexao, req)

    def conexao(self, host, timeout=None):
        # Na versão do httplib do servidor o HTTPSConnection funciona Ok,
        # e este que criei não, então tem que usar "httplib.HTTPSConnection"
        # para rodar no servidor com versões antigas.
        # Na versão atual de 16 Jul 2013, "httplib.HTTPSConnection" funciona.
        # Para maior segurança, utilizar HTTPSConnection acima por fazer uso
        # de autoridade certificadora.
        return HTTPSConnection(host, timeout=timeout, key_file=self.key_file,
                               cert_file=self.cert_file, ca_certs=self.ca_file)


# Sobrescrita a função "str" de Element (E) para não endentar nem quebrar linha
# Pelo menos o servidor de SP não aceita caracteres entre as marcas, erro 588
# Esse código foi retirado de uma versão mais nova do E da função "plain":
# http://jortel.fedorapeople.org/suds/doc/suds.sax.element-pysrc.html#Element.plain
# Foi colocado o parâmetro "indent", porém ignorado,
# para compatilidade com a função "str"
# A sobrescrita ocorre após o código com E.str = __plain,
# sendo a antiga em "__str_indent"
def __plain(self, indent=0):
    # Se estiver com a versão que já tem o "plain", pode usar este, porém terá
    # o problema em algumas SEFAZ com o cabeçalho do SOAP por não aceitarem,
    # tns:<tag>, descomente a linha abaixo
    # return self.plain()
    result = []
    qname = self.qname()
    ns = self.nsdeclarations()
    if qname == 'tns:nfeCabecMsg':
        tns = self.parent.parent.nsdeclarations().split('xmlns:tns="')[1]
        tns = ' xmlns="%s"' % tns.split('"')[0]
        ns += tns
    if qname[:4] == 'tns:':
        qname = qname[4:]
    result.append('<%s' % qname)
    result.append(ns)
    for a in [unicode(a) for a in self.attributes]:
        result.append(' %s' % a)
    if self.isempty():
        result.append('/>')
        return ''.join(result)
    result.append('>')
    if self.hasText():
        result.append(self.text.escape())
    for c in self.children:
        result.append(c.str())
    result.append('</%s>' % qname)
    result = ''.join(result)
    return result


def __str_indent(self, indent=0):
    tab = '%*s' % (indent * 4, '')
    result = []
    result.append('%s<%s' % (tab, self.qname()))
    result.append(self.nsdeclarations())
    for a in [unicode(a) for a in self.attributes]:
        result.append(' %s' % a)
    if self.isempty():
        result.append('/>')
        return ''.join(result)
    result.append('>')
    if self.hasText():
        result.append(self.text.escape())
    for c in self.children:
        result.append('\n')
        result.append(c.str_indent(indent+1))
    if len(self.children):
        result.append('\n%s' % tab)
    result.append('</%s>' % self.qname())
    result = ''.join(result)
    return result
E.str_indent = __str_indent
E.str = __plain


class Webservice(object):
    '''Classe que realiza todas operações com o Webservice para tratamento da NFe.
       Parâmetros:
       ambiemte: inteiro (ou constante) 1 (PRODUCAO) ou 2 (HOMOLOGACAO)
       cnpj: CNPJ a ser procurado nos diretórios, ou uma string identificadora
       uf: UF a ser procurada nos diretórios e nas lista constante UFS_IBGE
       pacote: string com nome do diretório que contém o "Package Language"
       raiz: diretório que vai conter a estrutura de diretórios e arquivos para
             o Webservice, sendo padrão ${HOME}/NFe
       ${HOME}/NFe
       |---> certificadoras
       |     |---> certificado1.crt
       |     |---> certificado2.crt
       |     \---> ...
       |---> cnpjs
       |     |---> cnpj_ou_identificador_1
       |     |     |---> certificado_digital
       |     |     |     |---> chave.pem
       |     |     |     \---> certificado.pem
       |     |     |---> homologacao
       |     |     |     |---> nfe           ---> XMLs assinados e protocolados
       |     |     |     |---> danfe         ---> PDFs
       |     |     |     |---> inutilizacao  ---> XMLs assinados e protocolados
       |     |     |     \---> cancelamento  ---> XMLs assinados e protocolados
       |     |     \---> producao
       |     |           |---> nfe
       |     |           |---> danfe
       |     |           |---> inutilizacao
       |     |           \---> cancelamento
       |     |---> cnpj_ou_identificador_2
       |     |     \---> ...
       |     \---> ...
       |---> wsdl
       |     |---> sefaz_1
       |     |     |---> homologacao
       |     |     |     |---> 1.00
       |     |     |     |     |---> NfeDistribuicaoDFe.wsdl
       |     |     |     |     |---> RecepcaoEvento.wsdl
       |     |     |     |---> 2.00
       |     |     |     |     |---> NfeConsultaCadastro.wsdl
       |     |     |     |     |---> NfeConsultaProtocolo.wsdl
       |     |     |     |     |---> NfeInutilizacao.wsdl
       |     |     |     |     |---> NfeRecepcao.wsdl
       |     |     |     |     |---> NfeRetRecepcao.wsdl
       |     |     |     |     |---> NfeStatusServico.wsdl
       |     |     |     |     \---> RecepcaoEvento.wsdl
       |     |     |     \---> 3.10
       |     |     |           |---> NfeAutorizacao.wsdl
       |     |     |           |---> NfeConsultaCadastro.wsdl
       |     |     |           |---> NfeConsultaProtocolo.wsdl
       |     |     |           |---> NfeInutilizacao.wsdl
       |     |     |           |---> NfeRetAutorizacao.wsdl
       |     |     |           |---> NfeStatusServico.wsdl
       |     |     |           \---> RecepcaoEvento.wsdl
       |     |     \---> producao
       |     |           |---> ... (estrutura tal como homologacao)
       |     |           \---> ...
       |     |---> sefaz_2
       |     |     \---> ... (tal como sefaz_1)
       |     \---> ... (outras sefaz)
       \---> xsd
             |---> PL (geralmente link simbólico para o PL mais atual)
             |     |---> nfe_v2.00.xsd
             |     |---> ... (incluir link simbólicos para os eventos)
             |     \---> tiposBasico_v1.03.xsd
             \---> ... (outras versões de pacotes)
'''

    def __init__(self, cnpj, ambiente=PRODUCAO, uf='SP', sefaz=None, raiz=None,
                 pacote='PL', contingencia=False):
        if uf not in UFS_IBGE:
            raise ValueError('UF ' + str(uf) + ' inválida!')
        if sefaz is None:
            if contingencia:
                sefaz = SEFAZ_CONTINGENCIA[uf]
            else:
                sefaz = SEFAZ[uf]
        if ambiente not in (1, 2):
            raise ValueError('Ambiente ' + str(ambiente) + ' inválido!')
        self.__uf = uf
        self.__sefaz = sefaz
        self.__cnpj = cnpj
        self.__ambiente = ambiente
        self.__str_ambiente = ('producao', 'homologacao')[ambiente - 1]
        if raiz is None:
            self.__raiz = os.getenv("HOME") + '/NFe'
        else:
            self.__raiz = raiz
        self.__pacote = pacote
        # Caminho do certificado digital
        self.__chave = ('%s/cnpjs/%s/certificado_digital/chave.pem'
                        % (self.__raiz, self.__cnpj))
        self.__certificado = ('%s/cnpjs/%s/certificado_digital/certificado.pem'
                              % (self.__raiz, self.__cnpj))
        self.__certificadoras = ('%s/certificadoras/certificadoras.crt'
                                 % self.__raiz)

    def __cabecalho(self, cliente, versao_dados):
        cabecalho = cliente.factory.create('nfeCabecMsg')
        cabecalho.cUF = UFS_IBGE[self.__uf]
        cabecalho.versaoDados = versao_dados
        return cabecalho

    def servico(self, nome_wsdl, xml, nome_xsd=None, versao_wsdl=None):
        # Validar xml para envio
        if not self.validar(xml, nome_xsd):
            erros = "Erro(s) no XML: "
            for erro in self.erros:
                erros += erro['type_name'] + ': ' + erro['message']
            raise ValueError(erros)
        # Versões do XML e do WSDL
        versao_xml = xml('', 1)['versao'] or xml('', 1)('', 1)['versao']
        if not versao_wsdl:
            versao_wsdl = versao_xml
        # Carrega o wsdl da estrutura de arquivos pela versão do WSDL
        # <raiz>/wsdl/<sefaz>/<ambiente>/<versao>/<nome_wsdl>.wsdl
        arquivo_wsdl = os.path.join(self.__raiz, 'wsdl', self.__sefaz,
                                    self.__str_ambiente, versao_wsdl,
                                    nome_wsdl + '.wsdl')
        # Se não encontrou pela versão do WSDL especificada, vai pela do XML
        if not os.path.exists(arquivo_wsdl):
            arquivo_wsdl = os.path.join(
                self.__raiz, 'wsdl', self.__sefaz,
                self.__str_ambiente, versao_xml, nome_wsdl + '.wsdl')
        arquivo_wsdl = 'file://' + arquivo_wsdl
        # Criar meio de transporte criptografado
        transporte = suds.transport.http.HttpTransport()
        transporte_ssl = https_ssl
        transporte.urlopener = urllib2.build_opener(
            transporte_ssl(key_file=self.__chave, cert_file=self.__certificado,
                           ca_file=self.__certificadoras))
        wsdl = suds.client.Client(arquivo_wsdl, transport=transporte)
        # Configurar o ambiente do SOAP 1.2
        wsdl.options.cache.clear()
        ns_anterior = suds.bindings.binding.envns
        suds.bindings.binding.envns = (
            'soap12', 'http://www.w3.org/2003/05/soap-envelope')
        # Cria uma função do primeiro serviço, primeira URL (port)
        # e primeiro método, visto que são únicos
        funcao = suds.client.Method(wsdl, wsdl.wsdl.
                                    services[0].ports[0].methods.values()[0])
        # Configura os headers http para SOAP 1.2, o cabeçalho e retorno em XML
        wsdl.set_options(soapheaders=self.__cabecalho(wsdl, versao_xml),
                         headers={'Content-Type':
                                  'application/soap+xml; charset=utf-8'},
                         retxml=True)
        # Na versão do servidor não tem o parâmetro prettyxml,
        # então tem que comentá-lo para rodar lá
        if sys.version_info.major > 2 or sys.version_info.minor > 6:
            wsdl.set_options(prettyxml=True)
        # Executa a função e coleta o resultado em XML
        resultado = funcao(suds.sax.parser.Parser().parse(
                           string=PoleXML.serializar(xml)).root())
        # Voltando o ambiente do SOAP
        suds.bindings.binding.envns = ns_anterior
        # Retornar o resultado na forma da classe XML,
        # somente o corpo do envelope Soap
        return PoleXML.importar(resultado).Envelope.Body('', 1)

    def status(self):
        consulta = PoleXML.XML()
        consulta.consStatServ['xmlns'] = 'http://www.portalfiscal.inf.br/nfe'
        consulta.consStatServ['versao'] = '3.10'
        consulta.consStatServ.tpAmb = self.__ambiente
        consulta.consStatServ.cUF = UFS_IBGE[self.__uf]
        consulta.consStatServ.xServ = 'STATUS'
        return self.servico('NfeStatusServico', consulta)

    def consultar_chave(self, chave):
        if chave[:2] == UFS_IBGE[self.__uf]:
            ws_consulta = self
        else:
            uf_consulta = dict([x[::-1] for x in UFS_IBGE.items()])[chave[:2]]
            ws_consulta = Webservice(self.__cnpj, self.__ambiente,
                                     uf_consulta, uf_consulta, self.__raiz,
                                     self.__pacote)
        consulta = PoleXML.XML()
        consulta.consSitNFe['xmlns'] = 'http://www.portalfiscal.inf.br/nfe'
        consulta.consSitNFe['versao'] = '3.10'
        consulta.consSitNFe.tpAmb = self.__ambiente
        consulta.consSitNFe.xServ = 'CONSULTAR'
        consulta.consSitNFe.chNFe = chave
        return ws_consulta.servico('NfeConsultaProtocolo', consulta)

    def consultar_num_nota(self, num_nota):
        for ano in range(datetime.date.today().year % 100, 5, -1):
            chave = (str(UFS_IBGE[self.__uf]) + '%02d' % ano + '09' +
                     self.__cnpj + '55001' + '%09d' % num_nota + '7825541981')
            retorno = self.consultar_chave(chave)
            if retorno.retConsSitNFe.cStat < '200':
                return retorno
            if str(retorno.retConsSitNFe.cStat) == '562':
                chave = str(retorno.retConsSitNFe.xMotivo)[-45:-1]
                retorno = self.consultar_chave(chave)
                break
            if str(retorno.retConsSitNFe.cStat) == '561':
                chave = chave[:34] + str(int(chave[-10:]) + 1000)[-10:]
                retorno = self.consultar_chave(chave)
                if retorno.retConsSitNFe.cStat == '562':
                    chave = str(retorno.retConsSitNFe.xMotivo)[-45:-1]
                    retorno = self.consultar_chave(chave)
                    break
        return retorno

    def cancelar_chave(self, justificativa, chave_nfe, protocolo=None):
        if not protocolo:
            consulta = self.consultar_chave(chave_nfe)
            protocolo = str(consulta.retConsSitNFe.protNFe.infProt.nProt)
        cancelamento = PoleXML.XML()
        # cancelamento.cancNFe['xmlns'] = 'http://www.portalfiscal.inf.br/nfe'
        # cancelamento.cancNFe['versao'] = '2.00'
        # cancelamento.cancNFe.infCanc['Id'] = 'ID' + chave_nfe
        # cancelamento.cancNFe.infCanc.tpAmb = self.__ambiente
        # cancelamento.cancNFe.infCanc.xServ = 'CANCELAR'
        # cancelamento.cancNFe.infCanc.chNFe = chave_nfe
        # cancelamento.cancNFe.infCanc.nProt = protocolo
        # cancelamento.cancNFe.infCanc.xJust = justificativa
        # self.assinar(cancelamento, cancelamento.cancNFe.infCanc)
        # recibo = self.servico('NfeCancelamento2', cancelamento)
        # retorno = PoleXML.XML()
        # retorno.procCancNFe['xmlns'] = 'http://www.portalfiscal.inf.br/nfe'
        # retorno.procCancNFe['versao'] = '2.00'
        # retorno.procCancNFe.cancNFe = cancelamento.cancNFe
        # retorno.procCancNFe.retCancNFe = recibo.retCancNFe
        # return retorno
        cancelamento.nProt = protocolo
        cancelamento.xJust = justificativa
        return self.enviar_envento('Cancelamento', chave_nfe,
                                   datetime.datetime.now(), 1, cancelamento)

    def cancelar_num_nota(self, justificativa, num_nota):
        consulta = self.consultar_num_nota(num_nota)
        return self.cancelar_chave(justificativa, consulta["chNFe"],
                                   consulta["protNFe"]["infProt"]["nProt"])

    def inutilizar(self, justificativa, ano, numero_inicial,
                   numero_final=None, serie=1):
        if numero_final is None:
            numero_final = numero_inicial
        inutilizacao = PoleXML.XML()
        inutilizacao.inutNFe['xmlns'] = 'http://www.portalfiscal.inf.br/nfe'
        inutilizacao.inutNFe['versao'] = '3.10'
        # Id = Código da UF + Ano (2 posições) + CNPJ + modelo + série +
        # nro inicial e nro final, precedida do literal “ID”
        inutilizacao.inutNFe.infInut['Id'] = ('ID%s%02i%s55%03i%09i%09i' %
                                              (UFS_IBGE[self.__uf],
                                               int(ano) % 100, self.__cnpj,
                                               int(serie), int(numero_inicial),
                                               int(numero_final)))
        inutilizacao.inutNFe.infInut.tpAmb = self.__ambiente
        inutilizacao.inutNFe.infInut.xServ = 'INUTILIZAR'
        inutilizacao.inutNFe.infInut.cUF = UFS_IBGE[self.__uf]
        inutilizacao.inutNFe.infInut.ano = int(ano) % 100
        inutilizacao.inutNFe.infInut.CNPJ = self.__cnpj
        inutilizacao.inutNFe.infInut.mod = 55
        inutilizacao.inutNFe.infInut.serie = serie
        inutilizacao.inutNFe.infInut.nNFIni = numero_inicial
        inutilizacao.inutNFe.infInut.nNFFin = numero_final
        inutilizacao.inutNFe.infInut.xJust = justificativa
        self.assinar(inutilizacao.inutNFe.infInut)
        return self.servico('NfeInutilizacao', inutilizacao)

    def enviar_envento(self, descr_evento, chave_nfe, data_hora_evento,
                       qtd_mesmo_evento, xml_adicional):
        dh = cf(data_hora_evento, datetime.datetime)[0]
        cod_evento, xsd_evento, ev_maiusculo, xsd_envio = EVENTOS[descr_evento]
        # tz = time.altzone if time.daylight else time.timezone
        # tz = '%c%02i:%02i' % ('-' if tz > 0 else '+', tz/3600, tz/60%60)
        # dh = dh.strftime('%Y-%m-%dT%H:%M:%S') + tz
        tz = pytz.timezone(open('/etc/timezone').read().strip())
        dh = tz.localize(dh).strftime('%Y-%m-%dT%H:%M:%S%z')
        dh = dh[:-2] + ':' + dh[-2:]
        evento = PoleXML.XML()
        ev = evento.Evento if ev_maiusculo else evento.evento
        ev['xmlns'] = 'http://www.portalfiscal.inf.br/nfe'
        ev['versao'] = '1.00'
        ev.infEvento['Id'] = 'ID%s%s%02i' % (cod_evento, chave_nfe,
                                             qtd_mesmo_evento)
        ev.infEvento.cOrgao = UFS_IBGE[self.__uf]
        ev.infEvento.tpAmb = self.__ambiente
        ev.infEvento.CNPJ = self.__cnpj
        ev.infEvento.chNFe = chave_nfe
        ev.infEvento.dhEvento = dh
        ev.infEvento.tpEvento = cod_evento
        ev.infEvento.nSeqEvento = qtd_mesmo_evento
        ev.infEvento.verEvento = '1.00'
        ev.infEvento.detEvento['versao'] = '1.00'
        ev.infEvento.detEvento.descEvento = descr_evento
        ev.infEvento.detEvento += xml_adicional
        self.assinar(ev.infEvento)
        # Validar xml da evento
        if not self.validar(evento, xsd_evento):
            erros = "Erro(s) no XML: "
            for erro in self.erros:
                erros += erro['type_name'] + ': ' + erro['message']
            raise ValueError(erros)
        # Lote para envio
        envio = PoleXML.XML()
        envio.envEvento['xmlns'] = 'http://www.portalfiscal.inf.br/nfe'
        envio.envEvento['versao'] = '1.00'
        # idLote = microsegundo/10 do envio - 15 dígitos no máximo
        envio.envEvento.idLote = str(int(time.time() * 100000))
        envio.envEvento.evento = ev(1)
        recibo = self.servico('RecepcaoEvento', envio, xsd_envio)
        retorno = PoleXML.XML()
        retorno.procEventoNFe['xmlns'] = 'http://www.portalfiscal.inf.br/nfe'
        retorno.procEventoNFe['versao'] = '1.00'
        retorno.procEventoNFe.evento = ev(1)
        if recibo.retEnvEvento('retEvento'):
            retorno.procEventoNFe.retEvento = recibo.retEnvEvento.retEvento
        else:
            retorno.procEventoNFe.retEnvEvento = recibo.retEnvEvento
        return retorno

    def enviar_carta_correcao(self, qtd_carta_correcao, correcao, chave_nfe,
                              data_hora_evento):
        carta = PoleXML.XML()
        carta.xCorrecao = correcao
        carta.xCondUso = ('A Carta de Correcao e disciplinada pelo paragrafo'
                          ' 1o-A do art. 7o do Convenio S/N, de 15 de dezembro'
                          ' de 1970 e pode ser utilizada para regularizacao de'
                          ' erro ocorrido na emissao de documento fiscal,'
                          ' desde que o erro nao esteja relacionado com:'
                          ' I - as variaveis que determinam o valor do imposto'
                          ' tais como: base de calculo, aliquota, diferenca de'
                          ' preco, quantidade, valor da operacao ou da'
                          ' prestacao; II - a correcao de dados cadastrais que'
                          ' implique mudanca do remetente ou do destinatario;'
                          ' III - a data de emissao ou de saida.')
        return self.enviar_envento('Carta de Correcao', chave_nfe,
                                   data_hora_evento, qtd_carta_correcao, carta)

    def enviar_nfe(self, xml):
        # Realiza o parser sobre nfe, identificada como string se iniciar por
        # '<', senão é identificada como nome de arquivo
        if type(xml) == str:
            if xml[0] == '<':
                xml = PoleXML.importar(xml)
            else:
                xml = PoleXML.importar(open(xml).read())
        if not isinstance(xml, PoleXML.XML):
            raise TypeError('A NFe em XML precisa ser passada como string XML,'
                            ' string com o nome do arquivo com o XML ou'
                            ' instância de PoleXML.XML!')
        # Assina a NFe
        self.assinar(xml.NFe.infNFe)
        # Cria envelope de lote para a NFe
        lote_nfe = PoleXML.XML()
        lote_nfe.enviNFe['xmlns'] = 'http://www.portalfiscal.inf.br/nfe'
        lote_nfe.enviNFe['versao'] = '3.10'
        id_lote = datetime.datetime.now().strftime('%y%m%d%H%M%S%f')[:15]
        lote_nfe.enviNFe.idLote = id_lote
        lote_nfe.enviNFe.indSinc = '0'
        lote_nfe.enviNFe += xml
        # Envia a NFe
        return self.servico('NfeAutorizacao', lote_nfe)

    def consultar_cadastro(self, CNPJ=None, IE=None, CPF=None):
        sefaz = self.__sefaz
        self.__sefaz = SEFAZ_CONSULTA[self.__uf]
        consulta = PoleXML.XML()
        consulta.ConsCad['xmlns'] = 'http://www.portalfiscal.inf.br/nfe'
        consulta.ConsCad['versao'] = '3.10' if self.__uf == 'MS' else '2.00'
        consulta.ConsCad.infCons.xServ = 'CONS-CAD'
        consulta.ConsCad.infCons.UF = self.__uf
        if CNPJ is not None:
            consulta.ConsCad.infCons.CNPJ = CNPJ
        elif IE is not None:
            consulta.ConsCad.infCons.IE = IE
        elif CPF is not None:
            consulta.ConsCad.infCons.CPF = CPF
        # Para cSit = Situação do contribuinte:
        #     0 - não habilitado
        #     1 - habilitado
        # Para indCredNFe e indCredCTe:
        #     0 - Não credenciado para emissão
        #     1 - Credenciado
        #     2 - Credenciado com obrigatoriedade para todas operações
        #     3 - Credenciado com obrigatoriedade parcial
        #     4 - a SEFAZ não fornece a informação
        # Especificar a versão, pois no XML é 2.00 e o wsdl é 3.10
        retorno = self.servico('NfeConsultaCadastro', consulta,
                               versao_wsdl='3.10')
        self.__sefaz = sefaz
        return retorno

    def consultar_recibo(self, recibo):
        # Cria a estrutra consulta pelo número do recibo e faz a consulta
        consulta = PoleXML.XML()
        consulta.consReciNFe['xmlns'] = 'http://www.portalfiscal.inf.br/nfe'
        consulta.consReciNFe['versao'] = '3.10'
        consulta.consReciNFe.tpAmb = self.__ambiente
        consulta.consReciNFe.nRec = recibo
        return self.servico('NfeRetAutorizacao', consulta)

    def enviar_nfe_e_consultar_recibo(self, xml, tentativas=30,
                                      espera_em_segundos=5,
                                      aviso_processamento=True):
        retorno = self.enviar_nfe(xml)
        # se o lote não foi recebido com sucesso (103), retorna este recibo
        if str(retorno.retEnviNFe.cStat) != '103':
            return retorno
        recibo = str(retorno.retEnviNFe.infRec.nRec)
        consulta = PoleXML.XML()
        consulta.consReciNFe['xmlns'] = 'http://www.portalfiscal.inf.br/nfe'
        consulta.consReciNFe['versao'] = '3.10'
        consulta.consReciNFe.tpAmb = self.__ambiente
        consulta.consReciNFe.nRec = recibo
        cStat = '105'  # 105 = Lote em processamento
        tentativa = 1
        while cStat == '105' and tentativa <= tentativas:
            time.sleep(espera_em_segundos)
            retorno = self.servico('NfeRetAutorizacao', consulta)
            cStat = str(retorno.retConsReciNFe.cStat)
            if aviso_processamento:
                print('Tentativa %i: %s - %s' % (tentativa,
                      str(retorno.retConsReciNFe.cStat),
                      str(retorno.retConsReciNFe.xMotivo)))
                if cStat == '105':
                    print 'Consultando novamente...'
            tentativa += 1
        # Retorna o resultado da consulta do recibo
        if aviso_processamento:
            print('Tentativa %i: %s - %s' % (tentativa - 1,
                  str(retorno.retConsReciNFe.protNFe.infProt.cStat),
                  str(retorno.retConsReciNFe.protNFe.infProt.xMotivo)))
        return retorno

    def validar(self, xml, nome_xsd=None):
        '''Função que valida um XML usando lxml do Python via arquivo XSD no
           diretório xsd/<pacote>/<nó_xml>.xsd'''
        # Realiza o parser sobre o xml, identificado como string se iniciar por
        # '<', senão é identificado como nome de arquivo
        if type(xml) == str:
            if xml[0] == '<':
                xml = PoleXML.importar(xml)
            else:
                xml = PoleXML.importar(open(xml).read())
        # Para este sistema com lxml funcionar foi preciso
        # trocar em tiposBasico_v1.03.xsd {0,} por *
        # Obeter a versão do primeiro ou segundo nó
        versao = xml('', 1)['versao'] or xml('', 1)('', 1)['versao']
        # O padrão de nome de arquivos xsd é iniciar com letras minúsculas,
        # mantendo maiúsuclas iniciais de palavras, assim foi preciso desse
        # trecho de código para passar para músculas iniciais maiúsculas
        if nome_xsd is None:
            nome = ''
            temp = xml('', 1)._XML__nome
            for i in range(len(temp)):
                if temp[i].isupper():
                    nome += temp[i].lower()
                else:
                    break
            nome += temp[i:]
        else:
            nome = nome_xsd
        # Caminho do arquivo XSD
        arquivo_xsd = os.path.join(self.__raiz, 'xsd', self.__pacote,
                                   nome + '_v' + versao + '.xsd')
        # Verifica a validade do xml
        self.erros = PoleXML.validar(xml, arquivo_xsd)
        return len(self.erros) == 0

    def assinar(self, filho_id):
        return PoleXML.assinar(filho_id, 'Id', self.__chave,
                               self.__certificado)

    def verificar_assinatura(self, filho_id):
        return PoleXML.verificar_assinatura(filho_id, 'Id', self.__raiz +
                                            '/certificadoras/v1_v2_v3.crt')

    def download_nfe(self, chave):  # usar uf = 'AN' (ambiente nacional)
        requisicao = PoleXML.XML()
        requisicao.downloadNFe['xmlns'] = 'http://www.portalfiscal.inf.br/nfe'
        requisicao.downloadNFe['versao'] = '1.00'
        requisicao.downloadNFe.tpAmb = self.__ambiente
        requisicao.downloadNFe.xServ = 'DOWNLOAD NFE'
        requisicao.downloadNFe.CNPJ = self.__cnpj
        requisicao.downloadNFe.chNFe = chave
        return self.servico('NfeDownloadNF', requisicao)

    def manifestar(self, manifestacao, chave_nfe, justificativa=None):
        manifesto = PoleXML.XML()
        if justificativa:
            manifesto.xJust = justificativa
        return self.enviar_envento(manifestacao, chave_nfe,
                                   datetime.datetime.now(), 1, manifesto)

    def consultar_nfes_destinadas(self, consultar=TODAS,
                                  sem_cnpj_base=False, ultimo_nsu=0):
        consulta = PoleXML.XML()
        consulta.consNFeDest['xmlns'] = 'http://www.portalfiscal.inf.br/nfe'
        consulta.consNFeDest['versao'] = '1.01'
        consulta.consNFeDest.tpAmb = self.__ambiente
        consulta.consNFeDest.xServ = 'CONSULTAR NFE DEST'
        consulta.consNFeDest.CNPJ = self.__cnpj
        consulta.consNFeDest.indNFe = consultar
        consulta.consNFeDest.indEmi = +sem_cnpj_base
        consulta.consNFeDest.ultNSU = ultimo_nsu
        retorno = self.servico('NfeConsultaDest', consulta)
        while (retorno.retConsNFeDest.cStat == '138' and
               retorno.retConsNFeDest.indCont == '1'):
            consulta.consNFeDest.ultNSU = retorno.consNFeDest.ultNSU
            retorno += self.servico('NfeConsultaDest', consulta)
        return retorno
