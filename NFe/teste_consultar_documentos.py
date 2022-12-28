#!/usr/bin/env python
# -*- coding: utf-8 -*-

import locale
import httplib
import sys
import time
import zlib
import base64
import socket
import ssl
import re
import pole
import signal
import traceback


continuar = True
pulos = 0


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
                                    ssl_version=ssl.PROTOCOL_TLSv1_2,  # SSLv23
                                    ca_certs=self.ca_certs,
                                    cert_reqs=ssl.CERT_REQUIRED)


def handler(signum, frame):
    global continuar
    print
    print "_~^~" * 20 + '\nSinal:', signum, '- Parando...\n' + "_~^~" * 20
    print
    sys.stdout.flush()
    continuar = False


signal.signal(signal.SIGTERM, handler)


if len(sys.argv) != 6:
    print("Uso: %s <uf> <cnpj> <ultimo_nsu_nfe>"
          " <ultimo_nsu_cte> <ultimo_nsu_mdfe>" % sys.argv[0])
    sys.exit(1)

locale.setlocale(locale.LC_ALL, '')

UFS_IBGE = {
    'AC': '12', 'CE': '23', 'MG': '31', 'PE': '26', 'RO': '11', 'SP': '35',
    'AL': '27', 'DF': '53', 'MS': '50', 'PI': '22', 'RR': '14', 'TO': '17',
    'AM': '13', 'ES': '32', 'MT': '51', 'PR': '41', 'RS': '43', 'AN': '91',
    'AP': '16', 'GO': '52', 'PA': '15', 'RJ': '33', 'SC': '42',
    'BA': '29', 'MA': '21', 'PB': '25', 'RN': '24', 'SE': '28'}

uf = UFS_IBGE[sys.argv[1]]
cnpj = sys.argv[2]
ult_nsu_nfe = int(sys.argv[3])
ult_nsu_cte = int(sys.argv[4])
ult_nsu_mdfe = int(sys.argv[5])

dir_certs = '/home/junior/NFe/cnpjs/%s/certificado_digital' % cnpj
key_file = dir_certs + '/chave.pem'
cert_file = dir_certs + '/certificado.pem'
ca_certs = dir_certs + '/ca.pem'
dir_consultas = '/media/NFe/consultas'

con_nfe = 'www1.nfe.fazenda.gov.br'
con_cte = 'www1.cte.fazenda.gov.br'
con_mdfe = 'mdfe.svrs.rs.gov.br'

headers = {'Content-Type': 'application/soap+xml; charset=utf-8'}

envelope_nfe = '''<?xml version="1.0" encoding="UTF-8"?>
<soap12:Envelope xmlns:ns0="http://www.portalfiscal.inf.br/nfe/wsdl/
                 NFeDistribuicaoDFe" xmlns:ns1="http://www.w3.org/2003/05/
                 soap-envelope" xmlns:soap12="http://www.w3.org/2003/05/
                 soap-envelope" xmlns:xsi="http://www.w3.org/
                 2001/XMLSchema-instance">
    <soap12:Header/>
    <ns1:Body>
        <nfeDistDFeInteresse xmlns="http://www.portalfiscal.inf.br/nfe/wsdl/
                                    NFeDistribuicaoDFe">
            <nfeDadosMsg>
                <distDFeInt xmlns="http://www.portalfiscal.inf.br/
                                   nfe" versao="1.35">
                    <tpAmb>1</tpAmb>
                    <cUFAutor>%s</cUFAutor>
                    <CNPJ>%s</CNPJ>
                    <distNSU>
                        <ultNSU>%015i</ultNSU>
                    </distNSU>
                </distDFeInt>
            </nfeDadosMsg>
        </nfeDistDFeInteresse>
    </ns1:Body>
</soap12:Envelope>'''

