#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pole

# import logging
# logging.basicConfig(level=logging.DEBUG)


# Não operacional para SVRS para UFs: AL, AP, DF, RJ, RO, RR, SE, TO
# Não operacional para SVAN para UFs: MA, PA, PI

cnpj_certificado = raw_input('CNPJ: ')

cnpj_uf = (('97837181001119', 'MG'), ('73828865000114', 'RJ'),
           ('33000167014838', 'RN'), ('97551543000139', 'SP'),
           ('97467856000103', 'PR'), ('98417348000183', 'RS'),
           ('69983484000132', 'AL'), ('92660406001352', 'ES'),
           ('90347840000894', 'PE'), ('69427219000178', 'MA'),
           ('15527906000993', 'PB'), ('00013314000129', 'AM'),
           ('63593594000101', 'AC'), ('33931486003318', 'SE'),
           ('97509350000110', 'GO'), ('38046579000104', 'DF'),
           ('96824594011240', 'MT'), ('88680095000182', 'BA'),
           ('95807137000169', 'SC'), ('06593156000100', 'CE'),
           ('84718741000100', 'RO'), ('42593269000926', 'AP'),
           ('84046101001912', 'MS'), ('72244114000198', 'TO'),
           ('41528852000133', 'PI'), ('84200518000169', 'PA'),
                                     ('17194077000657', 'RR'))

ambiente = pole.nfe.PRODUCAO
print '*' * 100
print 'Produção' if ambiente == pole.nfe.PRODUCAO else 'Homologação'
print '*' * 100
for cnpj, uf in cnpj_uf:
    print uf, cnpj
    try:
        webservice = pole.nfe.Webservice(cnpj_certificado,
                                         ambiente, uf=uf, pacote='PL')
        print repr(webservice.consultar_cadastro(CNPJ=cnpj))
    except Exception as e:
        print e
    print '-' * 100
