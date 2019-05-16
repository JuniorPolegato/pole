#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pole
import logging

logging.basicConfig(level=logging.DEBUG)


cnpj = raw_input('CNPJ: ')
nsu = int(raw_input('Ultimo NSU: '))

ambiente = pole.nfe.PRODUCAO
webservice = pole.nfe.Webservice(cnpj, ambiente)

# NFe
print '-' * 100
docs = webservice.consultar_distribuicao_dfe(nsu)
for doc, xml in docs.items():
    print '-' * 20 + '  ' + '%015i' % doc + '-dfe.xml  ' + '-' * 20
    with open('%015i' % doc + '-dfe.xml', 'wb') as arquivo:
        arquivo.write(pole.xml.serializar(xml))
    print repr(xml)
