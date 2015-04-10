#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Usando openssl em linha de comando:
# openssl pkcs12 -nodes -clcerts -nokeys -in certificado.pfx -out certificado.pem
# openssl pkcs12 -nodes -nocerts -in certificado.pfx -out chave.pem

from OpenSSL.crypto import *
import os

cnpj = raw_input('CNPJ: ')
passwd = raw_input('Senha: ')

cd = '%s/NFe/cnpjs/%s/certificado_digital/' % (os.getenv('HOME'), cnpj)

p12 = load_pkcs12(open(cd + 'certificado.pfx', 'rb').read(), passwd)

pkey = p12.get_privatekey()
open(cd + 'chave.pem', 'wb').write(dump_privatekey(FILETYPE_PEM, pkey))

cert = p12.get_certificate()
open(cd + 'certificado.pem', 'wb').write(dump_certificate(FILETYPE_PEM, cert))

ca_certs = p12.get_ca_certificates()
ca_file = open(cd + 'ca.pem', 'wb')
for ca in ca_certs:
    ca_file.write(dump_certificate(FILETYPE_PEM, ca))
