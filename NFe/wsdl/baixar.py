#!/usr/bin/env python
# -*- coding: utf-8 -*-

import httplib
import os
import ssl
import socket

# Estados que utilizam a SVAN - Sefaz Virtual do Ambiente Nacional: ES, MA, PA, PI
# Estados que utilizam a SVRS - Sefaz Virtual do RS: AC, AL, AM, AP, DF, MS, PB, RJ, RN, RO, RR, SC, SE, TO 

wsdls = {
    'homologacao':{
        'AM': {
            'NfeRecepcao2': 'https://homnfe.sefaz.am.gov.br/services2/services/NfeRecepcao2',
            'NfeRetRecepcao2': 'https://homnfe.sefaz.am.gov.br/services2/services/NfeRetRecepcao2',
            'NfeInutilizacao2': 'https://homnfe.sefaz.am.gov.br/services2/services/NfeInutilizacao2',
            'NfeConsulta2': 'https://homnfe.sefaz.am.gov.br/services2/services/NfeConsulta2',
            'NfeStatusServico2': 'https://homnfe.sefaz.am.gov.br/services2/services/NfeStatusServico2',
            'CadConsultaCadastro2': 'https://homnfe.sefaz.am.gov.br/services2/services/CadConsultaCadastro2',
            'RecepcaoEvento': 'https://homnfe.sefaz.am.gov.br/services2/services/RecepcaoEvento'},
        'BA': {
            'NfeRecepcao2': 'https://hnfe.sefaz.ba.gov.br/webservices/nfenw/NfeRecepcao2.asmx',
            'NfeRetRecepcao2': 'https://hnfe.sefaz.ba.gov.br/webservices/nfenw/NfeRetRecepcao2.asmx',
            'NfeInutilizacao2': 'https://hnfe.sefaz.ba.gov.br/webservices/nfenw/NfeInutilizacao2.asmx',
            'NfeConsulta2': 'https://hnfe.sefaz.ba.gov.br/webservices/nfenw/NfeConsulta2.asmx',
            'NfeStatusServico2': 'https://hnfe.sefaz.ba.gov.br/webservices/nfenw/NfeStatusServico2.asmx',
            'CadConsultaCadastro2': 'https://hnfe.sefaz.ba.gov.br/webservices/nfenw/CadConsultaCadastro2.asmx',
            'RecepcaoEvento': 'https://hnfe.sefaz.ba.gov.br/webservices/sre/RecepcaoEvento.asmx'},
        'CE': {
            'NfeRecepcao2': 'https://nfeh.sefaz.ce.gov.br/nfe2/services/NfeRecepcao2',
            'NfeRetRecepcao2': 'https://nfeh.sefaz.ce.gov.br/nfe2/services/NfeRetRecepcao2',
            'NfeInutilizacao2': 'https://nfeh.sefaz.ce.gov.br/nfe2/services/NfeInutilizacao2',
            'NfeConsulta2': 'https://nfeh.sefaz.ce.gov.br/nfe2/services/NfeConsulta2',
            'NfeStatusServico2': 'https://nfeh.sefaz.ce.gov.br/nfe2/services/NfeStatusServico2',
            'CadConsultaCadastro2': 'https://nfeh.sefaz.ce.gov.br/nfe2/services/CadConsultaCadastro2',
            'RecepcaoEvento': 'https://nfeh.sefaz.ce.gov.br/nfe2/services/RecepcaoEvento'},
        'GO': {
            'NfeRecepcao2': 'https://homolog.sefaz.go.gov.br/nfe/services/v2/NfeRecepcao2',
            'NfeRetRecepcao2': 'https://homolog.sefaz.go.gov.br/nfe/services/v2/NfeRetRecepcao2',
            'NfeInutilizacao2': 'https://homolog.sefaz.go.gov.br/nfe/services/v2/NfeInutilizacao2',
            'NfeConsulta2': 'https://homolog.sefaz.go.gov.br/nfe/services/v2/NfeConsulta2',
            'NfeStatusServico2': 'https://homolog.sefaz.go.gov.br/nfe/services/v2/NfeStatusServico2',
            'CadConsultaCadastro2': 'https://homolog.sefaz.go.gov.br/nfe/services/v2/CadConsultaCadastro2',
            'NfeRecepcaoEvento': 'https://homolog.sefaz.go.gov.br/nfe/services/v2/NfeRecepcaoEvento'},
        'MT': {
            'NfeRecepcao2': 'https://homologacao.sefaz.mt.gov.br/nfews/v2/services/NfeRecepcao2',
            'NfeRetRecepcao2': 'https://homologacao.sefaz.mt.gov.br/nfews/v2/services/NfeRetRecepcao2',
            'NfeInutilizacao2': 'https://homologacao.sefaz.mt.gov.br/nfews/v2/services/NfeInutilizacao2',
            'NfeConsulta2': 'https://homologacao.sefaz.mt.gov.br/nfews/v2/services/NfeConsulta2',
            'NfeStatusServico2': 'https://homologacao.sefaz.mt.gov.br/nfews/v2/services/NfeStatusServico2',
            'RecepcaoEvento': 'https://homologacao.sefaz.mt.gov.br/nfews/v2/services/RecepcaoEvento'},
        'MS': {
            'NfeRecepcao2': 'https://homologacao.nfe.ms.gov.br/homologacao/services2/NfeRecepcao2',
            'NfeRetRecepcao2': 'https://homologacao.nfe.ms.gov.br/homologacao/services2/NfeRetRecepcao2',
            'NfeInutilizacao2': 'https://homologacao.nfe.ms.gov.br/homologacao/services2/NfeInutilizacao2',
            'NfeConsulta2': 'https://homologacao.nfe.ms.gov.br/homologacao/services2/NfeConsulta2',
            'NfeStatusServico2': 'https://homologacao.nfe.ms.gov.br/homologacao/services2/NfeStatusServico2',
            'CadConsultaCadastro2': 'https://homologacao.nfe.ms.gov.br/homologacao/services2/CadConsultaCadastro2',
            'RecepcaoEvento': 'https://homologacao.nfe.ms.gov.br/homologacao/services2/RecepcaoEvento'},
        'MG': {
            'NfeRecepcao2': 'https://hnfe.fazenda.mg.gov.br/nfe2/services/NfeRecepcao2',
            'NfeRetRecepcao2': 'https://hnfe.fazenda.mg.gov.br/nfe2/services/NfeRetRecepcao2',
            'NfeInutilizacao2': 'https://hnfe.fazenda.mg.gov.br/nfe2/services/NfeInutilizacao2',
            'NfeConsulta2': 'https://hnfe.fazenda.mg.gov.br/nfe2/services/NfeConsulta2',
            'NfeStatusServico2': 'https://hnfe.fazenda.mg.gov.br/nfe2/services/NfeStatusServico2',
            'CadConsultaCadastro2': 'https://hnfe.fazenda.mg.gov.br/nfe2/services/cadconsultacadastro2',
            'RecepcaoEvento': 'https://hnfe.fazenda.mg.gov.br/nfe2/services/RecepcaoEvento'},
        'PR': {
            'NfeRecepcao2': 'https://homologacao.nfe2.fazenda.pr.gov.br/nfe/NFeRecepcao2',
            'NfeRetRecepcao2': 'https://homologacao.nfe2.fazenda.pr.gov.br/nfe/NFeRetRecepcao2',
            'NfeInutilizacao2': 'https://homologacao.nfe2.fazenda.pr.gov.br/nfe/NFeInutilizacao2',
            'NfeConsulta2': 'https://homologacao.nfe2.fazenda.pr.gov.br/nfe/NFeConsulta2',
            'NfeStatusServico2': 'https://homologacao.nfe2.fazenda.pr.gov.br/nfe/NFeStatusServico2',
            'CadConsultaCadastro2': 'https://homologacao.nfe2.fazenda.pr.gov.br/nfe/CadConsultaCadastro2',
            'RecepcaoEvento': 'https://homologacao.nfe2.fazenda.pr.gov.br/nfe-evento/NFeRecepcaoEvento'},
        'PE': {
            'NfeRecepcao2': 'https://nfehomolog.sefaz.pe.gov.br/nfe-service/services/NfeRecepcao2',
            'NfeRetRecepcao2': 'https://nfehomolog.sefaz.pe.gov.br/nfe-service/services/NfeRetRecepcao2',
            'NfeInutilizacao2': 'https://nfehomolog.sefaz.pe.gov.br/nfe-service/services/NfeInutilizacao2',
            'NfeConsulta2': 'https://nfehomolog.sefaz.pe.gov.br/nfe-service/services/NfeConsulta2',
            'NfeStatusServico2': 'https://nfehomolog.sefaz.pe.gov.br/nfe-service/services/NfeStatusServico2',
            'RecepcaoEvento': 'https://nfehomolog.sefaz.pe.gov.br/nfe-service/services/RecepcaoEvento'},
        'RN': {
            'CadConsultaCadastro2': 'https://webservice.set.rn.gov.br/projetonfehomolog/set_nfe/servicos/CadConsultaCadastroWS.asmx'},
        'RS': {
            'NfeRecepcao2': 'https://homologacao.nfe.sefaz.rs.gov.br/ws/Nferecepcao/NFeRecepcao2.asmx',
            'NfeRetRecepcao2': 'https://homologacao.nfe.sefaz.rs.gov.br/ws/NfeRetRecepcao/NfeRetRecepcao2.asmx',
            'NfeInutilizacao2': 'https://homologacao.nfe.sefaz.rs.gov.br/ws/nfeinutilizacao/nfeinutilizacao2.asmx',
            'NfeConsulta2': 'https://homologacao.nfe.sefaz.rs.gov.br/ws/NfeConsulta/NfeConsulta2.asmx',
            'NfeStatusServico2': 'https://homologacao.nfe.sefaz.rs.gov.br/ws/NfeStatusServico/NfeStatusServico2.asmx',
            'RecepcaoEvento': 'https://homologacao.nfe.sefaz.rs.gov.br/ws/recepcaoevento/recepcaoevento.asmx',
            'NfeConsultaDest': 'https://homologacao.nfe.sefaz.rs.gov.br/ws/nfeConsultaDest/nfeConsultaDest.asmx',
            'NfeDownloadNF': 'https://homologacao.nfe.sefaz.rs.gov.br/ws/nfeDownloadNF/nfeDownloadNF.asmx'},
        'SP': {
            'NfeRecepcao2': 'https://homologacao.nfe.fazenda.sp.gov.br/nfeweb/services/NfeRecepcao2.asmx',
            'NfeRetRecepcao2': 'https://homologacao.nfe.fazenda.sp.gov.br/nfeweb/services/NfeRetRecepcao2.asmx',
            'NfeInutilizacao2': 'https://homologacao.nfe.fazenda.sp.gov.br/nfeweb/services/NfeInutilizacao2.asmx',
            'NfeConsulta2': 'https://homologacao.nfe.fazenda.sp.gov.br/nfeweb/services/NfeConsulta2.asmx',
            'NfeStatusServico2': 'https://homologacao.nfe.fazenda.sp.gov.br/nfeweb/services/NfeStatusServico2.asmx',
            'CadConsultaCadastro2': 'https://homologacao.nfe.fazenda.sp.gov.br/nfeweb/services/CadConsultaCadastro2.asmx',
            'RecepcaoEvento': 'https://homologacao.nfe.fazenda.sp.gov.br/eventosWEB/services/RecepcaoEvento.asmx'},
        'SVAN': {
            'NfeRecepcao2': 'https://hom.sefazvirtual.fazenda.gov.br/NfeRecepcao2/NfeRecepcao2.asmx',
            'NfeRetRecepcao2': 'https://hom.sefazvirtual.fazenda.gov.br/NfeRetRecepcao2/NfeRetRecepcao2.asmx',
            'NfeInutilizacao2': 'https://hom.sefazvirtual.fazenda.gov.br/NfeInutilizacao2/NfeInutilizacao2.asmx',
            'NfeConsulta2': 'https://hom.sefazvirtual.fazenda.gov.br/NfeConsulta2/NfeConsulta2.asmx',
            'NfeStatusServico2': 'https://hom.sefazvirtual.fazenda.gov.br/NfeStatusServico2/NfeStatusServico2.asmx',
            'RecepcaoEvento': 'https://hom.sefazvirtual.fazenda.gov.br/RecepcaoEvento/RecepcaoEvento.asmx',
            'NfeDownloadNF': 'https://hom.sefazvirtual.fazenda.gov.br/NfeDownloadNF/NfeDownloadNF.asmx'},
        'SVRS': {
            'NfeRecepcao2': 'https://homologacao.nfe.sefazvirtual.rs.gov.br/ws/Nferecepcao/NFeRecepcao2.asmx',
            'NfeRetRecepcao2': 'https://homologacao.nfe.sefazvirtual.rs.gov.br/ws/NfeRetRecepcao/NfeRetRecepcao2.asmx',
            'NfeInutilizacao2': 'https://homologacao.nfe.sefazvirtual.rs.gov.br/ws/nfeinutilizacao/nfeinutilizacao2.asmx',
            'NfeConsulta2': 'https://homologacao.nfe.sefazvirtual.rs.gov.br/ws/NfeConsulta/NfeConsulta2.asmx',
            'NfeStatusServico2': 'https://homologacao.nfe.sefazvirtual.rs.gov.br/ws/NfeStatusServico/NfeStatusServico2.asmx',
            'RecepcaoEvento': 'https://homologacao.nfe.sefazvirtual.rs.gov.br/ws/recepcaoevento/recepcaoevento.asmx'},
        'SCAN': {
            'NfeRecepcao2': 'https://hom.nfe.fazenda.gov.br/SCAN/NfeRecepcao2/NfeRecepcao2.asmx',
            'NfeRetRecepcao2': 'https://hom.nfe.fazenda.gov.br/SCAN/NfeRetRecepcao2/NfeRetRecepcao2.asmx',
            'NfeInutilizacao2': 'https://hom.nfe.fazenda.gov.br/SCAN/NfeInutilizacao2/NfeInutilizacao2.asmx',
            'NfeConsulta2': 'https://hom.nfe.fazenda.gov.br/SCAN/NfeConsulta2/NfeConsulta2.asmx',
            'NfeStatusServico2': 'https://hom.nfe.fazenda.gov.br/SCAN/NfeStatusServico2/NfeStatusServico2.asmx',
            'RecepcaoEvento': 'https://hom.nfe.fazenda.gov.br/SCAN/RecepcaoEvento/RecepcaoEvento.asmx'},
        'SVC': {
            'NfeRecepcao2': 'https://hom.svc.fazenda.gov.br/NfeRecepcao2/NfeRecepcao2.asmx',
            'NfeRetRecepcao2': 'https://hom.svc.fazenda.gov.br/NfeRetRecepcao2/NfeRetRecepcao2.asmx',
            'NfeInutilizacao2': 'https://hom.svc.fazenda.gov.br/NfeInutilizacao2/NfeInutilizacao2.asmx',
            'NfeConsulta2': 'https://hom.svc.fazenda.gov.br/NfeConsulta2/NfeConsulta2.asmx',
            'NfeStatusServico2': 'https://hom.svc.fazenda.gov.br/NFeStatusServico2/NFeStatusServico2.asmx',
            'RecepcaoEvento': 'https://hom.svc.fazenda.gov.br/RecepcaoEvento/RecepcaoEvento.asmx'},
        'AN': {
            'RecepcaoEvento': 'https://hom.nfe.fazenda.gov.br/RecepcaoEvento/RecepcaoEvento.asmx',
            'NfeConsultaDest': 'https://hom.nfe.fazenda.gov.br/NFeConsultaDest/NFeConsultaDest.asmx',
            'NfeDownloadNF': 'https://hom.nfe.fazenda.gov.br/NfeDownloadNF/NfeDownloadNF.asmx'},
    },
    'producao': {
        'AM': {
            'NfeRecepcao2': 'https://nfe.sefaz.am.gov.br/services2/services/NfeRecepcao2',
            'NfeRetRecepcao2': 'https://nfe.sefaz.am.gov.br/services2/services/NfeRetRecepcao2',
            'NfeInutilizacao2': 'https://nfe.sefaz.am.gov.br/services2/services/NfeInutilizacao2',
            'NfeConsulta2': 'https://nfe.sefaz.am.gov.br/services2/services/NfeConsulta2',
            'NfeStatusServico2': 'https://nfe.sefaz.am.gov.br/services2/services/NfeStatusServico2',
            'CadConsultaCadastro2': 'https://nfe.sefaz.am.gov.br/services2/services/CadConsultaCadastro2',
            'RecepcaoEvento': 'https://nfe.sefaz.am.gov.br/services2/services/RecepcaoEvento'},
        'BA': {
            'NfeRecepcao2': 'https://nfe.sefaz.ba.gov.br/webservices/nfenw/NfeRecepcao2.asmx',
            'NfeRetRecepcao2': 'https://nfe.sefaz.ba.gov.br/webservices/nfenw/NfeRetRecepcao2.asmx',
            'NfeInutilizacao2': 'https://nfe.sefaz.ba.gov.br/webservices/nfenw/NfeInutilizacao2.asmx',
            'NfeConsulta2': 'https://nfe.sefaz.ba.gov.br/webservices/nfenw/NfeConsulta2.asmx',
            'NfeStatusServico2': 'https://nfe.sefaz.ba.gov.br/webservices/nfenw/NfeStatusServico2.asmx',
            'CadConsultaCadastro2': 'https://nfe.sefaz.ba.gov.br/webservices/nfenw/CadConsultaCadastro2.asmx',
            'RecepcaoEvento': 'https://nfe.sefaz.ba.gov.br/webservices/sre/RecepcaoEvento.asmx'},
        'CE': {
            'NfeRecepcao2': 'https://nfe.sefaz.ce.gov.br/nfe2/services/NfeRecepcao2',
            'NfeRetRecepcao2': 'https://nfe.sefaz.ce.gov.br/nfe2/services/NfeRetRecepcao2',
            'NfeInutilizacao2': 'https://nfe.sefaz.ce.gov.br/nfe2/services/NfeInutilizacao2',
            'NfeConsulta2': 'https://nfe.sefaz.ce.gov.br/nfe2/services/NfeConsulta2',
            'NfeStatusServico2': 'https://nfe.sefaz.ce.gov.br/nfe2/services/NfeStatusServico2',
            'CadConsultaCadastro2': 'https://nfe.sefaz.ce.gov.br/nfe2/services/CadConsultaCadastro2',
            'RecepcaoEvento': 'https://nfe.sefaz.ce.gov.br/nfe2/services/RecepcaoEvento'},
        'GO': {
            'NfeRecepcao2': 'https://nfe.sefaz.go.gov.br/nfe/services/v2/NfeRecepcao2',
            'NfeRetRecepcao2': 'https://nfe.sefaz.go.gov.br/nfe/services/v2/NfeRetRecepcao2',
            'NfeInutilizacao2': 'https://nfe.sefaz.go.gov.br/nfe/services/v2/NfeInutilizacao2',
            'NfeConsulta2': 'https://nfe.sefaz.go.gov.br/nfe/services/v2/NfeConsulta2',
            'NfeStatusServico2': 'https://nfe.sefaz.go.gov.br/nfe/services/v2/NfeStatusServico2',
            'CadConsultaCadastro2': 'https://nfe.sefaz.go.gov.br/nfe/services/v2/CadConsultaCadastro2',
            'RecepcaoEvento': 'https://nfe.sefaz.go.gov.br/nfe/services/v2/RecepcaoEvento'},
        'MG': {
            'NfeRecepcao2': 'https://nfe.fazenda.mg.gov.br/nfe2/services/NfeRecepcao2',
            'NfeRetRecepcao2': 'https://nfe.fazenda.mg.gov.br/nfe2/services/NfeRetRecepcao2',
            'NfeInutilizacao2': 'https://nfe.fazenda.mg.gov.br/nfe2/services/NfeInutilizacao2',
            'NfeConsulta2': 'https://nfe.fazenda.mg.gov.br/nfe2/services/NfeConsulta2',
            'NfeStatus2': 'https://nfe.fazenda.mg.gov.br/nfe2/services/NfeStatus2',
            'CadConsultaCadastro2': 'https://nfe.fazenda.mg.gov.br/nfe2/services/cadconsultacadastro2',
            'RecepcaoEvento': 'https://nfe.fazenda.mg.gov.br/nfe2/services/RecepcaoEvento'},
        'MS': {
            'NfeRecepcao2': 'https://nfe.fazenda.ms.gov.br/producao/services2/NfeRecepcao2',
            'NfeRetRecepcao2': 'https://nfe.fazenda.ms.gov.br/producao/services2/NfeRetRecepcao2',
            'NfeInutilizacao2': 'https://nfe.fazenda.ms.gov.br/producao/services2/NfeInutilizacao2',
            'NfeConsulta2': 'https://nfe.fazenda.ms.gov.br/producao/services2/NfeConsulta2',
            'NfeStatusServico2': 'https://nfe.fazenda.ms.gov.br/producao/services2/NfeStatusServico2',
            'CadConsultaCadastro2': 'https://nfe.fazenda.ms.gov.br/producao/services2/CadConsultaCadastro2',
            'RecepcaoEvento': 'https://nfe.fazenda.ms.gov.br/producao/services2/RecepcaoEvento'},
        'MT': {
            'NfeRecepcao2': 'https://nfe.sefaz.mt.gov.br/nfews/v2/services/NfeRecepcao2',
            'NfeRetRecepcao2': 'https://nfe.sefaz.mt.gov.br/nfews/v2/services/NfeRetRecepcao2',
            'NfeInutilizacao2': 'https://nfe.sefaz.mt.gov.br/nfews/v2/services/NfeInutilizacao2',
            'NfeConsulta2': 'https://nfe.sefaz.mt.gov.br/nfews/v2/services/NfeConsulta2',
            'NfeStatusServico2': 'https://nfe.sefaz.mt.gov.br/nfews/v2/services/NfeStatusServico2',
            'CadConsultaCadastro2': 'https://nfe.sefaz.mt.gov.br/nfews/v2/services/CadConsultaCadastro2',
            'RecepcaoEvento': 'https://nfe.sefaz.mt.gov.br/nfews/v2/services/RecepcaoEvento'},
        'PE': {
            'NfeRecepcao2': 'https://nfe.sefaz.pe.gov.br/nfe-service/services/NfeRecepcao2',
            'NfeRetRecepcao2': 'https://nfe.sefaz.pe.gov.br/nfe-service/services/NfeRetRecepcao2',
            'NfeInutilizacao2': 'https://nfe.sefaz.pe.gov.br/nfe-service/services/NfeInutilizacao2',
            'NfeConsulta2': 'https://nfe.sefaz.pe.gov.br/nfe-service/services/NfeConsulta2',
            'NfeStatusServico2': 'https://nfe.sefaz.pe.gov.br/nfe-service/services/NfeStatusServico2',
            'CadConsultaCadastro2': 'https://nfe.sefaz.pe.gov.br/nfe-service/services/CadConsultaCadastro2',
            'RecepcaoEvento': 'https://nfe.sefaz.pe.gov.br/nfe-service/services/RecepcaoEvento'},
        'PR': {
            'NfeRecepcao2': 'https://nfe2.fazenda.pr.gov.br/nfe/NFeRecepcao2',
            'NfeRetRecepcao2': 'https://nfe2.fazenda.pr.gov.br/nfe/NFeRetRecepcao2',
            'NfeInutilizacao2': 'https://nfe2.fazenda.pr.gov.br/nfe/NFeInutilizacao2',
            'NfeConsulta2': 'https://nfe2.fazenda.pr.gov.br/nfe/NFeConsulta2',
            'NfeStatusServico2': 'https://nfe2.fazenda.pr.gov.br/nfe/NFeStatusServico2',
            'CadConsultaCadastro2': 'https://nfe2.fazenda.pr.gov.br/nfe/CadConsultaCadastro2',
            'RecepcaoEvento': 'https://nfe2.fazenda.pr.gov.br/nfe-evento/NFeRecepcaoEvento'},
        'RN': {
            'CadConsultaCadastroWS': 'https://webservice.set.rn.gov.br/projetonfeprod/set_nfe/servicos/CadConsultaCadastroWS.asmx'},
        'RS': {
            'NfeRecepcao2': 'https://nfe.sefaz.rs.gov.br/ws/Nferecepcao/NFeRecepcao2.asmx',
            'NfeRetRecepcao2': 'https://nfe.sefaz.rs.gov.br/ws/NfeRetRecepcao/NfeRetRecepcao2.asmx',
            'NfeInutilizacao2': 'https://nfe.sefaz.rs.gov.br/ws/nfeinutilizacao/nfeinutilizacao2.asmx',
            'NfeConsulta2': 'https://nfe.sefaz.rs.gov.br/ws/NfeConsulta/NfeConsulta2.asmx',
            'NfeStatusServico2': 'https://nfe.sefaz.rs.gov.br/ws/NfeStatusServico/NfeStatusServico2.asmx',
            'CadConsultaCadastro2': 'https://sef.sefaz.rs.gov.br/ws/cadconsultacadastro/CadConsultaCadastro2.asmx',
            'RecepcaoEvento': 'https://nfe.sefaz.rs.gov.br/ws/recepcaoevento/recepcaoevento.asmx',
            'NfeConsultaDest': 'https://nfe.sefaz.rs.gov.br/ws/nfeConsultaDest/nfeConsultaDest.asmx',
            'NfeDownloadNF': 'https://nfe.sefaz.rs.gov.br/ws/nfeDownloadNF/nfeDownloadNF.asmx'},
        'SP': {
            'NfeRecepcao2': 'https://nfe.fazenda.sp.gov.br/nfeweb/services/nferecepcao2.asmx',
            'NfeRetRecepcao2': 'https://nfe.fazenda.sp.gov.br/nfeweb/services/nferetrecepcao2.asmx',
            'NfeInutilizacao2': 'https://nfe.fazenda.sp.gov.br/nfeweb/services/nfeinutilizacao2.asmx',
            'NfeConsulta2': 'https://nfe.fazenda.sp.gov.br/nfeweb/services/nfeconsulta2.asmx',
            'NfeStatusServico2': 'https://nfe.fazenda.sp.gov.br/nfeweb/services/nfestatusservico2.asmx',
            'CadConsultaCadastro2': 'https://nfe.fazenda.sp.gov.br/nfeweb/services/CadConsultaCadastro2.asmx',
            'RecepcaoEvento': 'https://nfe.fazenda.sp.gov.br/eventosWEB/services/RecepcaoEvento.asmx'},
        'SVAN': {
            'NfeRecepcao2': 'https://www.sefazvirtual.fazenda.gov.br/NfeRecepcao2/NfeRecepcao2.asmx',
            'NfeRetRecepcao2': 'https://www.sefazvirtual.fazenda.gov.br/NfeRetRecepcao2/NfeRetRecepcao2.asmx',
            'NfeInutilizacao2': 'https://www.sefazvirtual.fazenda.gov.br/NfeInutilizacao2/NfeInutilizacao2.asmx',
            'NfeConsulta2': 'https://www.sefazvirtual.fazenda.gov.br/NfeConsulta2/NfeConsulta2.asmx',
            'NfeStatusServico2': 'https://www.sefazvirtual.fazenda.gov.br/NfeStatusServico2/NfeStatusServico2.asmx',
            'RecepcaoEvento': 'https://www.sefazvirtual.fazenda.gov.br/RecepcaoEvento/RecepcaoEvento.asmx',
            'NfeDownloadNF': 'https://www.sefazvirtual.fazenda.gov.br/NfeDownloadNF/NfeDownloadNF.asmx'},
        'SVRS': {
            'NfeRecepcao2': 'https://nfe.sefazvirtual.rs.gov.br/ws/Nferecepcao/NFeRecepcao2.asmx',
            'NfeRetRecepcao2': 'https://nfe.sefazvirtual.rs.gov.br/ws/NfeRetRecepcao/NfeRetRecepcao2.asmx',
            'NfeInutilizacao2': 'https://nfe.sefazvirtual.rs.gov.br/ws/nfeinutilizacao/nfeinutilizacao2.asmx',
            'NfeConsulta2': 'https://nfe.sefazvirtual.rs.gov.br/ws/NfeConsulta/NfeConsulta2.asmx',
            'NfeStatusServico2': 'https://nfe.sefazvirtual.rs.gov.br/ws/NfeStatusServico/NfeStatusServico2.asmx',
            'RecepcaoEvento': 'https://nfe.sefazvirtual.rs.gov.br/ws/recepcaoevento/recepcaoevento.asmx'},
        'SCAN': {
            'NfeRecepcao2': 'https://www.scan.fazenda.gov.br/NfeRecepcao2/NfeRecepcao2.asmx',
            'NfeRetRecepcao2': 'https://www.scan.fazenda.gov.br/NfeRetRecepcao2/NfeRetRecepcao2.asmx',
            'NfeInutilizacao2': 'https://www.scan.fazenda.gov.br/NfeInutilizacao2/NfeInutilizacao2.asmx',
            'NfeConsulta2': 'https://www.scan.fazenda.gov.br/NfeConsulta2/NfeConsulta2.asmx',
            'NfeStatusServico2': 'https://www.scan.fazenda.gov.br/NfeStatusServico2/NfeStatusServico2.asmx',
            'RecepcaoEvento': 'https://www.scan.fazenda.gov.br/RecepcaoEvento/RecepcaoEvento.asmx'},
        'AN': {
            'RecepcaoEvento': 'https://www.nfe.fazenda.gov.br/RecepcaoEvento/RecepcaoEvento.asmx',
            'NfeConsultaDest': 'https://www.nfe.fazenda.gov.br/NFeConsultaDest/NFeConsultaDest.asmx',
            'NfeDownloadNF': 'https://www.nfe.fazenda.gov.br/NfeDownloadNF/NfeDownloadNF.asmx'}
    }
}

cnpj = '11222333000101'
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
        #if sefaz not in ('PR', 'GO'): continue
        print ' ', sefaz
        criar_diretorios(sefaz)
        for servico, url in servicos.items():
            servico += '.wsdl'
            servidor, uri = url[8:].split('/', 1)
            uri = '/' + uri + '?wsdl'
            print '   ', servico
            print '     ', servidor
            print '       ', uri
            conexao = HTTPSConnection(servidor, 443, key_file, cert_file)
            conexao.request('GET', uri)
            cab_xml = "<?xml version='1.0' encoding='UTF-8'?>"
            wsdl = conexao.getresponse().read()
            if wsdl[:6] != cab_xml[:6]:
                wsdl = cab_xml + wsdl
            open('%s/%s/%s' % (sefaz, ambiente, servico), 'wb').write(wsdl)
            conexao.close()
