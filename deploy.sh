#!/bin/bash

mount /media/ERP_3.0.0/

if [ "$1" == "po" ]; then
    cp -av po/locale/pt_BR/LC_MESSAGES/pole.mo /media/ERP_3.0.0/pole/po/locale/pt_BR/LC_MESSAGES/pole.mo
    cp -av po/locale/es_ES/LC_MESSAGES/pole.mo /media/ERP_3.0.0/pole/po/locale/es_ES/LC_MESSAGES/pole.mo
else
    cp -av $1 /media/ERP_3.0.0/pole/
fi

sync
umount /media/ERP_3.0.0/

