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
import time
import datetime

# Módulos SUDS utilizados no programa
import suds.client
import suds.xsd.doctor
import suds.xsd.sxbasic
import suds.transport.http
import suds.bindings.binding
from suds.sax.element import Element as E

# Debug
#import logging
#logging.basicConfig(level=logging.INFO)
#logging.getLogger('suds.client').setLevel(logging.DEBUG)

# Módulo feito por Junior Polegato em CPython para assinar XML
import PoleXML

# Conversão
import PoleUtil
cf = PoleUtil.convert_and_format

# Constantes

PRODUCAO = 1
HOMOLOGACAO = 2

UFS_IBGE = {'AC': '12', 'CE': '23', 'MG': '31', 'PE': '26', 'RO': '11', 'SP': '35',
            'AL': '27', 'DF': '53', 'MS': '50', 'PI': '22', 'RR': '14', 'TO': '17',
            'AM': '13', 'ES': '32', 'MT': '51', 'PR': '41', 'RS': '43',
            'AP': '16', 'GO': '52', 'PA': '15', 'RJ': '33', 'SC': '42', 
            'BA': '29', 'MA': '21', 'PB': '25', 'RN': '24', 'SE': '28',
            'AN': '90'
        }

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
                                          'TO': 'Tocantins'
            }

# Classe para prover camada de transporte com conexão HTTPS/SSL
# Não suportada nativamente pelo Suds
# Inspirado em http://www.threepillarglobal.com/soap_client_auth
import socket
import httplib
import urllib2
import ssl
class HTTPSConnection(httplib.HTTPConnection):
    default_port = 443
    def __init__(self, host, port=None, key_file=None, cert_file=None,
                 strict=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
                 source_address=None):
        httplib.HTTPConnection.__init__(self, host, port, strict, timeout, source_address)
        self.key_file = key_file
        self.cert_file = cert_file
    def connect(self):
        sock = socket.create_connection((self.host, self.port), self.timeout, self.source_address)
        if self._tunnel_host:
            self.sock = sock
            self._tunnel()
        self.sock = ssl.wrap_socket(sock, self.key_file, self.cert_file, ssl_version=ssl.PROTOCOL_SSLv3)
class https_ssl(urllib2.HTTPSHandler):
    def __init__(self, key_file, cert_file):
        urllib2.HTTPSHandler.__init__(self)
        self.key_file = key_file
        self.cert_file = cert_file
        self.protocol = 2
    def https_open(self, req):
        return self.do_open(self.conexao, req)
    def conexao(self, host, timeout = None):
        return HTTPSConnection(host, timeout = timeout, key_file = self.key_file, cert_file = self.cert_file)

# Sobrescrita a função "str" de Element (E) para não endentar nem quebrar linha
# Pelo menos o servidor de SP não aceita caracteres entre as marcas, erro 588
# Esse código foi retirado de uma versão mais nova do E da função "plain":
# http://jortel.fedorapeople.org/suds/doc/suds.sax.element-pysrc.html#Element.plain
# Foi colocado o parâmetro "indent", porém ignorado, para compatilidade com a função "str"
# A sobrescrita ocorre após o código com E.str = __plain, sendo a antiga em "__str_indent"
def __plain(self, indent=0):
    # Se tive com a versão que já tem o "plain", basta descomentar a linha abaixo
    # return self.plain()
    result = []
    result.append('<%s' % self.qname())
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
        result.append(c.str())
    result.append('</%s>' % self.qname())
    result = ''.join(result)
    return result
