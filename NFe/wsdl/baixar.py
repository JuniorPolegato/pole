#!/usr/bin/env python
# -*- coding: utf-8 -*-

import httplib
import os
import ssl
import socket
import sys
import time

# No Geany usando substiuição por expressões regulares:
# 1. Trocar "Voltar ao topo da página" por ""
# 2. Trocar "\n\n.*\(([^)]+)\).*$" por "\n        },\n        '\1': {"
# 3. Trocar "^([^\t\n]+)\t([^\t]+)\t(.+)$" por "            ('\1', '\2'): '\3',"
# 4. Trocar "^([^\n]+)2\.00 / 3\.10(.*)$" por "\12.00\2\n\13.10\2"
# 5. Ajustar manualmente casos em que ficaram 1.0 ou 2.0 ou 3.1
# 6. Retirar o "2" em "PR" de "homologacao.nfe2..." e "nfe2..."
# 7. Trocar "homologacao.sef.sefaz.rs.gov.br" por "homologacao.nfe.sefaz.rs.gov.br"
# 8. Duplicar endereço de MT e MS das versões 2.00 e 3.10
# 9. Trocar nos wsdl do CE de http porta 80 para https por 443 com: for arquivo in `grep -rinl '"http://[^"]*.gov.br:80' wsdl`; do echo $arquivo; sed -i 's/"http:\/\/\([^"]*.gov.br\):80/"https:\/\/\1:443/g' $arquivo; done

