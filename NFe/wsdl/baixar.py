#!/usr/bin/env python
# -*- coding: utf-8 -*-

import httplib
import os
import ssl
import socket
import sys

# UF que utilizam a SVAN - Sefaz Virtual do Ambiente Nacional: MA, PA, PI
# UF que utilizam a SVRS - Sefaz Virtual do RS:
# - Para serviço de Consulta Cadastro: AC, RN, PB, SC
# - Para demais serviços relacionados com o sistema da NF-e: AC, AL, AP, DF, ES, PB, RJ, RN, RO, RR, SC, SE, TO
# Autorizadores em contingência:
# - UF que utilizam a SVC-AN - Sefaz Virtual de Contingência Ambiente Nacional: AC, AL, AP, DF, ES, MG, PB, RJ, RN, RO, RR, RS, SC, SE, SP, TO
# - UF que utilizam a SVC-RS - Sefaz Virtual de Contingência Rio Grande do Sul: AM, BA, CE, GO, MA, MS, MT, PA, PE, PI, PR

wsdls = {
    'homologacao':{
        'AM': {
            'NfeRecepcao2': 'https://homnfe.sefaz.am.gov.br/services2/services/NfeRecepcao2',
            'NfeRetRecepcao2': 'https://homnfe.sefaz.am.gov.br/services2/services/NfeRetRecepcao2',
            'NfeInutilizacao2': 'https://homnfe.sefaz.am.gov.br/services2/services/NfeInutilizacao2',
            'NfeConsulta2': 'https://homnfe.sefaz.am.gov.br/services2/services/NfeConsulta2',
            'NfeStatusServico2': 'https://homnfe.sefaz.am.gov.br/services2/services/NfeStatusServico2',
            'CadConsultaCadastro2': 'https://homnfe.sefaz.am.gov.br/services2/services/CadConsultaCadastro2',
            'RecepcaoEvento': 'https://homnfe.sefaz.am.gov.br/services2/services/RecepcaoEvento',
            'NfeAutorizacao': 'https://homnfe.sefaz.am.gov.br/services2/services/NfeAutorizacao',
            'NfeRetAutorizacao': 'https://homnfe.sefaz.am.gov.br/services2/services/NfeRetAutorizacao'},
        'BA': {
            'NfeRecepcao2': 'https://hnfe.sefaz.ba.gov.br/webservices/nfenw/NfeRecepcao2.asmx',
            'NfeRetRecepcao2': 'https://hnfe.sefaz.ba.gov.br/webservices/nfenw/NfeRetRecepcao2.asmx',
            'NfeInutilizacao2': 'https://hnfe.sefaz.ba.gov.br/webservices/nfenw/nfeinutilizacao2.asmx',
            'NfeConsulta2': 'https://hnfe.sefaz.ba.gov.br/webservices/nfenw/nfeconsulta2.asmx',
            'NfeStatusServico2': 'https://hnfe.sefaz.ba.gov.br/webservices/nfenw/NfeStatusServico2.asmx',
            'CadConsultaCadastro2': 'https://hnfe.sefaz.ba.gov.br/webservices/nfenw/CadConsultaCadastro2.asmx',
            'RecepcaoEvento': 'https://hnfe.sefaz.ba.gov.br/webservices/sre/recepcaoevento.asmx',
            'NfeStatusServico': 'https://hnfe.sefaz.ba.gov.br/webservices/NfeStatusServico/NfeStatusServico.asmx',
            'NfeAutorizacao': 'https://hnfe.sefaz.ba.gov.br/webservices/NfeAutorizacao/NfeAutorizacao.asmx',
            'NfeRetAutorizacao': 'https://hnfe.sefaz.ba.gov.br/webservices/NfeRetAutorizacao/NfeRetAutorizacao.asmx'},
        'CE': {
            'NfeRecepcao2': 'https://nfeh.sefaz.ce.gov.br/nfe2/services/NfeRecepcao2',
            'NfeRetRecepcao2': 'https://nfeh.sefaz.ce.gov.br/nfe2/services/NfeRetRecepcao2',
            'NfeInutilizacao2': 'https://nfeh.sefaz.ce.gov.br/nfe2/services/NfeInutilizacao2',
            'NfeConsulta2': 'https://nfeh.sefaz.ce.gov.br/nfe2/services/NfeConsulta2',
            'NfeStatusServico2': 'https://nfeh.sefaz.ce.gov.br/nfe2/services/NfeStatusServico2',
            'CadConsultaCadastro2': 'https://nfeh.sefaz.ce.gov.br/nfe2/services/CadConsultaCadastro2',
            'RecepcaoEvento': 'https://nfeh.sefaz.ce.gov.br/nfe2/services/RecepcaoEvento'},
        'ES': {
            'CadConsultaCadastro2': 'https://app.sefaz.es.gov.br/ConsultaCadastroService/CadConsultaCadastro2.asmx'},
        'GO': {
            'NfeRecepcao2': 'https://homolog.sefaz.go.gov.br/nfe/services/v2/NfeRecepcao2',
            'NfeRetRecepcao2': 'https://homolog.sefaz.go.gov.br/nfe/services/v2/NfeRetRecepcao2',
            'NfeInutilizacao2': 'https://homolog.sefaz.go.gov.br/nfe/services/v2/NfeInutilizacao2',
            'NfeConsulta2': 'https://homolog.sefaz.go.gov.br/nfe/services/v2/NfeConsulta2',
            'NfeStatusServico2': 'https://homolog.sefaz.go.gov.br/nfe/services/v2/NfeStatusServico2',
            'CadConsultaCadastro2': 'https://homolog.sefaz.go.gov.br/nfe/services/v2/CadConsultaCadastro2',
            'RecepcaoEvento': 'https://homolog.sefaz.go.gov.br/nfe/services/v2/RecepcaoEvento',
            'NfeAutorizacao': 'https://homolog.sefaz.go.gov.br/nfe/services/v2/NfeAutorizacao',
            'NfeRetAutorizacao': 'https://homolog.sefaz.go.gov.br/nfe/services/v2/NfeRetAutorizacao'},
        'MT': {
            'NfeRecepcao2': 'https://homologacao.sefaz.mt.gov.br/nfews/v2/services/NfeRecepcao2',
            'NfeRetRecepcao2': 'https://homologacao.sefaz.mt.gov.br/nfews/v2/services/NfeRetRecepcao2',
            'NfeInutilizacao2': 'https://homologacao.sefaz.mt.gov.br/nfews/v2/services/NfeInutilizacao2',
            'NfeConsulta2': 'https://homologacao.sefaz.mt.gov.br/nfews/v2/services/NfeConsulta2',
            'NfeStatusServico2': 'https://homologacao.sefaz.mt.gov.br/nfews/v2/services/NfeStatusServico2',
            'RecepcaoEvento': 'https://homologacao.sefaz.mt.gov.br/nfews/v2/services/RecepcaoEvento',
            'CadConsultaCadastro2': 'https://homologacao.sefaz.mt.gov.br/nfews/v2/services/CadConsultaCadastro2',
            'NfeAutorizacao': 'https://homologacao.sefaz.mt.gov.br/nfews/v2/services/NfeAutorizacao',
            'NfeRetAutorizacao': 'https://homologacao.sefaz.mt.gov.br/nfews/v2/services/NfeRetAutorizacao'},
        'MS': {
            'NfeRecepcao2': 'https://homologacao.nfe.ms.gov.br/homologacao/services2/NfeRecepcao2',
            'NfeRetRecepcao2': 'https://homologacao.nfe.ms.gov.br/homologacao/services2/NfeRetRecepcao2',
            'NfeInutilizacao2': 'https://homologacao.nfe.ms.gov.br/homologacao/services2/NfeInutilizacao2',
            'NfeConsulta2': 'https://homologacao.nfe.ms.gov.br/homologacao/services2/NfeConsulta2',
            'NfeStatusServico2': 'https://homologacao.nfe.ms.gov.br/homologacao/services2/NfeStatusServico2',
            'CadConsultaCadastro2': 'https://homologacao.nfe.ms.gov.br/homologacao/services2/CadConsultaCadastro2',
            'RecepcaoEvento': 'https://homologacao.nfe.ms.gov.br/homologacao/services2/RecepcaoEvento',
            'NfeAutorizacao': 'https://homologacao.nfe.ms.gov.br/homologacao/services2/NfeAutorizacao',
            'NfeRetAutorizacao': 'https://homologacao.nfe.ms.gov.br/homologacao/services2/NfeRetAutorizacao'},
        'MG': {
            'NfeRecepcao2': 'https://hnfe.fazenda.mg.gov.br/nfe2/services/NfeRecepcao2',
            'NfeRetRecepcao2': 'https://hnfe.fazenda.mg.gov.br/nfe2/services/NfeRetRecepcao2',
            'NfeInutilizacao2': 'https://hnfe.fazenda.mg.gov.br/nfe2/services/NfeInutilizacao2',
            'NfeConsulta2': 'https://hnfe.fazenda.mg.gov.br/nfe2/services/NfeConsulta2',
            'NfeStatusServico2': 'https://hnfe.fazenda.mg.gov.br/nfe2/services/NfeStatusServico2',
            'CadConsultaCadastro2': 'https://hnfe.fazenda.mg.gov.br/nfe2/services/cadconsultacadastro2',
            'RecepcaoEvento': 'https://hnfe.fazenda.mg.gov.br/nfe2/services/RecepcaoEvento',
            'NfeAutorizacao': 'https://hnfe.fazenda.mg.gov.br/nfe2/services/NfeAutorizacao',
            'NfeRetAutorizacao': 'https://hnfe.fazenda.mg.gov.br/nfe2/services/NfeRetAutorizacao'},
        'PR': {
            'NfeRecepcao2': 'https://homologacao.nfe2.fazenda.pr.gov.br/nfe/NFeRecepcao2',
            'NfeRetRecepcao2': 'https://homologacao.nfe2.fazenda.pr.gov.br/nfe/NFeRetRecepcao2',
            'NfeInutilizacao2': 'https://homologacao.nfe2.fazenda.pr.gov.br/nfe/NFeInutilizacao2',
            'NfeConsulta2': 'https://homologacao.nfe2.fazenda.pr.gov.br/nfe/NFeConsulta2',
            'NfeStatusServico2': 'https://homologacao.nfe2.fazenda.pr.gov.br/nfe/NFeStatusServico2',
            'CadConsultaCadastro2': 'https://homologacao.nfe2.fazenda.pr.gov.br/nfe/CadConsultaCadastro2',
            'RecepcaoEvento': 'https://homologacao.nfe2.fazenda.pr.gov.br/nfe-evento/NFeRecepcaoEvento',
            'NfeRecepcao3': 'https://homologacao.nfe.fazenda.pr.gov.br/nfe/NFeRecepcao3',
            'NfeInutilizacao3': 'https://homologacao.nfe.fazenda.pr.gov.br/nfe/NFeInutilizacao3',
            'NfeConsulta3': 'https://homologacao.nfe.fazenda.pr.gov.br/nfe/NFeConsulta3',
            'NfeStatusServico3 ': 'https://homologacao.nfe.fazenda.pr.gov.br/nfe/NFeStatusServico3 ',
            'CadConsultaCadastro2': 'https://homologacao.nfe.fazenda.pr.gov.br/nfe/CadConsultaCadastro2',
            'NfeRecepcaoEvento': 'https://homologacao.nfe.fazenda.pr.gov.br/nfe/NFeRecepcaoEvento',
            'NfeAutorizacao': 'https://homologacao.nfe.fazenda.pr.gov.br/nfe/NFeAutorizacao3',
            'NfeRetAutorizacao': 'https://homologacao.nfe.fazenda.pr.gov.br/nfe/NFeRetAutorizacao3'},
        'PE': {
            'NfeRecepcao2': 'https://nfehomolog.sefaz.pe.gov.br/nfe-service/services/NfeRecepcao2',
            'NfeRetRecepcao2': 'https://nfehomolog.sefaz.pe.gov.br/nfe-service/services/NfeRetRecepcao2',
            'NfeInutilizacao2': 'https://nfehomolog.sefaz.pe.gov.br/nfe-service/services/NfeInutilizacao2',
            'NfeConsulta2': 'https://nfehomolog.sefaz.pe.gov.br/nfe-service/services/NfeConsulta2',
            'NfeStatusServico2': 'https://nfehomolog.sefaz.pe.gov.br/nfe-service/services/NfeStatusServico2',
            'RecepcaoEvento': 'https://nfehomolog.sefaz.pe.gov.br/nfe-service/services/RecepcaoEvento',
            'NfeAutorizacao': 'https://nfehomolog.sefaz.pe.gov.br/nfe-service/services/NfeAutorizacao',
            'NfeRetAutorizacao': 'https://nfehomolog.sefaz.pe.gov.br/nfe-service/services/NfeRetAutorizacao'},
        'RS': {
            'NfeRecepcao2': 'https://homologacao.nfe.sefaz.rs.gov.br/ws/Nferecepcao/NFeRecepcao2.asmx',
            'NfeRetRecepcao2': 'https://homologacao.nfe.sefaz.rs.gov.br/ws/NfeRetRecepcao/NfeRetRecepcao2.asmx',
            'CadConsultaCadastro2': 'https://sef.sefaz.rs.gov.br/ws/cadconsultacadastro/cadconsultacadastro2.asmx',
            'NfeInutilizacao2': 'https://homologacao.nfe.sefaz.rs.gov.br/ws/nfeinutilizacao/nfeinutilizacao2.asmx',
            'NfeConsulta2': 'https://homologacao.nfe.sefaz.rs.gov.br/ws/NfeConsulta/NfeConsulta2.asmx',
            'NfeStatusServico2': 'https://homologacao.nfe.sefaz.rs.gov.br/ws/NfeStatusServico/NfeStatusServico2.asmx',
            'RecepcaoEvento': 'https://homologacao.nfe.sefaz.rs.gov.br/ws/recepcaoevento/recepcaoevento.asmx',
            'NfeConsultaDest': 'https://homologacao.nfe.sefaz.rs.gov.br/ws/nfeConsultaDest/nfeConsultaDest.asmx',
            'NfeDownloadNF': 'https://homologacao.nfe.sefaz.rs.gov.br/ws/nfeDownloadNF/nfeDownloadNF.asmx',
            'NfeAutorizacao': 'https://homologacao.nfe.sefaz.rs.gov.br/ws/NfeAutorizacao/NFeAutorizacao.asmx',
            'NfeRetAutorizacao': 'https://homologacao.nfe.sefaz.rs.gov.br/ws/NfeRetAutorizacao/NFeRetAutorizacao.asmx'},
        'SP': {
            'NfeRecepcao2': 'https://homologacao.nfe.fazenda.sp.gov.br/nfeweb/services/NfeRecepcao2.asmx',
            'NfeRetRecepcao2': 'https://homologacao.nfe.fazenda.sp.gov.br/nfeweb/services/NfeRetRecepcao2.asmx',
            'NfeInutilizacao2': 'https://homologacao.nfe.fazenda.sp.gov.br/nfeweb/services/nfeinutilizacao2.asmx',
            'NfeConsulta2': 'https://homologacao.nfe.fazenda.sp.gov.br/nfeweb/services/nfeconsulta2.asmx',
            'NfeStatusServico2': 'https://homologacao.nfe.fazenda.sp.gov.br/nfeweb/services/nfestatusservico2.asmx',
            'CadConsultaCadastro2': 'https://homologacao.nfe.fazenda.sp.gov.br/nfeweb/services/cadconsultacadastro2.asmx',
            'RecepcaoEvento': 'https://homologacao.nfe.fazenda.sp.gov.br/eventosWEB/services/RecepcaoEvento.asmx',
            'NfeAutorizacao': 'https://homologacao.nfe.fazenda.sp.gov.br/ws/nfeautorizacao.asmx',
            'NfeRetAutorizacao': 'https://homologacao.nfe.fazenda.sp.gov.br/ws/nferetautorizacao.asmx'},
        'SVAN': {
            'NfeRecepcao2': 'https://hom.sefazvirtual.fazenda.gov.br/NfeRecepcao2/NfeRecepcao2.asmx',
            'NfeRetRecepcao2': 'https://hom.sefazvirtual.fazenda.gov.br/NfeRetRecepcao2/NfeRetRecepcao2.asmx',
            'NfeInutilizacao2': 'https://hom.sefazvirtual.fazenda.gov.br/NfeInutilizacao2/NfeInutilizacao2.asmx',
            'NfeConsulta2': 'https://hom.sefazvirtual.fazenda.gov.br/NfeConsulta2/NfeConsulta2.asmx',
            'NfeStatusServico2': 'https://hom.sefazvirtual.fazenda.gov.br/NfeStatusServico2/NfeStatusServico2.asmx',
            'RecepcaoEvento': 'https://hom.sefazvirtual.fazenda.gov.br/RecepcaoEvento/RecepcaoEvento.asmx',
            'NfeDownloadNF': 'https://hom.sefazvirtual.fazenda.gov.br/NfeDownloadNF/NfeDownloadNF.asmx',
            'NfeAutorizacao': 'https://hom.sefazvirtual.fazenda.gov.br/NfeAutorizacao/NfeAutorizacao.asmx',
            'NfeRetAutorizacao': 'https://hom.sefazvirtual.fazenda.gov.br/NfeRetAutorizacao/NfeRetAutorizacao.asmx'},
        'SVRS': {
            'NfeRecepcao2': 'https://homologacao.nfe.sefazvirtual.rs.gov.br/ws/Nferecepcao/NFeRecepcao2.asmx',
            'NfeRetRecepcao2': 'https://homologacao.nfe.sefazvirtual.rs.gov.br/ws/NfeRetRecepcao/NfeRetRecepcao2.asmx',
            'CadConsultaCadastro2': 'https://sef.sefaz.rs.gov.br/ws/cadconsultacadastro/cadconsultacadastro2.asmx',
            'NfeInutilizacao2': 'https://homologacao.nfe.sefazvirtual.rs.gov.br/ws/nfeinutilizacao/nfeinutilizacao2.asmx',
            'NfeConsulta2': 'https://homologacao.nfe.sefazvirtual.rs.gov.br/ws/NfeConsulta/NfeConsulta2.asmx',
            'NfeStatusServico2': 'https://homologacao.nfe.sefazvirtual.rs.gov.br/ws/NfeStatusServico/NfeStatusServico2.asmx',
            'RecepcaoEvento': 'https://homologacao.nfe.sefazvirtual.rs.gov.br/ws/recepcaoevento/recepcaoevento.asmx',
            'NfeAutorizacao': 'https://homologacao.nfe.sefazvirtual.rs.gov.br/ws/NfeAutorizacao/NFeAutorizacao.asmx',
            'NfeRetAutorizacao': 'https://homologacao.nfe.sefazvirtual.rs.gov.br/ws/NfeRetAutorizacao/NFeRetAutorizacao.asmx'},
        'SCAN': {
            'NfeRecepcao2': 'https://hom.nfe.fazenda.gov.br/SCAN/NfeRecepcao2/NfeRecepcao2.asmx',
            'NfeRetRecepcao2': 'https://hom.nfe.fazenda.gov.br/SCAN/NfeRetRecepcao2/NfeRetRecepcao2.asmx',
            'NfeInutilizacao2': 'https://hom.nfe.fazenda.gov.br/SCAN/NfeInutilizacao2/NfeInutilizacao2.asmx',
            'NfeConsulta2': 'https://hom.nfe.fazenda.gov.br/SCAN/NfeConsulta2/NfeConsulta2.asmx',
            'NfeStatusServico2': 'https://hom.nfe.fazenda.gov.br/SCAN/NfeStatusServico2/NfeStatusServico2.asmx',
            'RecepcaoEvento': 'https://hom.nfe.fazenda.gov.br/SCAN/RecepcaoEvento/RecepcaoEvento.asmx',
            'NfeAutorizacao': 'https://hom.nfe.fazenda.gov.br/SCAN/NfeAutorizacao/NfeAutorizacao.asmx',
            'NfeRetAutorizacao': 'https://hom.nfe.fazenda.gov.br/SCAN/NfeRetAutorizacao/NfeRetAutorizacao.asmx'},
        'SVC-AN': {
            'NfeRecepcao2': 'https://hom.svc.fazenda.gov.br/NfeRecepcao2/NfeRecepcao2.asmx',
            'NfeRetRecepcao2': 'https://hom.svc.fazenda.gov.br/NfeRetRecepcao2/NfeRetRecepcao2.asmx',
            'NfeConsulta2': 'https://hom.svc.fazenda.gov.br/NfeConsulta2/NfeConsulta2.asmx',
            'NfeStatusServico2': 'https://hom.svc.fazenda.gov.br/NfeStatusServico2/NfeStatusServico2.asmx',
            'RecepcaoEvento': 'https://hom.svc.fazenda.gov.br/RecepcaoEvento/RecepcaoEvento.asmx',
            'NfeAutorizacao': 'https://hom.svc.fazenda.gov.br/NfeAutorizacao/NfeAutorizacao.asmx',
            'NfeRetAutorizacao': 'https://hom.svc.fazenda.gov.br/NfeRetAutorizacao/NfeRetAutorizacao.asmx'},
        'SVC-RS': {
            'NfeRecepcao2': 'https://homologacao.nfe.sefazvirtual.rs.gov.br/ws/Nferecepcao/NFeRecepcao2.asmx',
            'NfeRetRecepcao2': 'https://homologacao.nfe.sefazvirtual.rs.gov.br/ws/NfeRetRecepcao/NfeRetRecepcao2.asmx',
            'NfeConsulta2': 'https://homologacao.nfe.sefazvirtual.rs.gov.br/ws/NfeConsulta/NfeConsulta2.asmx',
            'NfeStatusServico2': 'https://homologacao.nfe.sefazvirtual.rs.gov.br/ws/NfeStatusServico/NfeStatusServico2.asmx',
            'RecepcaoEvento': 'https://homologacao.nfe.sefazvirtual.rs.gov.br/ws/recepcaoevento/recepcaoevento.asmx',
            'NfeAutorizacao': 'https://homologacao.nfe.sefazvirtual.rs.gov.br/ws/NfeAutorizacao/NFeAutorizacao.asmx',
            'CadConsultaCadastro2': 'https://svp-ws.sefazvirtual.rs.gov.br/ws/CadConsultaCadastro/CadConsultaCadastro2.asmx',
            'NfeRetAutorizacao': 'https://homologacao.nfe.sefazvirtual.rs.gov.br/ws/NfeRetAutorizacao/NFeRetAutorizacao.asmx'},
        'AN': {
            'RecepcaoEvento': 'https://hom.nfe.fazenda.gov.br/RecepcaoEvento/RecepcaoEvento.asmx',
            'NfeConsultaDest': 'https://hom.nfe.fazenda.gov.br/NFeConsultaDest/NFeConsultaDest.asmx',
            'NfeDownloadNF': 'https://hom.nfe.fazenda.gov.br/NfeDownloadNF/NfeDownloadNF.asmx'}
    },
    'producao': {
        'AM': {
            'NfeRecepcao2': 'https://nfe.sefaz.am.gov.br/services2/services/NfeRecepcao2',
            'NfeRetRecepcao2': 'https://nfe.sefaz.am.gov.br/services2/services/NfeRetRecepcao2',
            'NfeInutilizacao2': 'https://nfe.sefaz.am.gov.br/services2/services/NfeInutilizacao2',
            'NfeConsulta2': 'https://nfe.sefaz.am.gov.br/services2/services/NfeConsulta2',
            'NfeStatusServico2': 'https://nfe.sefaz.am.gov.br/services2/services/NfeStatusServico2',
            'CadConsultaCadastro2': 'https://nfe.sefaz.am.gov.br/services2/services/CadConsultaCadastro2',
            'RecepcaoEvento': 'https://nfe.sefaz.am.gov.br/services2/services/RecepcaoEvento',
            'NfeAutorizacao': 'https://nfe.sefaz.am.gov.br/services2/services/NfeAutorizacao',
            'NfeRetAutorizacao': 'https://nfe.sefaz.am.gov.br/services2/services/NfeRetAutorizacao'},
        'BA': {
            'NfeRecepcao2': 'https://nfe.sefaz.ba.gov.br/webservices/nfenw/NfeRecepcao2.asmx',
            'NfeRetRecepcao2': 'https://nfe.sefaz.ba.gov.br/webservices/nfenw/NfeRetRecepcao2.asmx',
            'NfeInutilizacao2': 'https://nfe.sefaz.ba.gov.br/webservices/nfenw/nfeinutilizacao2.asmx',
            'NfeConsulta2': 'https://nfe.sefaz.ba.gov.br/webservices/nfenw/nfeconsulta2.asmx',
            'NfeStatusServico2': 'https://nfe.sefaz.ba.gov.br/webservices/nfenw/NfeStatusServico2.asmx',
            'CadConsultaCadastro2': 'https://nfe.sefaz.ba.gov.br/webservices/nfenw/CadConsultaCadastro2.asmx',
            'RecepcaoEvento': 'https://nfe.sefaz.ba.gov.br/webservices/sre/recepcaoevento.asmx',
            'NfeStatusServico': 'https://nfe.sefaz.ba.gov.br/webservices/NfeStatusServico/NfeStatusServico.asmx',
            'NfeAutorizacao': 'https://nfe.sefaz.ba.gov.br/webservices/NfeAutorizacao/NfeAutorizacao.asmx',
            'NfeRetAutorizacao': 'https://nfe.sefaz.ba.gov.br/webservices/NfeRetAutorizacao/NfeRetAutorizacao.asmx'},
        'CE': {
            'NfeRecepcao2': 'https://nfe.sefaz.ce.gov.br/nfe2/services/NfeRecepcao2',
            'NfeRetRecepcao2': 'https://nfe.sefaz.ce.gov.br/nfe2/services/NfeRetRecepcao2',
            'NfeInutilizacao2': 'https://nfe.sefaz.ce.gov.br/nfe2/services/NfeInutilizacao2',
            'NfeConsulta2': 'https://nfe.sefaz.ce.gov.br/nfe2/services/NfeConsulta2',
            'NfeStatusServico2': 'https://nfe.sefaz.ce.gov.br/nfe2/services/NfeStatusServico2',
            'CadConsultaCadastro2': 'https://nfe.sefaz.ce.gov.br/nfe2/services/CadConsultaCadastro2',
            'RecepcaoEvento': 'https://nfe.sefaz.ce.gov.br/nfe2/services/RecepcaoEvento'},
        'ES': {
            'CadConsultaCadastro2': 'https://app.sefaz.es.gov.br/ConsultaCadastroService/CadConsultaCadastro2.asmx'},
        'GO': {
            'NfeRecepcao2': 'https://nfe.sefaz.go.gov.br/nfe/services/v2/NfeRecepcao2',
            'NfeRetRecepcao2': 'https://nfe.sefaz.go.gov.br/nfe/services/v2/NfeRetRecepcao2',
            'NfeInutilizacao2': 'https://nfe.sefaz.go.gov.br/nfe/services/v2/NfeInutilizacao2',
            'NfeConsulta2': 'https://nfe.sefaz.go.gov.br/nfe/services/v2/NfeConsulta2',
            'NfeStatusServico2': 'https://nfe.sefaz.go.gov.br/nfe/services/v2/NfeStatusServico2',
            'CadConsultaCadastro2': 'https://nfe.sefaz.go.gov.br/nfe/services/v2/CadConsultaCadastro2',
            'RecepcaoEvento': 'https://nfe.sefaz.go.gov.br/nfe/services/v2/RecepcaoEvento',
            'NfeAutorizacao': 'https://nfe.sefaz.go.gov.br/nfe/services/v2/NfeAutorizacao',
            'NfeRetAutorizacao': 'https://nfe.sefaz.go.gov.br/nfe/services/v2/NfeRetAutorizacao'},
        'MG': {
            'NfeRecepcao2': 'https://nfe.fazenda.mg.gov.br/nfe2/services/NfeRecepcao2',
            'NfeRetRecepcao2': 'https://nfe.fazenda.mg.gov.br/nfe2/services/NfeRetRecepcao2',
            'NfeInutilizacao2': 'https://nfe.fazenda.mg.gov.br/nfe2/services/NfeInutilizacao2',
            'NfeConsulta2': 'https://nfe.fazenda.mg.gov.br/nfe2/services/NfeConsulta2',
            'NfeStatus2': 'https://nfe.fazenda.mg.gov.br/nfe2/services/NfeStatus2',
            'CadConsultaCadastro2': 'https://nfe.fazenda.mg.gov.br/nfe2/services/cadconsultacadastro2',
            'RecepcaoEvento': 'https://nfe.fazenda.mg.gov.br/nfe2/services/RecepcaoEvento',
            'NfeAutorizacao': 'https://nfe.fazenda.mg.gov.br/nfe2/services/NfeAutorizacao',
            'NfeRetAutorizacao': 'https://nfe.fazenda.mg.gov.br/nfe2/services/NfeRetAutorizacao'},
        'MS': {
            'NfeRecepcao2': 'https://nfe.fazenda.ms.gov.br/producao/services2/NfeRecepcao2',
            'NfeRetRecepcao2': 'https://nfe.fazenda.ms.gov.br/producao/services2/NfeRetRecepcao2',
            'NfeInutilizacao2': 'https://nfe.fazenda.ms.gov.br/producao/services2/NfeInutilizacao2',
            'NfeConsulta2': 'https://nfe.fazenda.ms.gov.br/producao/services2/NfeConsulta2',
            'NfeStatusServico2': 'https://nfe.fazenda.ms.gov.br/producao/services2/NfeStatusServico2',
            'CadConsultaCadastro2': 'https://nfe.fazenda.ms.gov.br/producao/services2/CadConsultaCadastro2',
            'RecepcaoEvento': 'https://nfe.fazenda.ms.gov.br/producao/services2/RecepcaoEvento',
            'NfeAutorizacao': 'https://nfe.fazenda.ms.gov.br/producao/services2/NfeAutorizacao',
            'NfeRetAutorizacao': 'https://nfe.fazenda.ms.gov.br/producao/services2/NfeRetAutorizacao'},
        'MT': {
            'NfeRecepcao2': 'https://nfe.sefaz.mt.gov.br/nfews/v2/services/NfeRecepcao2',
            'NfeRetRecepcao2': 'https://nfe.sefaz.mt.gov.br/nfews/v2/services/NfeRetRecepcao2',
            'NfeInutilizacao2': 'https://nfe.sefaz.mt.gov.br/nfews/v2/services/NfeInutilizacao2',
            'NfeConsulta2': 'https://nfe.sefaz.mt.gov.br/nfews/v2/services/NfeConsulta2',
            'NfeStatusServico2': 'https://nfe.sefaz.mt.gov.br/nfews/v2/services/NfeStatusServico2',
            'CadConsultaCadastro2': 'https://nfe.sefaz.mt.gov.br/nfews/v2/services/CadConsultaCadastro2',
            'RecepcaoEvento': 'https://nfe.sefaz.mt.gov.br/nfews/v2/services/RecepcaoEvento',
            'NfeAutorizacao': 'https://nfe.sefaz.mt.gov.br/nfews/v2/services/NfeAutorizacao',
            'NfeRetAutorizacao': 'https://nfe.sefaz.mt.gov.br/nfews/v2/services/NfeRetAutorizacao'},
        'PE': {
            'NfeRecepcao2': 'https://nfe.sefaz.pe.gov.br/nfe-service/services/NfeRecepcao2',
            'NfeRetRecepcao2': 'https://nfe.sefaz.pe.gov.br/nfe-service/services/NfeRetRecepcao2',
            'NfeInutilizacao2': 'https://nfe.sefaz.pe.gov.br/nfe-service/services/NfeInutilizacao2',
            'NfeConsulta2': 'https://nfe.sefaz.pe.gov.br/nfe-service/services/NfeConsulta2',
            'NfeStatusServico2': 'https://nfe.sefaz.pe.gov.br/nfe-service/services/NfeStatusServico2',
            'CadConsultaCadastro2': 'https://nfe.sefaz.pe.gov.br/nfe-service/services/CadConsultaCadastro2',
            'RecepcaoEvento': 'https://nfe.sefaz.pe.gov.br/nfe-service/services/RecepcaoEvento',
            'NfeAutorizacao': 'https://nfe.sefaz.pe.gov.br/nfe-service/services/NfeAutorizacao',
            'NfeRetAutorizacao': 'https://nfe.sefaz.pe.gov.br/nfe-service/services/NfeRetAutorizacao'},
        'PR': {
            'NfeRecepcao2': 'https://nfe2.fazenda.pr.gov.br/nfe/NFeRecepcao2',
            'NfeRetRecepcao2': 'https://nfe2.fazenda.pr.gov.br/nfe/NFeRetRecepcao2',
            'NfeInutilizacao2': 'https://nfe2.fazenda.pr.gov.br/nfe/NFeInutilizacao2',
            'NfeConsulta2': 'https://nfe2.fazenda.pr.gov.br/nfe/NFeConsulta2',
            'NfeStatusServico2': 'https://nfe2.fazenda.pr.gov.br/nfe/NFeStatusServico2',
            'CadConsultaCadastro2': 'https://nfe2.fazenda.pr.gov.br/nfe/CadConsultaCadastro2',
            'RecepcaoEvento': 'https://nfe2.fazenda.pr.gov.br/nfe-evento/NFeRecepcaoEvento'},
        'RS': {
            'NfeRecepcao2': 'https://nfe.sefaz.rs.gov.br/ws/Nferecepcao/NFeRecepcao2.asmx',
            'NfeRetRecepcao2': 'https://nfe.sefaz.rs.gov.br/ws/NfeRetRecepcao/NfeRetRecepcao2.asmx',
            'NfeInutilizacao2': 'https://nfe.sefaz.rs.gov.br/ws/NfeInutilizacao/NfeInutilizacao2.asmx',
            'NfeConsulta2': 'https://nfe.sefaz.rs.gov.br/ws/NfeConsulta/NfeConsulta2.asmx',
            'NfeStatusServico2': 'https://nfe.sefaz.rs.gov.br/ws/NfeStatusServico/NfeStatusServico2.asmx',
            'CadConsultaCadastro2': 'https://sef.sefaz.rs.gov.br/ws/cadconsultacadastro/cadconsultacadastro2.asmx',
            'RecepcaoEvento': 'https://nfe.sefaz.rs.gov.br/ws/recepcaoevento/recepcaoevento.asmx',
            'NfeConsultaDest': 'https://nfe.sefaz.rs.gov.br/ws/nfeConsultaDest/nfeConsultaDest.asmx',
            'NfeDownloadNF': 'https://nfe.sefaz.rs.gov.br/ws/nfeDownloadNF/nfeDownloadNF.asmx',
            'NFeAutorizacao': 'https://nfe.sefaz.rs.gov.br/ws/NfeAutorizacao/NFeAutorizacao.asmx',
            'NFeRetAutorizacao': 'https://nfe.sefaz.rs.gov.br/ws/NfeRetAutorizacao/NFeRetAutorizacao.asmx'},
        'SP': {
            'NfeRecepcao2': 'https://nfe.fazenda.sp.gov.br/nfeweb/services/nferecepcao2.asmx',
            'NfeRetRecepcao2': 'https://nfe.fazenda.sp.gov.br/nfeweb/services/nferetrecepcao2.asmx',
            'NfeInutilizacao2': 'https://nfe.fazenda.sp.gov.br/nfeweb/services/nfeinutilizacao2.asmx',
            'NfeConsulta2': 'https://nfe.fazenda.sp.gov.br/nfeweb/services/nfeconsulta2.asmx',
            'NfeStatusServico2': 'https://nfe.fazenda.sp.gov.br/nfeweb/services/nfestatusservico2.asmx',
            'CadConsultaCadastro2': 'https://nfe.fazenda.sp.gov.br/nfeweb/services/cadconsultacadastro2.asmx',
            'RecepcaoEvento': 'https://nfe.fazenda.sp.gov.br/eventosWEB/services/RecepcaoEvento.asmx',
            'NfeAutorizacao': 'https://nfe.fazenda.sp.gov.br/ws/nfeautorizacao.asmx',
            'NfeRetAutorizacao': 'https://nfe.fazenda.sp.gov.br/ws/nferetautorizacao.asmx'},
        'SVAN': {
            'NfeRecepcao2': 'https://www.sefazvirtual.fazenda.gov.br/NfeRecepcao2/NfeRecepcao2.asmx',
            'NfeRetRecepcao2': 'https://www.sefazvirtual.fazenda.gov.br/NfeRetRecepcao2/NfeRetRecepcao2.asmx',
            'NfeInutilizacao2': 'https://www.sefazvirtual.fazenda.gov.br/NfeInutilizacao2/NfeInutilizacao2.asmx',
            'NfeConsulta2': 'https://www.sefazvirtual.fazenda.gov.br/NfeConsulta2/NfeConsulta2.asmx',
            'NfeStatusServico2': 'https://www.sefazvirtual.fazenda.gov.br/NfeStatusServico2/NfeStatusServico2.asmx',
            'RecepcaoEvento': 'https://www.sefazvirtual.fazenda.gov.br/RecepcaoEvento/RecepcaoEvento.asmx',
            'NfeDownloadNF': 'https://www.sefazvirtual.fazenda.gov.br/NfeDownloadNF/NfeDownloadNF.asmx',
            'NfeAutorizacao': 'https://www.sefazvirtual.fazenda.gov.br/NfeAutorizacao/NfeAutorizacao.asmx',
            'NfeRetAutorizacao': 'https://www.sefazvirtual.fazenda.gov.br/NfeRetAutorizacao/NfeRetAutorizacao.asmx'},
        'SVRS': {
            'NfeRecepcao2': 'https://nfe.sefazvirtual.rs.gov.br/ws/Nferecepcao/NFeRecepcao2.asmx',
            'NfeRetRecepcao2': 'https://nfe.sefazvirtual.rs.gov.br/ws/NfeRetRecepcao/NfeRetRecepcao2.asmx',
            'NfeInutilizacao2': 'https://nfe.sefazvirtual.rs.gov.br/ws/nfeinutilizacao/nfeinutilizacao2.asmx',
            'NfeConsulta2': 'https://nfe.sefazvirtual.rs.gov.br/ws/NfeConsulta/NfeConsulta2.asmx',
            'NfeStatusServico2': 'https://nfe.sefazvirtual.rs.gov.br/ws/NfeStatusServico/NfeStatusServico2.asmx',
            'RecepcaoEvento': 'https://nfe.sefazvirtual.rs.gov.br/ws/recepcaoevento/recepcaoevento.asmx',
            'NfeAutorizacao': 'https://nfe.sefazvirtual.rs.gov.br/ws/NfeAutorizacao/NFeAutorizacao.asmx',
            'CadConsultaCadastro2': 'https://svp-ws.sefazvirtual.rs.gov.br/ws/CadConsultaCadastro/CadConsultaCadastro2.asmx',
            'NFeRetAutorizacao': 'https://nfe.sefazvirtual.rs.gov.br/ws/NfeRetAutorizacao/NFeRetAutorizacao.asmx'},
        'SCAN': {
            'NfeRecepcao2': 'https://www.scan.fazenda.gov.br/NfeRecepcao2/NfeRecepcao2.asmx',
            'NfeRetRecepcao2': 'https://www.scan.fazenda.gov.br/NfeRetRecepcao2/NfeRetRecepcao2.asmx',
            'NfeInutilizacao2': 'https://www.scan.fazenda.gov.br/NfeInutilizacao2/NfeInutilizacao2.asmx',
            'NfeConsulta2': 'https://www.scan.fazenda.gov.br/NfeConsulta2/NfeConsulta2.asmx',
            'NfeStatusServico2': 'https://www.scan.fazenda.gov.br/NfeStatusServico2/NfeStatusServico2.asmx',
            'RecepcaoEvento': 'https://www.scan.fazenda.gov.br/RecepcaoEvento/RecepcaoEvento.asmx',
            'NfeAutorizacao': 'https://www.scan.fazenda.gov.br/NfeAutorizacao/NfeAutorizacao.asmx',
            'NfeRetAutorizacao': 'https://www.scan.fazenda.gov.br/NfeRetAutorizacao/NfeRetAutorizacao.asmx'},
        'SVC-AN': {
            'RecepcaoEvento': 'https://www.svc.fazenda.gov.br/RecepcaoEvento/RecepcaoEvento.asmx',
            'NfeRecepcao2': 'https://www.svc.fazenda.gov.br/NfeRecepcao2/NfeRecepcao2.asmx',
            'NfeRetRecepcao2': 'https://www.svc.fazenda.gov.br/NfeRetRecepcao2/NfeRetRecepcao2.asmx',
            'NfeConsulta2': 'https://www.svc.fazenda.gov.br/NfeConsulta2/NfeConsulta2.asmx',
            'NfeStatusServico2': 'https://www.svc.fazenda.gov.br/NfeStatusServico2/NfeStatusServico2.asmx',
            'NfeAutorizacao': 'https://www.svc.fazenda.gov.br/NfeAutorizacao/NfeAutorizacao.asmx',
            'NfeRetAutorizacao': 'https://www.svc.fazenda.gov.br/NfeRetAutorizacao/NfeRetAutorizacao.asmx'},
        'SVC-RS': {
            'RecepcaoEvento': 'https://nfe.sefazvirtual.rs.gov.br/ws/recepcaoevento/recepcaoevento.asmx',
            'NfeRecepcao2': 'https://nfe.sefazvirtual.rs.gov.br/ws/Nferecepcao/NFeRecepcao2.asmx',
            'NfeRetRecepcao2': 'https://nfe.sefazvirtual.rs.gov.br/ws/NfeRetRecepcao/NfeRetRecepcao2.asmx',
            'NfeConsulta2': 'https://nfe.sefazvirtual.rs.gov.br/ws/NfeConsulta/NfeConsulta2.asmx',
            'NfeStatusServico2': 'https://nfe.sefazvirtual.rs.gov.br/ws/NfeStatusServico/NfeStatusServico2.asmx',
            'CadConsultaCadastro2': 'https://sef.sefaz.rs.gov.br/ws/cadconsultacadastro/cadconsultacadastro2.asmx',
            'NfeAutorizacao': 'https://nfe.sefazvirtual.rs.gov.br/ws/NfeAutorizacao/NFeAutorizacao.asmx',
            'NfeRetAutorizacao': 'https://nfe.sefazvirtual.rs.gov.br/ws/NfeRetAutorizacao/NFeRetAutorizacao.asmx'},
        'AN': {
            'RecepcaoEvento': 'https://www.nfe.fazenda.gov.br/RecepcaoEvento/RecepcaoEvento.asmx',
            'NfeConsultaDest': 'https://www.nfe.fazenda.gov.br/NFeConsultaDest/NFeConsultaDest.asmx',
            'NfeDownloadNF': 'https://www.nfe.fazenda.gov.br/NfeDownloadNF/NfeDownloadNF.asmx'}
    }
}

