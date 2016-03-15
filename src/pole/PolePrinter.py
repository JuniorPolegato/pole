#!/bin/env python
# -*- coding: utf-8 -*-

from PoleUtil import formatar


class LX300(object):
    _BRAND = 'Epson'
    _MODEL = 'LX300'
    _ESC_AT = chr(64)
    _CR = chr(13)
    _LF = chr(10)
    _ESC_P = chr(80)
    _ESC_SI = chr(15)
    _DC2 = chr(18)
    _ESC_SO = chr(14)
    _DC4 = chr(20)

    def __init__(self):
        super(LX300, self).__init__()
        self._buffer = ''
        self._lines_counter = 0

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
        self.append(LX300._ESC_AT)

    def carriage_return(self):
        self.append(LX300._CR)

    def line_feed(self, lines=1):
        self.append(LX300._LF * lines)
        self._lines_counter += 1 * lines

    def select_10_cpi(self):
        self.append(LX300._ESC_P)

    def select_condensed_mode(self):
        self.cancel_doublewith_mode()
        self.append(LX300._ESC_SI)

    def cancel_condensed_mode(self):
        self.append(LX300._DC2)

    def select_doublewith_mode(self):
        self.cancel_condensed_mode()
        self.append(LX300._ESC_SO)

    def cancel_doublewith_mode(self):
        self.append(LX300._DC4)

    def return_and_feed(self, lines=1):
        self.carriage_return()
        self.line_feed(lines)

    def append(self, text, *args):
        if args:
            text = text.format(*args)

        self._buffer += formatar(text, 'Letras')


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
            picote = abs(self.linhas_folha - total_linhas)

        else:
            picote = abs(self.linhas_folha - (total_linhas % self.linhas_folha))

        if picote:
            self.line_feed(picote)

    def avanca_papel(self):
        self.line_feed(self.linhas_avanco - self.linhas_cabecalho)
