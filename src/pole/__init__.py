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

import PoleSetting as setting
import PoleUtil as util
import PolePDF as pdf
import PoleHTTP as http
import PolePrinter as printer

import PoleLog as log
from PoleLog import logger


try:
    import PoleGTK as gtk
except ImportError as error:
    logger.warning("Problemas ao importar o módulo PoleGTK: %s.", error)

try:
    import PoleXML as xml
except ImportError as error:
    logger.warning("Problemas ao importar o módulo PoleXML: %s.", error)

try:
    import PoleNFe as nfe
except ImportError as error:
    logger.warning("Problemas ao importar o módulo PoleNFe: %s.", error)

try:
    import PoleDANFe as danfe
except ImportError as error:
    logger.warning("Problemas ao importar o módulo PoleDANFe: %s.", error)

try:
    import PoleRelatorio as relatorio
except ImportError as error:
    logger.warning("Problemas ao importar o módulo PoleRelatorio: %s.", error)