wsdls = {

    'homologacao': {

        # Copiado e colado em 31/03/2015 de
        # http://hom.nfe.fazenda.gov.br/portal/webServices.aspx
        #
        # Relação de Serviços Web
        #
        # UF que utilizam a SVAN - Sefaz Virtual do Ambiente Nacional: MA, PA, PI
        #
        # UF que utilizam a SVRS - Sefaz Virtual do RS:
        # - Para serviço de Consulta Cadastro: AC, RN, PB, SC, ES
        # - Para demais serviços relacionados com o sistema da NF-e: AC, AL, AP, DF, ES, PB, RJ, RN, RO, RR, SC, SE, TO
        #
        # Autorizadores em contingência:
        # - UF que utilizam a SVC-AN - Sefaz Virtual de Contingência Ambiente Nacional: AC, AL, AP, DF, ES, MG, PB, RJ, RN, RO, RR, RS, SC, SE, SP, TO
        # - UF que utilizam a SVC-RS - Sefaz Virtual de Contingência Rio Grande do Sul: AM, BA, CE, GO, MA, MS, MT, PA, PE, PI, PR
        #
        # Autorizadores: AM BA CE GO MG MA MS MT PE PR RS SP SVAN SVRS SVC-AN SVC-RS AN

        'AM': {
            ('RecepcaoEvento', '1.00'): 'https://homnfe.sefaz.am.gov.br/services2/services/RecepcaoEvento',
            ('NfeRecepcao', '2.00'): 'https://homnfe.sefaz.am.gov.br/services2/services/NfeRecepcao2',
            ('NfeRetRecepcao', '2.00'): 'https://homnfe.sefaz.am.gov.br/services2/services/NfeRetRecepcao2',
            ('NfeInutilizacao', '2.00'): 'https://homnfe.sefaz.am.gov.br/services2/services/NfeInutilizacao2',
            ('NfeInutilizacao', '3.10'): 'https://homnfe.sefaz.am.gov.br/services2/services/NfeInutilizacao2',
            ('NfeConsultaProtocolo', '2.00'): 'https://homnfe.sefaz.am.gov.br/services2/services/NfeConsulta2',
            ('NfeConsultaProtocolo', '3.10'): 'https://homnfe.sefaz.am.gov.br/services2/services/NfeConsulta2',
            ('NfeStatusServico', '2.00'): 'https://homnfe.sefaz.am.gov.br/services2/services/NfeStatusServico2',
            ('NfeStatusServico', '3.10'): 'https://homnfe.sefaz.am.gov.br/services2/services/NfeStatusServico2',
            ('NfeConsultaCadastro', '2.00'): 'https://homnfe.sefaz.am.gov.br/services2/services/CadConsultaCadastro2',
            ('NfeConsultaCadastro', '3.10'): 'https://homnfe.sefaz.am.gov.br/services2/services/CadConsultaCadastro2',
            ('NFeAutorizacao', '3.10'): 'https://homnfe.sefaz.am.gov.br/services2/services/NfeAutorizacao',
            ('NFeRetAutorizacao', '3.10'): 'https://homnfe.sefaz.am.gov.br/services2/services/NfeRetAutorizacao',
        },
        'BA': {
            ('NfeRecepcao', '2.00'): 'https://hnfe.sefaz.ba.gov.br/webservices/nfenw/NfeRecepcao2.asmx',
            ('NfeRetRecepcao', '2.00'): 'https://hnfe.sefaz.ba.gov.br/webservices/nfenw/NfeRetRecepcao2.asmx',
            ('NfeInutilizacao', '2.00'): 'https://hnfe.sefaz.ba.gov.br/webservices/nfenw/nfeinutilizacao2.asmx',
            ('NfeConsultaProtocolo', '2.00'): 'https://hnfe.sefaz.ba.gov.br/webservices/nfenw/nfeconsulta2.asmx',
            ('NfeStatusServico', '2.00'): 'https://hnfe.sefaz.ba.gov.br/webservices/nfenw/NfeStatusServico2.asmx',
            ('NfeConsultaCadastro', '2.00'): 'https://hnfe.sefaz.ba.gov.br/webservices/nfenw/CadConsultaCadastro2.asmx',
            ('NfeConsultaCadastro', '3.10'): 'https://hnfe.sefaz.ba.gov.br/webservices/nfenw/CadConsultaCadastro2.asmx',
            ('RecepcaoEvento', '2.00'): 'https://hnfe.sefaz.ba.gov.br/webservices/sre/recepcaoevento.asmx',
            ('RecepcaoEvento', '3.10'): 'https://hnfe.sefaz.ba.gov.br/webservices/sre/recepcaoevento.asmx',
            ('NfeInutilizacao', '3.10'): 'https://hnfe.sefaz.ba.gov.br/webservices/NfeInutilizacao/NfeInutilizacao.asmx',
            ('NfeConsultaProtocolo', '3.10'): 'https://hnfe.sefaz.ba.gov.br/webservices/NfeConsulta/NfeConsulta.asmx',
            ('NfeStatusServico', '3.10'): 'https://hnfe.sefaz.ba.gov.br/webservices/NfeStatusServico/NfeStatusServico.asmx',
            ('NFeAutorizacao', '3.10'): 'https://hnfe.sefaz.ba.gov.br/webservices/NfeAutorizacao/NfeAutorizacao.asmx',
            ('NFeRetAutorizacao', '3.10'): 'https://hnfe.sefaz.ba.gov.br/webservices/NfeRetAutorizacao/NfeRetAutorizacao.asmx',
        },
        'CE': {
            ('RecepcaoEvento', '1.00'): 'https://nfeh.sefaz.ce.gov.br/nfe2/services/RecepcaoEvento?wsdl',
            ('NfeRecepcao', '2.00'): 'https://nfeh.sefaz.ce.gov.br/nfe2/services/NfeRecepcao2?wsdl',
            ('NfeRetRecepcao', '2.00'): 'https://nfeh.sefaz.ce.gov.br/nfe2/services/NfeRetRecepcao2?wsdl',
            ('NfeInutilizacao', '2.00'): 'https://nfeh.sefaz.ce.gov.br/nfe2/services/NfeInutilizacao2?wsdl',
            ('NfeInutilizacao', '3.10'): 'https://nfeh.sefaz.ce.gov.br/nfe2/services/NfeInutilizacao2?wsdl',
            ('NfeConsultaProtocolo', '2.00'): 'https://nfeh.sefaz.ce.gov.br/nfe2/services/NfeConsulta2?wsdl',
            ('NfeConsultaProtocolo', '3.10'): 'https://nfeh.sefaz.ce.gov.br/nfe2/services/NfeConsulta2?wsdl',
            ('NfeStatusServico', '2.00'): 'https://nfeh.sefaz.ce.gov.br/nfe2/services/NfeStatusServico2?wsdl',
            ('NfeStatusServico', '3.10'): 'https://nfeh.sefaz.ce.gov.br/nfe2/services/NfeStatusServico2?wsdl',
            ('NfeConsultaCadastro', '2.00'): 'https://nfeh.sefaz.ce.gov.br/nfe2/services/CadConsultaCadastro2?wsdl',
            ('NfeConsultaCadastro', '3.10'): 'https://nfeh.sefaz.ce.gov.br/nfe2/services/CadConsultaCadastro2?wsdl',
            ('NfeDownloadNF', '2.00'): 'https://nfeh.sefaz.ce.gov.br/nfe2/services/NfeDownloadNF?wsdl',
            ('NfeDownloadNF', '3.10'): 'https://nfeh.sefaz.ce.gov.br/nfe2/services/NfeDownloadNF?wsdl',
            ('NFeAutorizacao', '3.10'): 'https://nfeh.sefaz.ce.gov.br/nfe2/services/NfeAutorizacao?wsdl',
            ('NFeRetAutorizacao', '3.10'): 'https://nfeh.sefaz.ce.gov.br/nfe2/services/NfeRetAutorizacao?wsdl',
        },
        'GO': {
            ('RecepcaoEvento', '1.00'): 'https://homolog.sefaz.go.gov.br/nfe/services/v2/RecepcaoEvento?wsdl',
            ('NfeRecepcao', '2.00'): 'https://homolog.sefaz.go.gov.br/nfe/services/v2/NfeRecepcao2?wsdl',
            ('NfeRetRecepcao', '2.00'): 'https://homolog.sefaz.go.gov.br/nfe/services/v2/NfeRetRecepcao2?wsdl',
            ('NfeInutilizacao', '2.00'): 'https://homolog.sefaz.go.gov.br/nfe/services/v2/NfeInutilizacao2?wsdl',
            ('NfeInutilizacao', '3.10'): 'https://homolog.sefaz.go.gov.br/nfe/services/v2/NfeInutilizacao2?wsdl',
            ('NfeConsultaProtocolo', '2.00'): 'https://homolog.sefaz.go.gov.br/nfe/services/v2/NfeConsulta2?wsdl',
            ('NfeConsultaProtocolo', '3.10'): 'https://homolog.sefaz.go.gov.br/nfe/services/v2/NfeConsulta2?wsdl',
            ('NfeStatusServico', '2.00'): 'https://homolog.sefaz.go.gov.br/nfe/services/v2/NfeStatusServico2?wsdl',
            ('NfeStatusServico', '3.10'): 'https://homolog.sefaz.go.gov.br/nfe/services/v2/NfeStatusServico2?wsdl',
            ('NfeConsultaCadastro', '2.00'): 'https://homolog.sefaz.go.gov.br/nfe/services/v2/CadConsultaCadastro2?wsdl',
            ('NfeConsultaCadastro', '3.10'): 'https://homolog.sefaz.go.gov.br/nfe/services/v2/CadConsultaCadastro2?wsdl',
            ('NFeAutorizacao', '3.10'): 'https://homolog.sefaz.go.gov.br/nfe/services/v2/NfeAutorizacao?wsdl',
            ('NFeRetAutorizacao', '3.10'): 'https://homolog.sefaz.go.gov.br/nfe/services/v2/NfeRetAutorizacao?wsdl',
        },
        'MG': {
            ('RecepcaoEvento', '1.00'): 'https://hnfe.fazenda.mg.gov.br/nfe2/services/RecepcaoEvento',
            ('NfeRecepcao', '2.00'): 'https://hnfe.fazenda.mg.gov.br/nfe2/services/NfeRecepcao2',
            ('NfeRetRecepcao', '2.00'): 'https://hnfe.fazenda.mg.gov.br/nfe2/services/NfeRetRecepcao2',
            ('NfeInutilizacao', '2.00'): 'https://hnfe.fazenda.mg.gov.br/nfe2/services/NfeInutilizacao2',
            ('NfeInutilizacao', '3.10'): 'https://hnfe.fazenda.mg.gov.br/nfe2/services/NfeInutilizacao2',
            ('NfeConsultaProtocolo', '2.00'): 'https://hnfe.fazenda.mg.gov.br/nfe2/services/NfeConsulta2',
            ('NfeConsultaProtocolo', '3.10'): 'https://hnfe.fazenda.mg.gov.br/nfe2/services/NfeConsulta2',
            ('NfeStatusServico', '2.00'): 'https://hnfe.fazenda.mg.gov.br/nfe2/services/NfeStatusServico2',
            ('NfeStatusServico', '3.10'): 'https://hnfe.fazenda.mg.gov.br/nfe2/services/NfeStatusServico2',
            ('NfeConsultaCadastro', '2.00'): 'https://hnfe.fazenda.mg.gov.br/nfe2/services/cadconsultacadastro2',
            ('NfeConsultaCadastro', '3.10'): 'https://hnfe.fazenda.mg.gov.br/nfe2/services/cadconsultacadastro2',
            ('NFeAutorizacao', '3.10'): 'https://hnfe.fazenda.mg.gov.br/nfe2/services/NfeAutorizacao',
            ('NFeRetAutorizacao', '3.10'): 'https://hnfe.fazenda.mg.gov.br/nfe2/services/NfeRetAutorizacao',
        },
        'MA': {
            ('NfeConsultaCadastro', '2.00'): 'https://sistemas.sefaz.ma.gov.br/wscadastro/CadConsultaCadastro2?wsdl',
        },
        'MS': {
            ('RecepcaoEvento', '1.00'): 'https://homologacao.nfe.ms.gov.br/homologacao/services2/RecepcaoEvento',
            ('NfeRecepcao', '2.00'): 'https://homologacao.nfe.ms.gov.br/homologacao/services2/NfeRecepcao2',
            ('NfeRetRecepcao', '2.00'): 'https://homologacao.nfe.ms.gov.br/homologacao/services2/NfeRetRecepcao2',
            ('NfeConsultaCadastro', '2.00'): 'https://homologacao.nfe.ms.gov.br/homologacao/services2/CadConsultaCadastro2',
            ('NfeConsultaCadastro', '3.10'): 'https://homologacao.nfe.ms.gov.br/homologacao/services2/CadConsultaCadastro2',
            ('NfeInutilizacao', '2.00'): 'https://homologacao.nfe.ms.gov.br/homologacao/services2/NfeInutilizacao2',
            ('NfeInutilizacao', '3.10'): 'https://homologacao.nfe.ms.gov.br/homologacao/services2/NfeInutilizacao2',
            ('NfeConsultaProtocolo', '2.00'): 'https://homologacao.nfe.ms.gov.br/homologacao/services2/NfeConsulta2',
            ('NfeConsultaProtocolo', '3.10'): 'https://homologacao.nfe.ms.gov.br/homologacao/services2/NfeConsulta2',
            ('NfeStatusServico', '2.00'): 'https://homologacao.nfe.ms.gov.br/homologacao/services2/NfeStatusServico2',
            ('NfeStatusServico', '3.10'): 'https://homologacao.nfe.ms.gov.br/homologacao/services2/NfeStatusServico2',
            ('NFeAutorizacao', '3.10'): 'https://homologacao.nfe.ms.gov.br/homologacao/services2/NfeAutorizacao',
            ('NFeRetAutorizacao', '3.10'): 'https://homologacao.nfe.ms.gov.br/homologacao/services2/NfeRetAutorizacao',
        },
        'MT': {
            ('NfeRecepcao', '2.00'): 'https://homologacao.sefaz.mt.gov.br/nfews/v2/services/NfeRecepcao2?wsdl',
            ('NfeRetRecepcao', '2.00'): 'https://homologacao.sefaz.mt.gov.br/nfews/v2/services/NfeRetRecepcao2?wsdl',
            ('NfeInutilizacao', '2.00'): 'https://homologacao.sefaz.mt.gov.br/nfews/v2/services/NfeInutilizacao2?wsdl',
            ('NfeConsultaProtocolo', '2.00'): 'https://homologacao.sefaz.mt.gov.br/nfews/v2/services/NfeConsulta2?wsdl',
            ('NfeStatusServico', '2.00'): 'https://homologacao.sefaz.mt.gov.br/nfews/v2/services/NfeStatusServico2?wsdl',
            ('NfeStatusServico', '3.10'): 'https://homologacao.sefaz.mt.gov.br/nfews/v2/services/NfeStatusServico2?wsdl',
            ('RecepcaoEvento', '2.00'): 'https://homologacao.sefaz.mt.gov.br/nfews/v2/services/RecepcaoEvento?wsdl',
            ('NfeConsultaCadastro', '3.10'): 'https://homologacao.sefaz.mt.gov.br/nfews/v2/services/CadConsultaCadastro2?wsdl',
            ('NFeAutorizacao', '3.10'): 'https://homologacao.sefaz.mt.gov.br/nfews/v2/services/NfeAutorizacao?wsdl',
            ('NFeRetAutorizacao', '3.10'): 'https://homologacao.sefaz.mt.gov.br/nfews/v2/services/NfeRetAutorizacao?wsdl',
        },
        'PE': {
            ('RecepcaoEvento', '1.00'): 'https://nfehomolog.sefaz.pe.gov.br/nfe-service/services/RecepcaoEvento',
            ('NfeRecepcao', '2.00'): 'https://nfehomolog.sefaz.pe.gov.br/nfe-service/services/NfeRecepcao2',
            ('NfeRetRecepcao', '2.00'): 'https://nfehomolog.sefaz.pe.gov.br/nfe-service/services/NfeRetRecepcao2',
            ('NfeInutilizacao', '2.00'): 'https://nfehomolog.sefaz.pe.gov.br/nfe-service/services/NfeInutilizacao2',
            ('NfeInutilizacao', '3.10'): 'https://nfehomolog.sefaz.pe.gov.br/nfe-service/services/NfeInutilizacao2',
            ('NfeConsultaProtocolo', '2.00'): 'https://nfehomolog.sefaz.pe.gov.br/nfe-service/services/NfeConsulta2',
            ('NfeConsultaProtocolo', '3.10'): 'https://nfehomolog.sefaz.pe.gov.br/nfe-service/services/NfeConsulta2',
            ('NfeStatusServico', '2.00'): 'https://nfehomolog.sefaz.pe.gov.br/nfe-service/services/NfeStatusServico2',
            ('NfeStatusServico', '3.10'): 'https://nfehomolog.sefaz.pe.gov.br/nfe-service/services/NfeStatusServico2',
            ('NFeAutorizacao', '3.10'): 'https://nfehomolog.sefaz.pe.gov.br/nfe-service/services/NfeAutorizacao?wsdl',
            ('NFeRetAutorizacao', '3.10'): 'https://nfehomolog.sefaz.pe.gov.br/nfe-service/services/NfeRetAutorizacao?wsdl',
        },
        'PR': {
            ('NfeRecepcao', '2.00'): 'https://homologacao.nfe.fazenda.pr.gov.br/nfe/NFeRecepcao2?wsdl',
            ('NfeRetRecepcao', '2.00'): 'https://homologacao.nfe.fazenda.pr.gov.br/nfe/NFeRetRecepcao2?wsdl',
            ('NfeInutilizacao', '2.00'): 'https://homologacao.nfe.fazenda.pr.gov.br/nfe/NFeInutilizacao2?wsdl',
            ('NfeConsultaProtocolo', '2.00'): 'https://homologacao.nfe.fazenda.pr.gov.br/nfe/NFeConsulta2?wsdl',
            ('NfeStatusServico', '2.00'): 'https://homologacao.nfe.fazenda.pr.gov.br/nfe/NFeStatusServico2?wsdl',
            ('NfeConsultaCadastro', '2.00'): 'https://homologacao.nfe.fazenda.pr.gov.br/nfe/CadConsultaCadastro2?wsdl',
            ('RecepcaoEvento', '2.00'): 'https://homologacao.nfe.fazenda.pr.gov.br/nfe-evento/NFeRecepcaoEvento?wsdl',
            ('NfeInutilizacao', '3.10'): 'https://homologacao.nfe.fazenda.pr.gov.br/nfe/NFeInutilizacao3?wsdl',
            ('NfeConsultaProtocolo', '3.10'): 'https://homologacao.nfe.fazenda.pr.gov.br/nfe/NFeConsulta3?wsdl',
            ('NfeStatusServico', '3.10'): 'https://homologacao.nfe.fazenda.pr.gov.br/nfe/NFeStatusServico3?wsdl',
            ('NfeConsultaCadastro', '3.10'): 'https://homologacao.nfe.fazenda.pr.gov.br/nfe/CadConsultaCadastro2?wsdl',
            ('RecepcaoEvento', '3.10'): 'https://homologacao.nfe.fazenda.pr.gov.br/nfe/NFeRecepcaoEvento?wsdl',
            ('NFeAutorizacao', '3.10'): 'https://homologacao.nfe.fazenda.pr.gov.br/nfe/NFeAutorizacao3?wsdl',
            ('NFeRetAutorizacao', '3.10'): 'https://homologacao.nfe.fazenda.pr.gov.br/nfe/NFeRetAutorizacao3?wsdl',
        },
        'RS': {
            ('RecepcaoEvento', '1.00'): 'https://homologacao.nfe.sefaz.rs.gov.br/ws/recepcaoevento/recepcaoevento.asmx',
            ('NfeRecepcao', '2.00'): 'https://homologacao.nfe.sefaz.rs.gov.br/ws/Nferecepcao/NFeRecepcao2.asmx',
            ('NfeRetRecepcao', '2.00'): 'https://homologacao.nfe.sefaz.rs.gov.br/ws/NfeRetRecepcao/NfeRetRecepcao2.asmx',
            ('NfeConsultaCadastro', '2.00'): 'https://sef.sefaz.rs.gov.br/ws/cadconsultacadastro/cadconsultacadastro2.asmx',
            ('NfeConsultaDest', '2.00'): 'https://homologacao.nfe.sefaz.rs.gov.br/ws/nfeConsultaDest/nfeConsultaDest.asmx',
            ('NfeDownloadNF', '2.00'): 'https://homologacao.nfe.sefaz.rs.gov.br/ws/nfeDownloadNF/nfeDownloadNF.asmx',
            ('NfeInutilizacao', '2.00'): 'https://homologacao.nfe.sefaz.rs.gov.br/ws/nfeinutilizacao/nfeinutilizacao2.asmx',
            ('NfeInutilizacao', '3.10'): 'https://homologacao.nfe.sefaz.rs.gov.br/ws/nfeinutilizacao/nfeinutilizacao2.asmx',
            ('NfeConsultaProtocolo', '2.00'): 'https://homologacao.nfe.sefaz.rs.gov.br/ws/NfeConsulta/NfeConsulta2.asmx',
            ('NfeConsultaProtocolo', '3.10'): 'https://homologacao.nfe.sefaz.rs.gov.br/ws/NfeConsulta/NfeConsulta2.asmx',
            ('NfeStatusServico', '2.00'): 'https://homologacao.nfe.sefaz.rs.gov.br/ws/NfeStatusServico/NfeStatusServico2.asmx',
            ('NfeStatusServico', '3.10'): 'https://homologacao.nfe.sefaz.rs.gov.br/ws/NfeStatusServico/NfeStatusServico2.asmx',
            ('NFeAutorizacao', '3.10'): 'https://homologacao.nfe.sefaz.rs.gov.br/ws/NfeAutorizacao/NFeAutorizacao.asmx',
            ('NFeRetAutorizacao', '3.10'): 'https://homologacao.nfe.sefaz.rs.gov.br/ws/NfeRetAutorizacao/NFeRetAutorizacao.asmx',
        },
        'SP': {
            ('NfeConsultaCadastro', '2.00'): 'https://homologacao.nfe.fazenda.sp.gov.br/nfeweb/services/cadconsultacadastro2.asmx',
            ('NfeRecepcao', '2.00'): 'https://homologacao.nfe.fazenda.sp.gov.br/nfeweb/services/NfeRecepcao2.asmx',
            ('NfeRetRecepcao', '2.00'): 'https://homologacao.nfe.fazenda.sp.gov.br/nfeweb/services/NfeRetRecepcao2.asmx',
            ('NfeInutilizacao', '2.00'): 'https://homologacao.nfe.fazenda.sp.gov.br/nfeweb/services/nfeinutilizacao2.asmx',
            ('NfeConsultaProtocolo', '2.00'): 'https://homologacao.nfe.fazenda.sp.gov.br/nfeweb/services/nfeconsulta2.asmx',
            ('NfeStatusServico', '2.00'): 'https://homologacao.nfe.fazenda.sp.gov.br/nfeweb/services/nfestatusservico2.asmx',
            ('RecepcaoEvento', '2.00'): 'https://homologacao.nfe.fazenda.sp.gov.br/eventosWEB/services/RecepcaoEvento.asmx',
            ('NfeInutilizacao', '3.10'): 'https://homologacao.nfe.fazenda.sp.gov.br/ws/nfeinutilizacao2.asmx',
            ('NfeConsultaProtocolo', '3.10'): 'https://homologacao.nfe.fazenda.sp.gov.br/ws/nfeconsulta2.asmx',
            ('NfeStatusServico', '3.10'): 'https://homologacao.nfe.fazenda.sp.gov.br/ws/nfestatusservico2.asmx',
            ('NfeConsultaCadastro', '3.10'): 'https://homologacao.nfe.fazenda.sp.gov.br/ws/cadconsultacadastro2.asmx',
            ('RecepcaoEvento', '3.10'): 'https://homologacao.nfe.fazenda.sp.gov.br/ws/recepcaoevento.asmx',
            ('NFeAutorizacao', '3.10'): 'https://homologacao.nfe.fazenda.sp.gov.br/ws/nfeautorizacao.asmx',
            ('NFeRetAutorizacao', '3.10'): 'https://homologacao.nfe.fazenda.sp.gov.br/ws/nferetautorizacao.asmx',
        },
        'SVAN': {
            ('RecepcaoEvento', '1.00'): 'https://hom.sefazvirtual.fazenda.gov.br/RecepcaoEvento/RecepcaoEvento.asmx',
            ('NfeRecepcao', '2.00'): 'https://hom.sefazvirtual.fazenda.gov.br/NfeRecepcao2/NfeRecepcao2.asmx',
            ('NfeRetRecepcao', '2.00'): 'https://hom.sefazvirtual.fazenda.gov.br/NfeRetRecepcao2/NfeRetRecepcao2.asmx',
            ('NfeInutilizacao', '2.00'): 'https://hom.sefazvirtual.fazenda.gov.br/NfeInutilizacao2/NfeInutilizacao2.asmx',
            ('NfeInutilizacao', '3.10'): 'https://hom.sefazvirtual.fazenda.gov.br/NfeInutilizacao2/NfeInutilizacao2.asmx',
            ('NfeConsultaProtocolo', '2.00'): 'https://hom.sefazvirtual.fazenda.gov.br/NfeConsulta2/NfeConsulta2.asmx',
            ('NfeConsultaProtocolo', '3.10'): 'https://hom.sefazvirtual.fazenda.gov.br/NfeConsulta2/NfeConsulta2.asmx',
            ('NfeStatusServico', '2.00'): 'https://hom.sefazvirtual.fazenda.gov.br/NfeStatusServico2/NfeStatusServico2.asmx',
            ('NfeStatusServico', '3.10'): 'https://hom.sefazvirtual.fazenda.gov.br/NfeStatusServico2/NfeStatusServico2.asmx',
            ('NfeDownloadNF', '2.00'): 'https://hom.sefazvirtual.fazenda.gov.br/NfeDownloadNF/NfeDownloadNF.asmx',
            ('NfeDownloadNF', '3.10'): 'https://hom.sefazvirtual.fazenda.gov.br/NfeDownloadNF/NfeDownloadNF.asmx',
            ('NFeAutorizacao', '3.10'): 'https://hom.sefazvirtual.fazenda.gov.br/NfeAutorizacao/NfeAutorizacao.asmx',
            ('NFeRetAutorizacao', '3.10'): 'https://hom.sefazvirtual.fazenda.gov.br/NfeRetAutorizacao/NfeRetAutorizacao.asmx',
        },
        'SVRS': {
            ('RecepcaoEvento', '1.00'): 'https://homologacao.nfe.sefazvirtual.rs.gov.br/ws/recepcaoevento/recepcaoevento.asmx',
            ('NfeRecepcao', '2.00'): 'https://homologacao.nfe.sefazvirtual.rs.gov.br/ws/Nferecepcao/NFeRecepcao2.asmx',
            ('NfeRetRecepcao', '2.00'): 'https://homologacao.nfe.sefazvirtual.rs.gov.br/ws/NfeRetRecepcao/NfeRetRecepcao2.asmx',
            ('NfeConsultaCadastro', '2.00'): 'https://homologacao.nfe.sefaz.rs.gov.br/ws/cadconsultacadastro/cadconsultacadastro2.asmx',
            ('NfeInutilizacao', '2.00'): 'https://homologacao.nfe.sefazvirtual.rs.gov.br/ws/nfeinutilizacao/nfeinutilizacao2.asmx',
            ('NfeInutilizacao', '3.10'): 'https://homologacao.nfe.sefazvirtual.rs.gov.br/ws/nfeinutilizacao/nfeinutilizacao2.asmx',
            ('NfeConsultaProtocolo', '2.00'): 'https://homologacao.nfe.sefazvirtual.rs.gov.br/ws/NfeConsulta/NfeConsulta2.asmx',
            ('NfeConsultaProtocolo', '3.10'): 'https://homologacao.nfe.sefazvirtual.rs.gov.br/ws/NfeConsulta/NfeConsulta2.asmx',
            ('NfeStatusServico', '2.00'): 'https://homologacao.nfe.sefazvirtual.rs.gov.br/ws/NfeStatusServico/NfeStatusServico2.asmx',
            ('NfeStatusServico', '3.10'): 'https://homologacao.nfe.sefazvirtual.rs.gov.br/ws/NfeStatusServico/NfeStatusServico2.asmx',
            ('NFeAutorizacao', '3.10'): 'https://homologacao.nfe.sefazvirtual.rs.gov.br/ws/NfeAutorizacao/NFeAutorizacao.asmx',
            ('NFeRetAutorizacao', '3.10'): 'https://homologacao.nfe.sefazvirtual.rs.gov.br/ws/NfeRetAutorizacao/NFeRetAutorizacao.asmx',
        },
        'SVC-AN': {
            ('RecepcaoEvento', '1.00'): 'https://hom.svc.fazenda.gov.br/RecepcaoEvento/RecepcaoEvento.asmx',
            ('NfeRecepcao', '2.00'): 'https://hom.svc.fazenda.gov.br/NfeRecepcao2/NfeRecepcao2.asmx',
            ('NfeRetRecepcao', '2.00'): 'https://hom.svc.fazenda.gov.br/NfeRetRecepcao2/NfeRetRecepcao2.asmx',
            ('NfeConsultaProtocolo', '2.00'): 'https://hom.svc.fazenda.gov.br/NfeConsulta2/NfeConsulta2.asmx',
            ('NfeConsultaProtocolo', '3.10'): 'https://hom.svc.fazenda.gov.br/NfeConsulta2/NfeConsulta2.asmx',
            ('NfeStatusServico', '2.00'): 'https://hom.svc.fazenda.gov.br/NfeStatusServico2/NfeStatusServico2.asmx',
            ('NfeStatusServico', '3.10'): 'https://hom.svc.fazenda.gov.br/NfeStatusServico2/NfeStatusServico2.asmx',
            ('NFeAutorizacao', '3.10'): 'https://hom.svc.fazenda.gov.br/NfeAutorizacao/NfeAutorizacao.asmx',
            ('NFeRetAutorizacao', '3.10'): 'https://hom.svc.fazenda.gov.br/NfeRetAutorizacao/NfeRetAutorizacao.asmx',
        },
        'SVC-RS': {
            ('RecepcaoEvento', '1.00'): 'https://homologacao.nfe.sefazvirtual.rs.gov.br/ws/recepcaoevento/recepcaoevento.asmx',
            ('NfeRecepcao', '2.00'): 'https://homologacao.nfe.sefazvirtual.rs.gov.br/ws/Nferecepcao/NFeRecepcao2.asmx',
            ('NfeRetRecepcao', '2.00'): 'https://homologacao.nfe.sefazvirtual.rs.gov.br/ws/NfeRetRecepcao/NfeRetRecepcao2.asmx',
            ('NfeConsultaProtocolo', '2.00'): 'https://homologacao.nfe.sefazvirtual.rs.gov.br/ws/NfeConsulta/NfeConsulta2.asmx',
            ('NfeConsultaProtocolo', '3.10'): 'https://homologacao.nfe.sefazvirtual.rs.gov.br/ws/NfeConsulta/NfeConsulta2.asmx',
            ('NfeStatusServico', '2.00'): 'https://homologacao.nfe.sefazvirtual.rs.gov.br/ws/NfeStatusServico/NfeStatusServico2.asmx',
            ('NfeStatusServico', '3.10'): 'https://homologacao.nfe.sefazvirtual.rs.gov.br/ws/NfeStatusServico/NfeStatusServico2.asmx',
            ('NFeAutorizacao', '3.10'): 'https://homologacao.nfe.sefazvirtual.rs.gov.br/ws/NfeAutorizacao/NFeAutorizacao.asmx',
            ('NFeRetAutorizacao', '3.10'): 'https://homologacao.nfe.sefazvirtual.rs.gov.br/ws/NfeRetAutorizacao/NFeRetAutorizacao.asmx',
        },
        'AN': {
            ('RecepcaoEvento', '1.00'): 'https://hom.nfe.fazenda.gov.br/RecepcaoEvento/RecepcaoEvento.asmx',
            ('NFeDistribuicaoDFe', '1.00'): 'https://hom.nfe.fazenda.gov.br/NFeDistribuicaoDFe/NFeDistribuicaoDFe.asmx',
            ('NfeConsultaDest', '2.00'): 'https://hom.nfe.fazenda.gov.br/NFeConsultaDest/NFeConsultaDest.asmx',
            ('NfeConsultaDest', '3.10'): 'https://hom.nfe.fazenda.gov.br/NFeConsultaDest/NFeConsultaDest.asmx',
            ('NfeDownloadNF', '2.00'): 'https://hom.nfe.fazenda.gov.br/NfeDownloadNF/NfeDownloadNF.asmx',
            ('NfeDownloadNF', '3.10'): 'https://hom.nfe.fazenda.gov.br/NfeDownloadNF/NfeDownloadNF.asmx',
        },
    },

    'producao': {

        # Copiado e colado em 31/03/2015 de
        # http://www.nfe.fazenda.gov.br/PORTAL/webServices.aspx
        #
        # Relação de Serviços Web
        #
        # UF que utilizam a SVAN - Sefaz Virtual do Ambiente Nacional: MA, PA, PI
        #
        # UF que utilizam a SVRS - Sefaz Virtual do RS:
        # - Para serviço de Consulta Cadastro: AC, ES, RN, PB, SC
        # - Para demais serviços relacionados com o sistema da NF-e: AC, AL, AP, DF, ES, PB, RJ, RN, RO, RR, SC, SE, TO
        #
        # Autorizadores em contingência:
        # - UF que utilizam a SVC-AN - Sefaz Virtual de Contingência Ambiente Nacional: AC, AL, AP, DF, ES, MG, PB, RJ, RN, RO, RR, RS, SC, SE, SP, TO
        # - UF que utilizam a SVC-RS - Sefaz Virtual de Contingência Rio Grande do Sul: AM, BA, CE, GO, MA, MS, MT, PA, PE, PI, PR
        #
        # Autorizadores: AM BA CE GO MG MA MS MT PE PR RS SP SVAN SVRS SVC-AN SVC-RS AN

        'AM': {
            ('RecepcaoEvento', '1.00'): 'https://nfe.sefaz.am.gov.br/services2/services/RecepcaoEvento',
            ('NfeRecepcao', '2.00'): 'https://nfe.sefaz.am.gov.br/services2/services/NfeRecepcao2',
            ('NfeRetRecepcao', '2.00'): 'https://nfe.sefaz.am.gov.br/services2/services/NfeRetRecepcao2',
            ('NfeInutilizacao', '2.00'): 'https://nfe.sefaz.am.gov.br/services2/services/NfeInutilizacao2',
            ('NfeInutilizacao', '3.10'): 'https://nfe.sefaz.am.gov.br/services2/services/NfeInutilizacao2',
            ('NfeConsultaProtocolo', '2.00'): 'https://nfe.sefaz.am.gov.br/services2/services/NfeConsulta2',
            ('NfeConsultaProtocolo', '3.10'): 'https://nfe.sefaz.am.gov.br/services2/services/NfeConsulta2',
            ('NfeStatusServico', '2.00'): 'https://nfe.sefaz.am.gov.br/services2/services/NfeStatusServico2',
            ('NfeStatusServico', '3.10'): 'https://nfe.sefaz.am.gov.br/services2/services/NfeStatusServico2',
            ('NfeConsultaCadastro', '2.00'): 'https://nfe.sefaz.am.gov.br/services2/services/CadConsultaCadastro2',
            ('NfeConsultaCadastro', '3.10'): 'https://nfe.sefaz.am.gov.br/services2/services/CadConsultaCadastro2',
            ('NFeAutorizacao', '3.10'): 'https://nfe.sefaz.am.gov.br/services2/services/NfeAutorizacao',
            ('NFeRetAutorizacao', '3.10'): 'https://nfe.sefaz.am.gov.br/services2/services/NfeRetAutorizacao',
        },
        'BA': {
            ('NfeRecepcao', '2.00'): 'https://nfe.sefaz.ba.gov.br/webservices/nfenw/NfeRecepcao2.asmx',
            ('NfeRetRecepcao', '2.00'): 'https://nfe.sefaz.ba.gov.br/webservices/nfenw/NfeRetRecepcao2.asmx',
            ('NfeInutilizacao', '2.00'): 'https://nfe.sefaz.ba.gov.br/webservices/nfenw/nfeinutilizacao2.asmx',
            ('NfeConsultaProtocolo', '2.00'): 'https://nfe.sefaz.ba.gov.br/webservices/nfenw/nfeconsulta2.asmx',
            ('NfeStatusServico', '2.00'): 'https://nfe.sefaz.ba.gov.br/webservices/nfenw/NfeStatusServico2.asmx',
            ('NfeConsultaCadastro', '2.00'): 'https://nfe.sefaz.ba.gov.br/webservices/nfenw/CadConsultaCadastro2.asmx',
            ('NfeConsultaCadastro', '3.10'): 'https://nfe.sefaz.ba.gov.br/webservices/nfenw/CadConsultaCadastro2.asmx',
            ('RecepcaoEvento', '2.00'): 'https://nfe.sefaz.ba.gov.br/webservices/sre/recepcaoevento.asmx',
            ('RecepcaoEvento', '3.10'): 'https://nfe.sefaz.ba.gov.br/webservices/sre/recepcaoevento.asmx',
            ('NfeInutilizacao', '3.10'): 'https://nfe.sefaz.ba.gov.br/webservices/NfeInutilizacao/NfeInutilizacao.asmx',
            ('NfeConsultaProtocolo', '3.10'): 'https://nfe.sefaz.ba.gov.br/webservices/NfeConsulta/NfeConsulta.asmx',
            ('NfeStatusServico', '3.10'): 'https://nfe.sefaz.ba.gov.br/webservices/NfeStatusServico/NfeStatusServico.asmx',
            ('NFeAutorizacao', '3.10'): 'https://nfe.sefaz.ba.gov.br/webservices/NfeAutorizacao/NfeAutorizacao.asmx',
            ('NFeRetAutorizacao', '3.10'): 'https://nfe.sefaz.ba.gov.br/webservices/NfeRetAutorizacao/NfeRetAutorizacao.asmx',
        },
        'CE': {
            ('RecepcaoEvento', '1.00'): 'https://nfe.sefaz.ce.gov.br/nfe2/services/RecepcaoEvento?wsdl',
            ('NfeRecepcao', '2.00'): 'https://nfe.sefaz.ce.gov.br/nfe2/services/NfeRecepcao2?wsdl',
            ('NfeRetRecepcao', '2.00'): 'https://nfe.sefaz.ce.gov.br/nfe2/services/NfeRetRecepcao2?wsdl',
            ('NfeInutilizacao', '2.00'): 'https://nfe.sefaz.ce.gov.br/nfe2/services/NfeInutilizacao2?wsdl',
            ('NfeInutilizacao', '3.10'): 'https://nfe.sefaz.ce.gov.br/nfe2/services/NfeInutilizacao2?wsdl',
            ('NfeConsultaProtocolo', '2.00'): 'https://nfe.sefaz.ce.gov.br/nfe2/services/NfeConsulta2?wsdl',
            ('NfeConsultaProtocolo', '3.10'): 'https://nfe.sefaz.ce.gov.br/nfe2/services/NfeConsulta2?wsdl',
            ('NfeStatusServico', '2.00'): 'https://nfe.sefaz.ce.gov.br/nfe2/services/NfeStatusServico2?wsdl',
            ('NfeStatusServico', '3.10'): 'https://nfe.sefaz.ce.gov.br/nfe2/services/NfeStatusServico2?wsdl',
            ('NfeConsultaCadastro', '2.00'): 'https://nfe.sefaz.ce.gov.br/nfe2/services/CadConsultaCadastro2?wsdl',
            ('NfeConsultaCadastro', '3.10'): 'https://nfe.sefaz.ce.gov.br/nfe2/services/CadConsultaCadastro2?wsdl',
            ('NfeDownloadNF', '2.00'): 'https://nfe.sefaz.ce.gov.br/nfe2/services/NfeDownloadNF?wsdl',
            ('NfeDownloadNF', '3.10'): 'https://nfe.sefaz.ce.gov.br/nfe2/services/NfeDownloadNF?wsdl',
            ('NFeAutorizacao', '3.10'): 'https://nfe.sefaz.ce.gov.br/nfe2/services/NfeAutorizacao?wsdl',
            ('NFeRetAutorizacao', '3.10'): 'https://nfe.sefaz.ce.gov.br/nfe2/services/NfeRetAutorizacao?wsdl',
        },
        'GO': {
            ('RecepcaoEvento', '1.00'): 'https://nfe.sefaz.go.gov.br/nfe/services/v2/RecepcaoEvento?wsdl',
            ('NfeRecepcao', '2.00'): 'https://nfe.sefaz.go.gov.br/nfe/services/v2/NfeRecepcao2?wsdl',
            ('NfeRetRecepcao', '2.00'): 'https://nfe.sefaz.go.gov.br/nfe/services/v2/NfeRetRecepcao2?wsdl',
            ('NfeInutilizacao', '2.00'): 'https://nfe.sefaz.go.gov.br/nfe/services/v2/NfeInutilizacao2?wsdl',
            ('NfeInutilizacao', '3.10'): 'https://nfe.sefaz.go.gov.br/nfe/services/v2/NfeInutilizacao2?wsdl',
            ('NfeConsultaProtocolo', '2.00'): 'https://nfe.sefaz.go.gov.br/nfe/services/v2/NfeConsulta2?wsdl',
            ('NfeConsultaProtocolo', '3.10'): 'https://nfe.sefaz.go.gov.br/nfe/services/v2/NfeConsulta2?wsdl',
            ('NfeStatusServico', '2.00'): 'https://nfe.sefaz.go.gov.br/nfe/services/v2/NfeStatusServico2?wsdl',
            ('NfeStatusServico', '3.10'): 'https://nfe.sefaz.go.gov.br/nfe/services/v2/NfeStatusServico2?wsdl',
            ('NfeConsultaCadastro', '2.00'): 'https://nfe.sefaz.go.gov.br/nfe/services/v2/CadConsultaCadastro2?wsdl',
            ('NfeConsultaCadastro', '3.10'): 'https://nfe.sefaz.go.gov.br/nfe/services/v2/CadConsultaCadastro2?wsdl',
            ('NFeAutorizacao', '3.10'): 'https://nfe.sefaz.go.gov.br/nfe/services/v2/NfeAutorizacao?wsdl',
            ('NFeRetAutorizacao', '3.10'): 'https://nfe.sefaz.go.gov.br/nfe/services/v2/NfeRetAutorizacao?wsdl',
        },
        'MG': {
            ('NfeRecepcao', '2.00'): 'https://nfe.fazenda.mg.gov.br/nfe2/services/NfeRecepcao2',
            ('NfeRetRecepcao', '2.00'): 'https://nfe.fazenda.mg.gov.br/nfe2/services/NfeRetRecepcao2',
            ('NfeInutilizacao', '2.00'): 'https://nfe.fazenda.mg.gov.br/nfe2/services/NfeInutilizacao2',
            ('NfeConsultaProtocolo', '2.00'): 'https://nfe.fazenda.mg.gov.br/nfe2/services/NfeConsulta2',
            ('NfeStatusServico', '2.00'): 'https://nfe.fazenda.mg.gov.br/nfe2/services/NfeStatus2',
            ('NfeStatusServico', '3.10'): 'https://nfe.fazenda.mg.gov.br/nfe2/services/NfeStatus2',
            ('NfeConsultaCadastro', '2.00'): 'https://nfe.fazenda.mg.gov.br/nfe2/services/cadconsultacadastro2',
            ('RecepcaoEvento', '2.00'): 'https://nfe.fazenda.mg.gov.br/nfe2/services/RecepcaoEvento',
            ('NFeAutorizacao', '3.10'): 'https://nfe.fazenda.mg.gov.br/nfe2/services/NfeAutorizacao',
            ('NFeRetAutorizacao', '3.10'): 'https://nfe.fazenda.mg.gov.br/nfe2/services/NfeRetAutorizacao',
        },
        'MA': {
            ('NfeConsultaCadastro', '2.00'): 'https://sistemas.sefaz.ma.gov.br/wscadastro/CadConsultaCadastro2?wsdl',
        },
        'MS': {
            ('RecepcaoEvento', '1.00'): 'https://nfe.fazenda.ms.gov.br/producao/services2/RecepcaoEvento',
            ('NfeRecepcao', '2.00'): 'https://nfe.fazenda.ms.gov.br/producao/services2/NfeRecepcao2',
            ('NfeRetRecepcao', '2.00'): 'https://nfe.fazenda.ms.gov.br/producao/services2/NfeRetRecepcao2',
            ('NfeConsultaCadastro', '2.00'): 'https://nfe.fazenda.ms.gov.br/producao/services2/CadConsultaCadastro2',
            ('NfeInutilizacao', '2.00'): 'https://nfe.fazenda.ms.gov.br/producao/services2/NfeInutilizacao2',
            ('NfeInutilizacao', '3.10'): 'https://nfe.fazenda.ms.gov.br/producao/services2/NfeInutilizacao2',
            ('NfeConsultaProtocolo', '2.00'): 'https://nfe.fazenda.ms.gov.br/producao/services2/NfeConsulta2',
            ('NfeConsultaProtocolo', '3.10'): 'https://nfe.fazenda.ms.gov.br/producao/services2/NfeConsulta2',
            ('NfeStatusServico', '2.00'): 'https://nfe.fazenda.ms.gov.br/producao/services2/NfeStatusServico2',
            ('NfeStatusServico', '3.10'): 'https://nfe.fazenda.ms.gov.br/producao/services2/NfeStatusServico2',
            ('NFeAutorizacao', '3.10'): 'https://nfe.fazenda.ms.gov.br/producao/services2/NfeAutorizacao',
            ('NFeRetAutorizacao', '3.10'): 'https://nfe.fazenda.ms.gov.br/producao/services2/NfeRetAutorizacao',
        },
        'MT': {
            ('NfeRecepcao', '2.00'): 'https://nfe.sefaz.mt.gov.br/nfews/v2/services/NfeRecepcao2?wsdl',
            ('NfeRetRecepcao', '2.00'): 'https://nfe.sefaz.mt.gov.br/nfews/v2/services/NfeRetRecepcao2?wsdl',
            ('NfeInutilizacao', '2.00'): 'https://nfe.sefaz.mt.gov.br/nfews/v2/services/NfeInutilizacao2?wsdl',
            ('NfeInutilizacao', '3.10'): 'https://nfe.sefaz.mt.gov.br/nfews/v2/services/NfeInutilizacao2?wsdl',
            ('NfeConsultaProtocolo', '2.00'): 'https://nfe.sefaz.mt.gov.br/nfews/v2/services/NfeConsulta2?wsdl',
            ('NfeConsultaProtocolo', '3.10'): 'https://nfe.sefaz.mt.gov.br/nfews/v2/services/NfeConsulta2?wsdl',
            ('NfeStatusServico', '2.00'): 'https://nfe.sefaz.mt.gov.br/nfews/v2/services/NfeStatusServico2?wsdl',
            ('NfeStatusServico', '3.10'): 'https://nfe.sefaz.mt.gov.br/nfews/v2/services/NfeStatusServico2?wsdl',
            ('NfeConsultaCadastro', '2.00'): 'https://nfe.sefaz.mt.gov.br/nfews/v2/services/CadConsultaCadastro2?wsdl',
            ('NfeConsultaCadastro', '3.10'): 'https://nfe.sefaz.mt.gov.br/nfews/v2/services/CadConsultaCadastro2?wsdl',
            ('RecepcaoEvento', '2.00'): 'https://nfe.sefaz.mt.gov.br/nfews/v2/services/RecepcaoEvento?wsdl',
            ('RecepcaoEvento', '3.10'): 'https://nfe.sefaz.mt.gov.br/nfews/v2/services/RecepcaoEvento?wsdl',
            ('NFeAutorizacao', '3.10'): 'https://nfe.sefaz.mt.gov.br/nfews/v2/services/NfeAutorizacao?wsdl',
            ('NFeRetAutorizacao', '3.10'): 'https://nfe.sefaz.mt.gov.br/nfews/v2/services/NfeRetAutorizacao?wsdl',
        },
        'PE': {
            ('RecepcaoEvento', '1.00'): 'https://nfe.sefaz.pe.gov.br/nfe-service/services/RecepcaoEvento',
            ('NfeRecepcao', '2.00'): 'https://nfe.sefaz.pe.gov.br/nfe-service/services/NfeRecepcao2',
            ('NfeRetRecepcao', '2.00'): 'https://nfe.sefaz.pe.gov.br/nfe-service/services/NfeRetRecepcao2',
            ('NfeInutilizacao', '2.00'): 'https://nfe.sefaz.pe.gov.br/nfe-service/services/NfeInutilizacao2',
            ('NfeInutilizacao', '3.10'): 'https://nfe.sefaz.pe.gov.br/nfe-service/services/NfeInutilizacao2',
            ('NfeConsultaProtocolo', '2.00'): 'https://nfe.sefaz.pe.gov.br/nfe-service/services/NfeConsulta2',
            ('NfeConsultaProtocolo', '3.10'): 'https://nfe.sefaz.pe.gov.br/nfe-service/services/NfeConsulta2',
            ('NfeStatusServico', '2.00'): 'https://nfe.sefaz.pe.gov.br/nfe-service/services/NfeStatusServico2',
            ('NfeStatusServico', '3.10'): 'https://nfe.sefaz.pe.gov.br/nfe-service/services/NfeStatusServico2',
            ('NfeConsultaCadastro', '2.00'): 'https://nfe.sefaz.pe.gov.br/nfe-service/services/CadConsultaCadastro2',
            ('NfeConsultaCadastro', '3.10'): 'https://nfe.sefaz.pe.gov.br/nfe-service/services/CadConsultaCadastro2',
            ('NFeAutorizacao', '3.10'): 'https://nfe.sefaz.pe.gov.br/nfe-service/services/NfeAutorizacao?wsdl',
            ('NFeRetAutorizacao', '3.10'): 'https://nfe.sefaz.pe.gov.br/nfe-service/services/NfeRetAutorizacao?wsdl',
        },
        'PR': {
            ('NfeRecepcao', '2.00'): 'https://nfe.fazenda.pr.gov.br/nfe/NFeRecepcao2?wsdl',
            ('NfeRetRecepcao', '2.00'): 'https://nfe.fazenda.pr.gov.br/nfe/NFeRetRecepcao2?wsdl',
            ('NfeInutilizacao', '2.00'): 'https://nfe.fazenda.pr.gov.br/nfe/NFeInutilizacao2?wsdl',
            ('NfeConsultaProtocolo', '2.00'): 'https://nfe.fazenda.pr.gov.br/nfe/NFeConsulta2?wsdl',
            ('NfeStatusServico', '2.00'): 'https://nfe.fazenda.pr.gov.br/nfe/NFeStatusServico2?wsdl',
            ('NfeConsultaCadastro', '2.00'): 'https://nfe.fazenda.pr.gov.br/nfe/CadConsultaCadastro2?wsdl',
            ('RecepcaoEvento', '2.00'): 'https://nfe.fazenda.pr.gov.br/nfe-evento/NFeRecepcaoEvento?wsdl',
            ('NfeInutilizacao', '3.10'): 'https://nfe.fazenda.pr.gov.br/nfe/NFeInutilizacao3?wsdl',
            ('NfeConsultaProtocolo', '3.10'): 'https://nfe.fazenda.pr.gov.br/nfe/NFeConsulta3?wsdl',
            ('NfeStatusServico', '3.10'): 'https://nfe.fazenda.pr.gov.br/nfe/NFeStatusServico3?wsdl',
            ('NfeConsultaCadastro', '3.10'): 'https://nfe.fazenda.pr.gov.br/nfe/CadConsultaCadastro2?wsdl',
            ('RecepcaoEvento', '3.10'): 'https://nfe.fazenda.pr.gov.br/nfe/NFeRecepcaoEvento?wsdl',
            ('NFeAutorizacao', '3.10'): 'https://nfe.fazenda.pr.gov.br/nfe/NFeAutorizacao3?wsdl',
            ('NFeRetAutorizacao', '3.10'): 'https://nfe.fazenda.pr.gov.br/nfe/NFeRetAutorizacao3?wsdl',
        },
        'RS': {
            ('RecepcaoEvento', '1.00'): 'https://nfe.sefaz.rs.gov.br/ws/recepcaoevento/recepcaoevento.asmx',
            ('NfeRecepcao', '2.00'): 'https://nfe.sefaz.rs.gov.br/ws/Nferecepcao/NFeRecepcao2.asmx',
            ('NfeRetRecepcao', '2.00'): 'https://nfe.sefaz.rs.gov.br/ws/NfeRetRecepcao/NfeRetRecepcao2.asmx',
            ('NfeConsultaCadastro', '2.00'): 'https://sef.sefaz.rs.gov.br/ws/cadconsultacadastro/cadconsultacadastro2.asmx',
            ('NfeConsultaDest', '2.00'): 'https://nfe.sefaz.rs.gov.br/ws/nfeConsultaDest/nfeConsultaDest.asmx',
            ('NfeDownloadNF', '2.00'): 'https://nfe.sefaz.rs.gov.br/ws/nfeDownloadNF/nfeDownloadNF.asmx',
            ('NfeInutilizacao', '2.00'): 'https://nfe.sefaz.rs.gov.br/ws/NfeInutilizacao/NfeInutilizacao2.asmx',
            ('NfeInutilizacao', '3.10'): 'https://nfe.sefaz.rs.gov.br/ws/NfeInutilizacao/NfeInutilizacao2.asmx',
            ('NfeConsultaProtocolo', '2.00'): 'https://nfe.sefaz.rs.gov.br/ws/NfeConsulta/NfeConsulta2.asmx',
            ('NfeConsultaProtocolo', '3.10'): 'https://nfe.sefaz.rs.gov.br/ws/NfeConsulta/NfeConsulta2.asmx',
            ('NfeStatusServico', '2.00'): 'https://nfe.sefaz.rs.gov.br/ws/NfeStatusServico/NfeStatusServico2.asmx',
            ('NfeStatusServico', '3.10'): 'https://nfe.sefaz.rs.gov.br/ws/NfeStatusServico/NfeStatusServico2.asmx',
            ('NFeAutorizacao', '3.10'): 'https://nfe.sefaz.rs.gov.br/ws/NfeAutorizacao/NFeAutorizacao.asmx',
            ('NFeRetAutorizacao', '3.10'): 'https://nfe.sefaz.rs.gov.br/ws/NfeRetAutorizacao/NFeRetAutorizacao.asmx',
        },
        'SP': {
            ('NfeRecepcao', '2.00'): 'https://nfe.fazenda.sp.gov.br/nfeweb/services/nferecepcao2.asmx',
            ('NfeRetRecepcao', '2.00'): 'https://nfe.fazenda.sp.gov.br/nfeweb/services/nferetrecepcao2.asmx',
            ('NfeInutilizacao', '2.00'): 'https://nfe.fazenda.sp.gov.br/nfeweb/services/nfeinutilizacao2.asmx',
            ('NfeConsultaProtocolo', '2.00'): 'https://nfe.fazenda.sp.gov.br/nfeweb/services/nfeconsulta2.asmx',
            ('NfeStatusServico', '2.00'): 'https://nfe.fazenda.sp.gov.br/nfeweb/services/nfestatusservico2.asmx',
            ('NfeConsultaCadastro', '2.00'): 'https://nfe.fazenda.sp.gov.br/nfeweb/services/cadconsultacadastro2.asmx',
            ('RecepcaoEvento', '2.00'): 'https://nfe.fazenda.sp.gov.br/eventosWEB/services/RecepcaoEvento.asmx',
            ('NfeInutilizacao', '3.10'): 'https://nfe.fazenda.sp.gov.br/ws/nfeinutilizacao2.asmx',
            ('NfeConsultaProtocolo', '3.10'): 'https://nfe.fazenda.sp.gov.br/ws/nfeconsulta2.asmx',
            ('NfeStatusServico', '3.10'): 'https://nfe.fazenda.sp.gov.br/ws/nfestatusservico2.asmx',
            ('NfeConsultaCadastro', '3.10'): 'https://nfe.fazenda.sp.gov.br/ws/cadconsultacadastro2.asmx',
            ('RecepcaoEvento', '3.10'): 'https://nfe.fazenda.sp.gov.br/ws/recepcaoevento.asmx',
            ('NFeAutorizacao', '3.10'): 'https://nfe.fazenda.sp.gov.br/ws/nfeautorizacao.asmx',
            ('NFeRetAutorizacao', '3.10'): 'https://nfe.fazenda.sp.gov.br/ws/nferetautorizacao.asmx',
        },
        'SVAN': {
            ('RecepcaoEvento', '1.00'): 'https://www.sefazvirtual.fazenda.gov.br/RecepcaoEvento/RecepcaoEvento.asmx',
            ('NfeRecepcao', '2.00'): 'https://www.sefazvirtual.fazenda.gov.br/NfeRecepcao2/NfeRecepcao2.asmx',
            ('NfeRetRecepcao', '2.00'): 'https://www.sefazvirtual.fazenda.gov.br/NfeRetRecepcao2/NfeRetRecepcao2.asmx',
            ('NfeInutilizacao', '2.00'): 'https://www.sefazvirtual.fazenda.gov.br/NfeInutilizacao2/NfeInutilizacao2.asmx',
            ('NfeInutilizacao', '3.10'): 'https://www.sefazvirtual.fazenda.gov.br/NfeInutilizacao2/NfeInutilizacao2.asmx',
            ('NfeConsultaProtocolo', '2.00'): 'https://www.sefazvirtual.fazenda.gov.br/NfeConsulta2/NfeConsulta2.asmx',
            ('NfeConsultaProtocolo', '3.10'): 'https://www.sefazvirtual.fazenda.gov.br/NfeConsulta2/NfeConsulta2.asmx',
            ('NfeStatusServico', '2.00'): 'https://www.sefazvirtual.fazenda.gov.br/NfeStatusServico2/NfeStatusServico2.asmx',
            ('NfeStatusServico', '3.10'): 'https://www.sefazvirtual.fazenda.gov.br/NfeStatusServico2/NfeStatusServico2.asmx',
            ('NfeDownloadNF', '2.00'): 'https://www.sefazvirtual.fazenda.gov.br/NfeDownloadNF/NfeDownloadNF.asmx',
            ('NfeDownloadNF', '3.10'): 'https://www.sefazvirtual.fazenda.gov.br/NfeDownloadNF/NfeDownloadNF.asmx',
            ('NFeAutorizacao', '3.10'): 'https://www.sefazvirtual.fazenda.gov.br/NfeAutorizacao/NfeAutorizacao.asmx',
            ('NFeRetAutorizacao', '3.10'): 'https://www.sefazvirtual.fazenda.gov.br/NfeRetAutorizacao/NfeRetAutorizacao.asmx',
        },
        'SVRS': {
            ('RecepcaoEvento', '1.00'): 'https://nfe.sefazvirtual.rs.gov.br/ws/recepcaoevento/recepcaoevento.asmx',
            ('NfeRecepcao', '2.00'): 'https://nfe.sefazvirtual.rs.gov.br/ws/Nferecepcao/NFeRecepcao2.asmx',
            ('NfeRetRecepcao', '2.00'): 'https://nfe.sefazvirtual.rs.gov.br/ws/NfeRetRecepcao/NfeRetRecepcao2.asmx',
            ('NfeConsultaCadastro', '2.00'): 'https://svp-ws.sefazvirtual.rs.gov.br/ws/CadConsultaCadastro/CadConsultaCadastro2.asmx',
            ('NfeInutilizacao', '2.00'): 'https://nfe.sefazvirtual.rs.gov.br/ws/nfeinutilizacao/nfeinutilizacao2.asmx',
            ('NfeInutilizacao', '3.10'): 'https://nfe.sefazvirtual.rs.gov.br/ws/nfeinutilizacao/nfeinutilizacao2.asmx',
            ('NfeConsultaProtocolo', '2.00'): 'https://nfe.sefazvirtual.rs.gov.br/ws/NfeConsulta/NfeConsulta2.asmx',
            ('NfeConsultaProtocolo', '3.10'): 'https://nfe.sefazvirtual.rs.gov.br/ws/NfeConsulta/NfeConsulta2.asmx',
            ('NfeStatusServico', '2.00'): 'https://nfe.sefazvirtual.rs.gov.br/ws/NfeStatusServico/NfeStatusServico2.asmx',
            ('NfeStatusServico', '3.10'): 'https://nfe.sefazvirtual.rs.gov.br/ws/NfeStatusServico/NfeStatusServico2.asmx',
            ('NFeAutorizacao', '3.10'): 'https://nfe.sefazvirtual.rs.gov.br/ws/NfeAutorizacao/NFeAutorizacao.asmx',
            ('NFeRetAutorizacao', '3.10'): 'https://nfe.sefazvirtual.rs.gov.br/ws/NfeRetAutorizacao/NFeRetAutorizacao.asmx',
        },
        'SVC-AN': {
            ('RecepcaoEvento', '1.00'): 'https://www.svc.fazenda.gov.br/RecepcaoEvento/RecepcaoEvento.asmx',
            ('NfeRecepcao', '2.00'): 'https://www.svc.fazenda.gov.br/NfeRecepcao2/NfeRecepcao2.asmx',
            ('NfeRetRecepcao', '2.00'): 'https://www.svc.fazenda.gov.br/NfeRetRecepcao2/NfeRetRecepcao2.asmx',
            ('NfeConsultaProtocolo', '2.00'): 'https://www.svc.fazenda.gov.br/NfeConsulta2/NfeConsulta2.asmx',
            ('NfeConsultaProtocolo', '3.10'): 'https://www.svc.fazenda.gov.br/NfeConsulta2/NfeConsulta2.asmx',
            ('NfeStatusServico', '2.00'): 'https://www.svc.fazenda.gov.br/NfeStatusServico2/NfeStatusServico2.asmx',
            ('NfeStatusServico', '3.10'): 'https://www.svc.fazenda.gov.br/NfeStatusServico2/NfeStatusServico2.asmx',
            ('NFeAutorizacao', '3.10'): 'https://www.svc.fazenda.gov.br/NfeAutorizacao/NfeAutorizacao.asmx',
            ('NFeRetAutorizacao', '3.10'): 'https://www.svc.fazenda.gov.br/NfeRetAutorizacao/NfeRetAutorizacao.asmx',
        },
        'SVC-RS': {
            ('RecepcaoEvento', '1.00'): 'https://nfe.sefazvirtual.rs.gov.br/ws/recepcaoevento/recepcaoevento.asmx',
            ('NfeRecepcao', '2.00'): 'https://nfe.sefazvirtual.rs.gov.br/ws/Nferecepcao/NFeRecepcao2.asmx',
            ('NfeRetRecepcao', '2.00'): 'https://nfe.sefazvirtual.rs.gov.br/ws/NfeRetRecepcao/NfeRetRecepcao2.asmx',
            ('NfeConsultaProtocolo', '2.00'): 'https://nfe.sefazvirtual.rs.gov.br/ws/NfeConsulta/NfeConsulta2.asmx',
            ('NfeConsultaProtocolo', '3.10'): 'https://nfe.sefazvirtual.rs.gov.br/ws/NfeConsulta/NfeConsulta2.asmx',
            ('NfeStatusServico', '2.00'): 'https://nfe.sefazvirtual.rs.gov.br/ws/NfeStatusServico/NfeStatusServico2.asmx',
            ('NfeStatusServico', '3.10'): 'https://nfe.sefazvirtual.rs.gov.br/ws/NfeStatusServico/NfeStatusServico2.asmx',
            ('NFeAutorizacao', '3.10'): 'https://nfe.sefazvirtual.rs.gov.br/ws/NfeAutorizacao/NFeAutorizacao.asmx',
            ('NFeRetAutorizacao', '3.10'): 'https://nfe.sefazvirtual.rs.gov.br/ws/NfeRetAutorizacao/NFeRetAutorizacao.asmx',
        },
        'AN': {
            ('RecepcaoEvento', '1.00'): 'https://www.nfe.fazenda.gov.br/RecepcaoEvento/RecepcaoEvento.asmx',
            ('NFeDistribuicaoDFe', '1.00'): 'https://www1.nfe.fazenda.gov.br/NFeDistribuicaoDFe/NFeDistribuicaoDFe.asmx',
            ('NfeConsultaDest', '2.00'): 'https://www.nfe.fazenda.gov.br/NFeConsultaDest/NFeConsultaDest.asmx',
            ('NfeConsultaDest', '3.10'): 'https://www.nfe.fazenda.gov.br/NFeConsultaDest/NFeConsultaDest.asmx',
            ('NfeDownloadNF', '2.00'): 'https://www.nfe.fazenda.gov.br/NfeDownloadNF/NfeDownloadNF.asmx',
            ('NfeDownloadNF', '3.10'): 'https://www.nfe.fazenda.gov.br/NfeDownloadNF/NfeDownloadNF.asmx',
        }
    }
}

