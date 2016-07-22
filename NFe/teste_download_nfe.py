#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pole

cnpj = raw_input('CNPJ: ')
nfe = raw_input('Chave da NFe: ')

ambiente = pole.nfe.PRODUCAO
webservice = pole.nfe.Webservice(cnpj, ambiente, uf='AN')
print repr(webservice.manifestar('Ciencia da Operacao', nfe))
print repr(webservice.download_nfe(nfe))