def __str_indent(self, indent = 0):
    tab = '%*s'%(indent * 4, '')
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
       pacote: string com nome do diretório que contém o "Package Language", padrão 'PL_006e'
       raiz: diretório que vai conter a estruturad de diretórios e arquivos para o Webservice, sendo padrão ${HOME}/NFe
       ${HOME}/NFe
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
       |     |     |     |--->NfeRecepcao2.wsdl
       |     |     |     |--->NfeRetRecepcao2.wsdl
       |     |     |     |--->NfeCancelamento2.wsdl
       |     |     |     |--->NfeInutilizacao2.wsdl
       |     |     |     |--->NfeConsulta2.wsdl
       |     |     |     \--->NfeStatusServico2.wsdl
       |     |     \---> producao
       |     |           |--->NfeRecepcao2.wsdl
       |     |           |--->NfeRetRecepcao2.wsdl
       |     |           |--->NfeCancelamento2.wsdl
       |     |           |--->NfeInutilizacao2.wsdl
       |     |           |--->NfeConsulta2.wsdl
       |     |           \--->NfeStatusServico2.wsdl
       |     |---> sefaz_2
       |     |     \---> ...
       |     \---> ...
       \---> xsd
             |---> PL_006e
             |     |---> nfe_v2.00.xsd
             |     |---> ...
             |     \---> tiposBasico_v1.03.xsd
             \---> ...