cnpj = raw_input('CNPJ: ')
home = os.getenv('HOME')
key_file = '%s/NFe/cnpjs/%s/certificado_digital/chave.pem' % (home, cnpj)
cert_file = '%s/NFe/cnpjs/%s/certificado_digital/certificado.pem' % (home, cnpj)


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
            print 'Aqui passou'
            self.sock = sock
            self._tunnel()
        self.sock = ssl.wrap_socket(sock, self.key_file, self.cert_file, ssl_version=ssl.PROTOCOL_SSLv23)


def criar_diretorios(sefaz, mostra_erro=False):
    for ambiente in ('producao', 'homologacao'):
        for versao in ('1.00', '2.00', '3.10'):
            try:
                os.makedirs('%s/%s/%s' % (sefaz, ambiente, versao))
            except os.error as erro:
                if mostra_erro:
                    print erro

cab_xml = "<?xml version='1.0' encoding='UTF-8'?>"

for ambiente, wss in wsdls.items():
    print ambiente
    for sefaz, servicos in wss.items():
        print ' ', sefaz
        criar_diretorios(sefaz)
        for (servico, versao), url in servicos.items():
            servico += '.wsdl'
            servidor, uri = url[8:].split('/', 1)
            uri = '/' + uri + ('?wsdl' if uri[-5:].lower() != '?wsdl' else '')
            print '   ', servico
            print '     ', servidor
            print '       ', uri
            c = 0
            while True:
                try:
                    # A sefaz MT tem problemas com o HTTPSConnection acima
                    # mas funciona com o httplib.HTTPSConnection
                    if sefaz == 'MT':
                        conexao = httplib.HTTPSConnection(servidor, 443, key_file, cert_file)
                    # Algumas sefaz tem problemas com httplib.HTTPSConnection
                    # mas todas as outras funcionam com o HTTPSConnection acima
                    else:
                        conexao = HTTPSConnection(servidor, 443, key_file, cert_file)
                    conexao.request('GET', uri)
                    wsdl = conexao.getresponse().read()
                    conexao.close()
                    if wsdl[:6] != cab_xml[:6]:
                        wsdl = cab_xml + wsdl
                    open('%s/%s/%s/%s' % (sefaz, ambiente, versao, servico), 'wb').write(wsdl)
                    break
                except:
                    print sys.exc_info()
                    if c > 4:
                        break
                    c += 1
                    time.sleep(1)