envelope_cte = '''<?xml version="1.0" encoding="utf-8"?>
<soap12:Envelope xmlns:xsi="http://www.w3.org/2001/
                 XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/
                 XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/
                 soap-envelope">
  <soap12:Body>
    <cteDistDFeInteresse xmlns="http://www.portalfiscal.inf.br/cte/wsdl/
                         CTeDistribuicaoDFe">
      <cteDadosMsg>
        <distDFeInt xmlns="http://www.portalfiscal.inf.br/cte" versao="1.00">
          <tpAmb>1</tpAmb>
          <cUFAutor>%s</cUFAutor>
          <CNPJ>%s</CNPJ>
          <distNSU>
            <ultNSU>%015i</ultNSU>
          </distNSU>
        </distDFeInt>
      </cteDadosMsg>
    </cteDistDFeInteresse>
  </soap12:Body>
</soap12:Envelope>'''

envelope_mdfe = '''<?xml version="1.0" encoding="utf-8"?>
<soap12:Envelope xmlns:xsi="http://www.w3.org/2001/
                 XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/
                 XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/
                 soap-envelope">
  <soap12:Header>
    <mdfeCabecMsg xmlns="http://www.portalfiscal.inf.br/mdfe/wsdl/
                  MDFeDistribuicaoDFe">
      <cUF>%s</cUF>
      <versaoDados>1.00</versaoDados>
    </mdfeCabecMsg>
  </soap12:Header>
  <soap12:Body>
    <mdfeDadosMsg xmlns="http://www.portalfiscal.inf.br/mdfe/wsdl/
                  MDFeDistribuicaoDFe">
        <distDFeInt xmlns="http://www.portalfiscal.inf.br/mdfe" versao="1.00">
          <tpAmb>1</tpAmb>
          <CNPJ>%s</CNPJ>
          <distNSU>
            <ultNSU>%015i</ultNSU>
          </distNSU>
        </distDFeInt>
    </mdfeDadosMsg>
  </soap12:Body>
</soap12:Envelope>'''

envelope_nfe = re.sub(r'\n\s*', '', envelope_nfe)
envelope_cte = re.sub(r'\n\s*', '', envelope_cte)
envelope_mdfe = re.sub(r'\n\s*', '', envelope_mdfe)

post_nfe = '/NFeDistribuicaoDFe/NFeDistribuicaoDFe.asmx'
post_cte = '/CTeDistribuicaoDFe/CTeDistribuicaoDFe.asmx'
post_mdfe = '/WS/MDFeDistribuicaoDFe/MDFeDistribuicaoDFe.asmx'

max_nsu_nfe = 999999999999999
max_nsu_cte = 999999999999999
max_nsu_mdfe = 999999999999999
max_pulos = 10

