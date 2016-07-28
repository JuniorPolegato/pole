#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pole

cnpj = raw_input('CNPJ: ')
nfe = raw_input('Chave da NFe: ')

ambiente = pole.nfe.PRODUCAO
webservice = pole.nfe.Webservice(cnpj, ambiente, uf='AN')

xml_ciencia = webservice.manifestar('Ciencia da Operacao', nfe)
xml_nfe = webservice.download_nfe(nfe)
xmls_eventos = webservice.download_eventos(nfe)

print '-' * 100
print repr(xml_ciencia)
print '-' * 100
print repr(xml_nfe)
print '-' * 100
for ev in xmls_eventos:
    print repr(ev)
    print '-' * 100

# Salvar XML da NFe
with open(nfe + '-nfe.xml', 'wb') as arquivo:
    arquivo.write(pole.xml.serializar(xml_nfe))

# Salvar XML de cada evento
for ev in xmls_eventos:
    nome = str(ev.procEventoNFe.evento.infEvento.detEvento.descEvento)
    nome = nome.replace(' ', '_') + '-' + nfe + '.xml'
    with open(nome, 'wb') as arquivo:
        arquivo.write(pole.xml.serializar(ev))
