#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pole
import logging

# logging.basicConfig(level=logging.DEBUG)


cnpj = raw_input('CNPJ: ')
nfe = raw_input('Chave da NFe: ')

ambiente = pole.nfe.PRODUCAO
webservice = pole.nfe.Webservice(cnpj, ambiente)

# Ciência da Operação
print '-' * 100
xml_ciencia = webservice.manifestar('Ciencia da Operacao', nfe)
nome = str(xml_ciencia.procEventoNFe.evento.infEvento.detEvento.descEvento)
nome = nfe + '-' + nome.replace(' ', '_') + '.xml'
with open(nome, 'wb') as arquivo:
    arquivo.write(pole.xml.serializar(xml_ciencia))
print '-' * 20 + ' ' + nome + ' ' + '-' * 20
print repr(xml_ciencia)
print '-' * 100

# NFe
print '-' * 20 + ' ' + nfe + '-nfe.xml' + ' ' + '-' * 20
xml_nfe = webservice.download_nfe(nfe)
with open(nfe + '-nfe.xml', 'wb') as arquivo:
    arquivo.write(pole.xml.serializar(xml_nfe))
print repr(xml_nfe)
print '-' * 100

# Eventos
xmls_eventos = webservice.lista_eventos(nfe)
print 'Eventos:', len(xmls_eventos)
for ev in xmls_eventos:
    nome = str(ev.procEventoNFe.evento.infEvento.detEvento.descEvento)
    nome = nfe + '-' + nome.replace(' ', '_') + '.xml'
    with open(nome, 'wb') as arquivo:
        arquivo.write(pole.xml.serializar(ev))
    print '-' * 20 + ' ' + nome + ' ' + '-' * 20
    print repr(ev)

print '=' * 100