cnpj = raw_input('CNPJ: ')
home = os.getenv('HOME')
key_file  = '%s/NFe/cnpjs/%s/certificado_digital/chave.pem' % (home, cnpj)
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
            self.sock = sock
            self._tunnel()
        self.sock = ssl.wrap_socket(sock, self.key_file, self.cert_file, ssl_version=ssl.PROTOCOL_SSLv3)

def criar_diretorios(sefaz, mostra_erro = False):
    for ambiente in ('producao', 'homologacao'):
        try:
            os.makedirs('%s/%s' % (sefaz, ambiente))
        except os.error as erro:
            if mostra_erro:
                print erro

for ambiente, wss in wsdls.items():
    print ambiente
    for sefaz, servicos in wss.items():
        print ' ', sefaz
        criar_diretorios(sefaz)
        for servico, url in servicos.items():
            servico += '.wsdl'
            servidor, uri = url[8:].split('/', 1)
            uri = '/' + uri + '?wsdl'
            print '   ', servico
            print '     ', servidor
            print '       ', uri
            try:
                  conexao = HTTPSConnection(servidor, 443, key_file, cert_file)
                  conexao.request('GET', uri)
                  cab_xml = "<?xml version='1.0' encoding='UTF-8'?>"
                  wsdl = conexao.getresponse().read()
                  if wsdl[:6] != cab_xml[:6]:
                      wsdl = cab_xml + wsdl
                  open('%s/%s/%s' % (sefaz, ambiente, servico), 'wb').write(wsdl)
                  conexao.close()
            except:
                  print sys.exc_info()