'''
    # ambiemte pode ser 1 (PRODUCAO) ou 2 (HOMOLOGACAO)
    # 
    # 
    def __init__(self, cnpj, ambiente = PRODUCAO, uf = 'SP', sefaz = None, raiz = None, pacote = 'PL'):
        if uf not in UFS_IBGE:
            raise ValueError('UF ' + str(uf) + ' inválida!')
        if sefaz is None:
            if uf in ('ES', 'MA', 'PA', 'PI', 'RN'):
                sefaz = 'SVAN'
            elif uf in ('AC', 'AL', 'AM', 'AP', 'DF', 'MS', 'PB', 'RJ', 'RO', 'RR', 'SC', 'SE', 'TO'):
                sefaz = 'SVRS'
            else:
                sefaz = uf
        if ambiente not in (1, 2):
            raise ValueError('Ambiente ' + str(ambiente) + ' inválido!')
        self.__uf = uf
        self.__sefaz = sefaz
        self.__cnpj = cnpj
        self.__ambiente = ambiente
        self.__str_ambiente = ('producao', 'homologacao')[ambiente - 1]
        if raiz == None:
            self.__raiz = os.getenv("HOME") + '/NFe'
        else:
            self.__raiz = raiz
        self.__pacote = pacote
        # Caminho do certificado digital
        self.__chave = self.__raiz + '/cnpjs/' + self.__cnpj + '/certificado_digital/chave.pem'
        self.__certificado = self.__raiz + '/cnpjs/' + self.__cnpj + '/certificado_digital/certificado.pem'

    def __cabecalho(self, cliente, versao_dados):
        cabecalho = cliente.factory.create('nfeCabecMsg')
        cabecalho.cUF = UFS_IBGE[self.__uf]
        cabecalho.versaoDados = versao_dados
        return cabecalho

    def servico(self, nome_wsdl, xml):
        # Validar xml para envio
        if not self.validar(xml):
            erros = "Erro(s) no XML: "
            for erro in self.erros:
                erros += erro['type_name'] + ': ' + erro['message']
            raise ValueError(erros)
        # Criar meio de transporte criptografado
        transporte = suds.transport.http.HttpTransport()
        transporte.urlopener = urllib2.build_opener(https_ssl(key_file = self.__chave, cert_file = self.__certificado))
        # Carrega o wsdl da estrutura de arquivos <raiz>/wsdl/<uf>/<nome_wsdl>.wsdl
        arquivo_wsdl = 'file://' + self.__raiz + '/wsdl/' + self.__sefaz + '/' + self.__str_ambiente + '/' + str(nome_wsdl) + '.wsdl'
        wsdl = suds.client.Client(arquivo_wsdl, transport = transporte)
        # Configurar o ambiente do SOAP
        wsdl.options.cache.clear()
        ns_anterior = suds.bindings.binding.envns
        suds.bindings.binding.envns = ('SOAP-ENV', 'http://www.w3.org/2003/05/soap-envelope')
        # Cria uma função do primeiro serviço, primeira URL (port) e primeiro método, visto que são únicos
        funcao = suds.client.Method(wsdl, wsdl.wsdl.services[0].ports[0].methods.values()[0])
        # Configura o cabeçalho e retorno em XML
        wsdl.set_options(soapheaders = self.__cabecalho(wsdl, xml('', 1)['versao']), retxml = True, prettyxml = True)
        # Executa a função e coleta o resultado em XML
        resultado = funcao(suds.sax.parser.Parser().parse(string = PoleXML.exportar(xml, -1)).root())
        #resultado = funcao(PoleXML.exportar(xml, -1))
        #print repr(PoleXML.importar(resultado))
        # Voltando o ambiente do SOAP
        suds.bindings.binding.envns = ns_anterior
        # Retornar o resultado na forma da classe XML, somente o corpo do envelope Soap
        return PoleXML.importar(resultado).Envelope.Body('', 1)

    def status(self):
        consulta = PoleXML.XML()
        consulta.consStatServ['xmlns'] = 'http://www.portalfiscal.inf.br/nfe'
        consulta.consStatServ['versao'] = '2.00'
        consulta.consStatServ.tpAmb = self.__ambiente
        consulta.consStatServ.cUF = UFS_IBGE[self.__uf]
        consulta.consStatServ.xServ = 'STATUS'
        return self.servico('NfeStatusServico2', consulta)
    
    def consultar_chave(self, chave):
        consulta = PoleXML.XML()
        consulta.consSitNFe['xmlns'] = 'http://www.portalfiscal.inf.br/nfe'
        consulta.consSitNFe['versao'] = '2.00'
        consulta.consSitNFe.tpAmb = self.__ambiente
        consulta.consSitNFe.xServ = 'CONSULTAR'
        consulta.consSitNFe.chNFe = chave
        return self.servico('NfeConsulta2', consulta)
    
    def consultar_num_nota(self, num_nota):
        for ano in range(datetime.date.today().year % 100, 5, -1):
            chave = str(UFS_IBGE[self.__uf]) + '%02d' % ano + '09' + self.__cnpj + '55001' + '%09d' % num_nota + '7825541981'
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

    def cancelar_chave(self, justificativa, chave, protocolo = None):
        if not protocolo:
            protocolo = str(self.consultar_chave(chave).retConsSitNFe.protNFe.infProt.nProt)
        cancelamento = PoleXML.XML()
        cancelamento.cancNFe['xmlns'] = 'http://www.portalfiscal.inf.br/nfe'
        cancelamento.cancNFe['versao'] = '2.00'
        cancelamento.cancNFe.infCanc['Id'] = 'ID' + chave
        cancelamento.cancNFe.infCanc.tpAmb = self.__ambiente
        cancelamento.cancNFe.infCanc.xServ = 'CANCELAR'
        cancelamento.cancNFe.infCanc.chNFe = chave
        cancelamento.cancNFe.infCanc.nProt = protocolo
        cancelamento.cancNFe.infCanc.xJust = justificativa
        self.assinar(cancelamento, cancelamento.cancNFe.infCanc)
        return self.servico('NfeCancelamento2', cancelamento)

    def cancelar_num_nota(self, justificativa, num_nota):
        consulta = self.consultar_num_nota(num_nota)
        return self.cancelar_chave(justificativa, consulta["chNFe"], consulta["protNFe"]["infProt"]["nProt"])

    def inutilizar(self, justificativa, ano, numero_inicial, numero_final = None, serie = 1):
        if numero_final is None:
            numero_final = numero_inicial
        inutilizacao = PoleXML.XML()
        inutilizacao.inutNFe['xmlns'] = 'http://www.portalfiscal.inf.br/nfe'
        inutilizacao.inutNFe['versao'] = '2.00'
        # Id = Código da UF + Ano (2 posições) + CNPJ + modelo + série + nro inicial e nro final, precedida do literal “ID”
        inutilizacao.inutNFe.infInut['Id'] = 'ID' + UFS_IBGE[self.__uf] + str(int(ano) % 100) + self.__cnpj + '55' + ("%03i" % int(serie)) + ("%09i" % int(numero_inicial)) + ("%09i" % int(numero_final))
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
        self.assinar(inutilizacao, inutilizacao.inutNFe.infInut)
        return self.servico('NfeInutilizacao2', inutilizacao)

    def enviar_carta_correcao(self, cod_lote_evento, qtd_carta_correcao, correcao, chave_nfe, cnpj_cpf, data_hora_evento):
        carta = PoleXML.XML()
        carta.evento['xmlns'] = 'http://www.portalfiscal.inf.br/nfe'
        carta.evento['versao'] = '1.00'
        carta.evento.infEvento['Id'] = 'ID' + '110110' + chave_nfe + "%02i" % qtd_carta_correcao
        carta.evento.infEvento.cOrgao = UFS_IBGE[self.__uf]
        carta.evento.infEvento.tpAmb = self.__ambiente
        if len(cnpj_cpf) > 11:
            carta.evento.infEvento.CNPJ = cnpj_cpf
        else:
            carta.evento.infEvento.CPF = cnpj_cpf
        carta.evento.infEvento.chNFe = chave_nfe
        dh = cf(data_hora_evento, datetime.datetime)[0]
        carta.evento.infEvento.dhEvento = dh.strftime('%Y-%m-%dT%H:%M:%S') + '-03:00'
        carta.evento.infEvento.tpEvento = '110110'
        carta.evento.infEvento.nSeqEvento = qtd_carta_correcao
        carta.evento.infEvento.verEvento = '1.00'
        carta.evento.infEvento.detEvento['versao'] = '1.00'
        carta.evento.infEvento.detEvento.descEvento = 'Carta de Correcao'
        carta.evento.infEvento.detEvento.xCorrecao = correcao
        carta.evento.infEvento.detEvento.xCondUso = 'A Carta de Correcao e disciplinada pelo paragrafo 1o-A do art. 7o do Convenio S/N, de 15 de dezembro de 1970 e pode ser utilizada para regularizacao de erro ocorrido na emissao de documento fiscal, desde que o erro nao esteja relacionado com: I - as variaveis que determinam o valor do imposto tais como: base de calculo, aliquota, diferenca de preco, quantidade, valor da operacao ou da prestacao; II - a correcao de dados cadastrais que implique mudanca do remetente ou do destinatario; III - a data de emissao ou de saida.'
        self.assinar(carta, carta.evento.infEvento)
        print repr(carta)
        # Validar xml da carta
        if not self.validar(carta, 'CCe'):
            erros = "Erro(s) no XML: "
            for erro in self.erros:
                erros += erro['type_name'] + ': ' + erro['message']
            raise ValueError(erros)
        # Lote para envio
        envio = PoleXML.XML()
        envio.envEvento['xmlns'] = 'http://www.portalfiscal.inf.br/nfe'
        envio.envEvento['versao'] = '1.00'
        envio.envEvento.idLote = cod_lote_evento
        envio.envEvento.evento = carta.evento
        print '*' * 100
        print repr(envio)

        return self.servico('RecepcaoEvento', envio)

    def enviar_nfe(self, xml):
        # Realiza o parser sobre nfe, identificada como string se iniciar por '<', senão é identificada como nome de arquivo
        if type(xml) == str:
            if xml[0] == '<':
                xml = PoleXML.importar(xml)
            else:
                xml = PoleXML.importar(open(xml).read())
        if not isinstance(xml, PoleXML.XML):
            raise TypeError('A NFe em XML precisa ser passada como string XML, string com o nome do arquivo com o XML ou instância de PoleXML.XML!')
        # Assina a NFe
        self.assinar(xml, xml.NFe.infNFe)
        # Cria envelope de lote para a NFe
        lote_nfe = PoleXML.XML()
        lote_nfe.enviNFe['xmlns'] = 'http://www.portalfiscal.inf.br/nfe'
        lote_nfe.enviNFe['versao'] = '2.00'
        lote_nfe.enviNFe.idLote = datetime.datetime.now().strftime('%y%m%d%H%M%S%f')[:15]
        lote_nfe.enviNFe = xml
        # Envia a NFe
        return self.servico('NfeRecepcao2', lote_nfe)

    def consultar_cadastro(self, CNPJ = None, IE = None, CPF = None):
        consulta = PoleXML.XML()
        consulta.ConsCad['xmlns'] = 'http://www.portalfiscal.inf.br/nfe'
        consulta.ConsCad['versao'] = '2.00'
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
        return self.servico('CadConsultaCadastro2', consulta)

    def consultar_recibo(self, recibo):
        # Cria a estrutra consulta pelo número do recibo e faz a consulta
        consulta = PoleXML.XML()
        consulta.consReciNFe['xmlns'] = 'http://www.portalfiscal.inf.br/nfe'
        consulta.consReciNFe['versao'] = '2.00'
        consulta.consReciNFe.tpAmb = self.__ambiente
        consulta.consReciNFe.nRec = recibo
        return self.servico('NfeRetRecepcao2', consulta)

    def enviar_nfe_e_consultar_recibo(self, xml, tentativas = 30, aviso_processamento = True):
        retorno = self.enviar_nfe(xml)
        if str(retorno.retEnviNFe.cStat) != '103': # 103 = Lote recebido com sucesso
            return retorno
        recibo = str(retorno.retEnviNFe.infRec.nRec)
        consulta = PoleXML.XML()
        consulta.consReciNFe['xmlns'] = 'http://www.portalfiscal.inf.br/nfe'
        consulta.consReciNFe['versao'] = '2.00'
        consulta.consReciNFe.tpAmb = self.__ambiente
        consulta.consReciNFe.nRec = recibo
        cStat = '105' # 105 = Lote em processamento
        tentativa = 1
        while cStat == '105' and tentativa <= tentativas:
            time.sleep(1)
            retorno = self.servico('NfeRetRecepcao2', consulta)
            cStat = str(retorno.retConsReciNFe.cStat)
            if aviso_processamento:
                print 'Tentativa ' + str(tentativa) + ': ' + str(retorno.retConsReciNFe.cStat) + ' - ' + str(retorno.retConsReciNFe.xMotivo)
                if cStat == '105':
                    print 'Consultando novamente...'
            tentativa += 1
        # Retorna o resultado da consulta do recibo
        print 'Tentativa ' + str(tentativa - 1) + ': ' + str(retorno.retConsReciNFe.protNFe.infProt.cStat) + ' - ' + str(retorno.retConsReciNFe.protNFe.infProt.xMotivo)
        return retorno

    def validar(self, xml, nome_xsd = None):
        '''Função que valida um XML usando lxml do Python via arquivo XSD no diretório xsd/<pacote>/<nó_xml>.xsd'''
        # Realiza o parser sobre o xml, identificado como string se iniciar por '<', senão é identificado como nome de arquivo
        if type(xml) == str:
            if xml[0] == '<':
                xml = PoleXML.importar(xml)
            else:
                xml = PoleXML.importar(open(xml).read())
        # Para este sistema com lxml funcionar foi preciso trocar em tiposBasico_v1.03.xsd {0,} por *
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
        print nome_xsd, self.__raiz , '/xsd/' , self.__pacote , '/' , nome , '_v' , versao , '.xsd'
        arquivo_xsd = self.__raiz + '/xsd/' + self.__pacote + '/' + nome + '_v' + versao + '.xsd'
        # Verifica a validade do xml
        self.erros = PoleXML.validar(xml, arquivo_xsd)
        return len(self.erros) == 0

    def assinar(self, xml, filho_id, filho_assinatura = None, atributo_id = 'Id'):
        if filho_assinatura is None:
            filho_assinatura = filho_id._XML__pai
        PoleXML.assinar(xml, filho_assinatura, filho_id, atributo_id, self.__chave, self.__certificado)