while continuar:
    print '#' * 100
    print "NSU NFe:", ult_nsu_nfe, max_nsu_nfe
    print "NSU CTe:", ult_nsu_cte, max_nsu_cte
    print "NSU MDFe:", ult_nsu_mdfe, max_nsu_mdfe
    print "Pulos:", pulos, max_pulos
    for consulta in ('nfe', 'cte', 'mdfe'):
        print '-' * 40 + '  ' + consulta + '  ' + '-' * 40
        sys.stdout.flush()

        if (consulta == 'nfe' and ult_nsu_nfe >= max_nsu_nfe
                or consulta == 'cte' and ult_nsu_cte >= max_nsu_cte
                or consulta == 'mdfe' and ult_nsu_mdfe >= max_nsu_mdfe):
            print 'Máximo atingido! Pulando...'
            pulos += 1
            continue
        try:
            con = HTTPSConnection(
                con_nfe if consulta == 'nfe'
                else con_cte if consulta == 'cte'
                else con_mdfe,
                key_file=key_file, cert_file=cert_file,
                ca_certs=ca_certs)

            con.request('POST',
                        post_nfe if consulta == 'nfe'
                        else post_cte if consulta == 'cte'
                        else post_mdfe,
                        (envelope_nfe if consulta == 'nfe'
                         else envelope_cte if consulta == 'cte'
                         else envelope_mdfe) %
                        (uf, cnpj,
                         ult_nsu_nfe if consulta == 'nfe'
                         else ult_nsu_cte if consulta == 'cte'
                         else ult_nsu_mdfe),
                        headers)

            r = con.getresponse()

        except Exception:
            traceback.print_exc()
            print '\nErro encontrado! Pulando...'
            pulos += 1
            continue

        print r.status, r.reason
        for h in r.getheaders():
            print h[0], h[1]
        dados = r.read()
        print dados[:1000] + ' ... ' + dados[-100:]
        print '-' * 100
        sys.stdout.flush()

        retorno = pole.xml.importar(dados)
        if consulta == 'nfe':
            ret = (retorno.Envelope.Body.nfeDistDFeInteresseResponse.
                   nfeDistDFeInteresseResult.retDistDFeInt)
        elif consulta == 'cte':
            ret = (retorno.Envelope.Body.cteDistDFeInteresseResponse.
                   cteDistDFeInteresseResult.retDistDFeInt)
        else:
            ret = (retorno.Envelope.Body.mdfeDistDFeInteresseResult.
                   retDistDFeInt)

        tpAmb = str(ret.tpAmb)
        verAplic = str(ret.verAplic)
        cStat = str(ret.cStat)
        xMotivo = str(ret.xMotivo)
        if cStat not in ('137', '138'):
            print 'Erro: ' + cStat + ' - ' + xMotivo
            continue
        dhResp = str(ret.dhResp)
        if cStat == '137':
            ult_nsu = (ult_nsu_nfe if consulta == 'nfe'
                       else ult_nsu_cte if consulta == 'cte'
                       else ult_nsu_mdfe)
            max_nsu = ult_nsu
        else:
            ult_nsu = int(str(ret.ultNSU))
            max_nsu = int(str(ret.maxNSU))
        lote = ret.loteDistDFeInt

        if consulta == 'nfe':
            ult_nsu_nfe = ult_nsu
            max_nsu_nfe = max_nsu
        elif consulta == 'cte':
            ult_nsu_cte = ult_nsu
            max_nsu_cte = max_nsu
        else:
            ult_nsu_mdfe = ult_nsu
            max_nsu_mdfe = max_nsu

        for ndoc in range(1, lote('docZip', 0) + 1):
            nsu = lote.docZip(ndoc)['NSU']
            print 'Processando:', str(ndoc), ' - ', nsu
            sys.stdout.flush()
            # print '=' * 40 + '  ' + str(ndoc) + ' - ' + nsu + '  ' + '=' * 40
            arquivo_64 = str(lote.docZip(ndoc))
            # print repr(arquivo_64)
            # print '-' * 100
            arquivo_zip = base64.b64decode(arquivo_64)
            # print repr(arquivo_zip)
            # with open('consulta_cte_' + nsu + '.zip', 'w') as arq:
            #     arq.write(arquivo_zip)
            # print '-' * 100
            arquivo = zlib.decompress(arquivo_zip, 16 + zlib.MAX_WBITS)
            with open('%s/consulta_%s_%s.xml' % (dir_consultas, consulta, nsu),
                      'wb') as arq:
                arq.write(arquivo)
            # print pole.xml.exportar(pole.xml.importar(arquivo))
            # print '=' * 100

    print '=======>', time.strftime(locale.nl_langinfo(locale.D_T_FMT))
    if all([ult_nsu_nfe >= max_nsu_nfe, ult_nsu_cte >= max_nsu_cte,
            ult_nsu_mdfe >= max_nsu_mdfe]):
        print '             \\-> Esperando 10 minutos...'
        sys.stdout.flush()
        time.sleep(600)
        max_nsu_nfe = 999999999999999
        max_nsu_cte = 999999999999999
        max_nsu_mdfe = 999999999999999
        pulos = 0
    else:
        print '             \\-> Esperando 10 segundos...'
        sys.stdout.flush()
        time.sleep(10)
        if pulos > max_pulos:
            max_nsu_nfe = 999999999999999
            max_nsu_cte = 999999999999999
            max_nsu_mdfe = 999999999999999
            pulos = 0
