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
import os
import errno
import logging
from logging.handlers import RotatingFileHandler


_MAX_LOG_SIZE = 1024 * 1024 * 7
_MAX_LOG_BACKUP = 7


def setup_logging(app):
    log = logging.getLogger(app)
    log.setLevel(logging.INFO)

    formatter = logging.Formatter("%(levelname)s %(asctime)s %(name)s "
                                  "%(filename)s(%(lineno)d): %(message)s")

    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    log.addHandler(sh)

    log_dir = os.path.expanduser('~')
    log_file = os.path.join(log_dir, '.erp', app + '.log')

    try:
        if not os.path.isdir(log_dir):
            os.makedirs(log_dir)
    except IOError as e:
        if e.errno == errno.EEXIST:
            return
        raise

    try:
        fh = RotatingFileHandler(log_file, maxBytes=_MAX_LOG_SIZE,
                                 backupCount=_MAX_LOG_BACKUP)
    except IOError:
        logging.exception('Could not set up file logging.')
        fh = None

    if fh:
        fh.setLevel(logging.INFO)
        fh.setFormatter(formatter)
        log.addHandler(fh)

    if os.getenv('DEBUG_SESSION_POLE', 0) == '1':
        log.setLevel(logging.DEBUG)
        log.debug('Debug enabled.')

        try:
            fh.setLevel(logging.DEBUG)
        except Exception, e:
            log.error(e)


setup_logging('pole')
logger = logging.getLogger('pole')


def log(message):
    logger.info(message)


def log_except():
    logger.critical('Unexpected error!', exc_info=True)
