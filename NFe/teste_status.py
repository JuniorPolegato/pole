#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pole

# import logging
# logging.basicConfig(level=logging.DEBUG)

cnpj = raw_input('CNPJ: ')

for ambiente in (pole.nfe.PRODUCAO, pole.nfe.HOMOLOGACAO):
    print '*' * 100
    print 'Produção' if ambiente == pole.nfe.PRODUCAO else 'Homologação'
    print '*' * 100
    for uf in sorted(pole.nfe.SEFAZ):
        print uf
        try:
            webservice = pole.nfe.Webservice(cnpj, ambiente, uf=uf)
            print repr(webservice.status())
        except Exception as e:
            print e
        print '-' * 100
