#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""PoleLog - Operações com Log em Python

Arquivo: PoleLog.py
Versão.: 0.2.0
Autor..: Claudio Polegato Junior
Data...: 04 Abr 2011

Copyright © 2011 - Claudio Polegato Junior <junior@juniorpolegato.com.br>
Todos os direitos reservados
"""

# Importing modules for log and debug
import sys
#import inspect
import traceback

# Translation
import PoleUtil
_ = PoleUtil._

DEBUG = False

def log(message):
    print '-~=' * 20
    print message
    print '-~=' * 20

def log_except():
    print '-~=' * 20
    traceback.print_exc()
    print '-~=' * 20    
    #~ frame = inspect.currentframe().f_back
    #~ if frame.f_back:
        #~ frame = frame.f_back
    #~ filename, lineno, function, code_context, index = inspect.getframeinfo(frame)
    #~ message = '%s - %s - %s:\n' % (filename, function, lineno)
    #~ if not code_context:
        #~ message += _("No code context\n")
    #~ else:
        #~ message += ''.join(code_context).rstrip() + '\n'
    #~ if type(sys.exc_info()[1]) == tuple and reduce(lambda x,y: x and type(y) in (str, unicode, int), sys.exc_info()[1]):
        #~ message += "%s: %s" % (type(sys.exc_info()[1]).__name__, ''.join(sys.exc_info()[1]))
    #~ else:
        #~ message += "%s: %s => %s" % (type(sys.exc_info()[1]).__name__, repr(sys.exc_info()[1]), str(sys.exc_info()[1]))
    #~ log(message)

def debug(message, var = ''):
    if DEBUG:
        print "DEBUG:", message, ":", var
