#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""PoleUtil - Funções e classes em Python para uso frequente

Arquivo: __init__.py
Versão.: 0.4.1
Autor..: Claudio Polegato Junior
Data...: 31 Mar 2011

Copyright © 2011 - Claudio Polegato Junior <junior@juniorpolegato.com.br>
Todos os direitos reservados
"""

import PoleUtil as util
import PoleLog  as log

try:
    import PoleGTK  as gtk
except ImportError as err:
    print "Problemas ao importar o módulo PoleGTK: " + str(err)
import PolePDF  as pdf

try:
    import PoleXML  as xml
except ImportError as err:
    print "Problemas ao importar o módulo PoleXML: " + str(err)

try:
    import PoleNFe  as nfe
except ImportError as err:
    print "Problemas ao importar o módulo PoleNFe: " + str(err)

import PoleRelatorio  as relatorio
