#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PoleUtil import normalize


class LX300(object):
    _BRAND = 'Epson'
    _MODEL = 'LX300'
    _ENCODING = 'CP850'
    _ENC_PROG = '\x1B\x28\x74\x33\x30\x00\x03\x00\x1B\x74\x00'  # CP850
    _CR = '\x0D'  # carrige return
    _LF = '\x0A'  # line feed
    _FF = '\x0C'  # form feed
    _SI = '\x0F'  # condensed
    _SO = '\x0E'  # select double-width mode (one line)
    _DC1 = '\x11'  # select printer
    _DC2 = '\x12'  # cancel condensed mode
    _DC3 = '\x13'  # deselect printer
    _DC4 = '\x14'  # cancel double-width mode (one line)
    _CAN = '\x18'  # cancel line
    _DEL = '\x7F'  # delete character
    _BEL_7 = '\x07'      # beeper
    _ESC_s = '\x1B\x73'  # turn half-speed mode on/off
    _ESC_U = '\x1B\x55'  # turn unidirectional mode on/off
    _ESC_8 = '\x1B\x38'  # disable paper-out detection
    _ESC_9 = '\x1B\x39'  # enable paper-out detection
    _ESC_P = '\x1B\x50'  # select 10 cpi
    _ESC_M = '\x1B\x4D'  # select 12 cpi
    _ESC_W = '\x1B\x57'  # turn double-width mode on/off
    _ESC_AT = '\x1B\x40'  # initialize printer
    _ESC_SI = '\x1B\x0F'  # select condensed mode
    _ESC_SO = '\x1B\x0E'  # select double-width mode (one line)
    _ESC_lt = '\x1B\x3C'  # Select Unidirectional Mode (one line)

    def __init__(self):
        super(LX300, self).__init__()
        self._buffer = ''
        self._lines_counter = 0
        self.initialize_printer()

    @property
    def brand(self):
        return self._BRAND

    @property
    def model(self):
        return self._MODEL

    @property
    def raw_buffer(self):
        return self._buffer

    @property
    def lines(self):
        return self._lines_counter

    def clear_buffer(self):
        self._lines_counter = 0
        self._buffer = ''

    def initialize_printer(self):
        self.append(LX300._DC2, command=True)
        self.append(LX300._DC4, command=True)
        self.append(LX300._ESC_P, command=True)
        self.append(LX300._ESC_AT, command=True)
        self.append(LX300._ENC_PROG, command=True)

    def carriage_return(self):
        self.append(LX300._CR, command=True)

    def line_feed(self, lines=1):
        self.append(LX300._LF * lines, command=True)
        self._lines_counter += 1 * lines

    def select_10_cpi(self):
        self.append(LX300._ESC_P, command=True)

    def select_condensed_mode(self):
        self.cancel_doublewith_mode()
        self.append(LX300._SI, command=True)

    def cancel_condensed_mode(self):
        self.append(LX300._DC2, command=True)

    def select_doublewith_mode(self):
        self.cancel_condensed_mode()
        self.append(LX300._SO, command=True)

    def cancel_doublewith_mode(self):
        self.append(LX300._DC4, command=True)

    def return_and_feed(self, lines=1):
        self.carriage_return()
        self.line_feed(lines)

    def append(self, text, *args, **kwargs):
        if args:
            text = text.format(*args)

        if not isinstance(text, (str, unicode)):
            text = str(text)

        if kwargs.get('command'):
            self._buffer += text
        else:
            try:
                self._buffer += text.decode('utf-8').encode(
                    LX300._ENCODING, 'replace')
            except Exception:
                self._buffer += normalize(text)


class ImpressoLX300(LX300):
    def __init__(self, linhas_folha, linhas_avanco, linhas_cabecalho):
        super(ImpressoLX300, self).__init__()
        self.linhas_folha = linhas_folha
        self.linhas_avanco = linhas_avanco
        self.linhas_cabecalho = linhas_cabecalho

    def escreve_condensado(self, texto, *args, **kwargs):
        self.select_condensed_mode()
        self._escreve(texto, *args, **kwargs)

    def escreve_negrito(self, texto, *args, **kwargs):
        self.select_doublewith_mode()
        self._escreve(texto, *args, **kwargs)

    def escreve(self, texto, *args, **kwargs):
        self.cancel_doublewith_mode()
        self.cancel_condensed_mode()
        self._escreve(texto, *args, **kwargs)

    def _escreve(self, texto, *args, **kwargs):
        self.append(texto, *args)

        if not kwargs.pop('mesmalinha', None):
            self.return_and_feed()

    def eof(self):
        total_linhas = self.lines + self.linhas_avanco

        if total_linhas <= self.linhas_folha:
            picote = self.linhas_folha - total_linhas

        else:
            picote = self.linhas_folha - (total_linhas % self.linhas_folha) + 1

        if picote:
            self.line_feed(picote)

    def avanca_papel(self):
        self.line_feed(self.linhas_avanco - self.linhas_cabecalho)
