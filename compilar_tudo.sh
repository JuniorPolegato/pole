#!/bin/bash

find fontes -name "*.pyc" -exec rm -v "{}" \;
find fontes -name "*.py" -exec python -m py_compile "{}" \;
find fontes -name "*.pyc" -and -not -path "./modulos/*" -exec mv -v "{}" modulos/ \;
