#!/bin/bash
# Copyright (C) 2024-2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT

set -e
set -u

set +u
MODALITA_ESECUZIONE=$1
set -u
if [[ -z "${MODALITA_ESECUZIONE}" ]]; then
    echo "Devi indicare la modalità di esecuzione (exec, run) come primo argomento"
    exit 1
fi
if [[ "${MODALITA_ESECUZIONE}" != "exec" && "${MODALITA_ESECUZIONE}" != "run" ]]; then
    echo "Tipo di esecuzione non valido ${MODALITA_ESECUZIONE}"
    exit 1
fi

set +u
COMPONENTE=$2
set -u
if [[ -z "${COMPONENTE}" ]]; then
    echo "Devi indicare il componente da testare (unit, integration, browser) come secondo argomento"
    exit 1
fi
if [[ "${COMPONENTE}" != "unit" && "${COMPONENTE}" != "integration" && "${COMPONENTE}" != "browser" ]]; then
    echo "Componente non valido ${COMPONENTE}"
    exit 1
fi

set +u
TIPO_DATABASE=$3
set -u
if [[ -z "${TIPO_DATABASE}" ]]; then
    TIPO_DATABASE="PostgreSQL"
fi
if [[
    "${TIPO_DATABASE}" != "PostgreSQL" && "${TIPO_DATABASE}" != "SQLite3"
]]; then
    echo "Tipo di database non valido ${TIPO_DATABASE}"
    exit 1
fi

COMANDO_TEST="\
    python3 -m pytest tests/${COMPONENTE} \
"

if [[ "${TIPO_DATABASE}" == "PostgreSQL" ]]; then
    PREPARAZIONE_DATABASE="\
        POSTGRES_DATABASE_NAME=\$(sed -n -e \"s/^RDS_DB_NAME=//p\" /root/config/settings.ini) && \
        sudo -u postgres dropdb --if-exists test_\${POSTGRES_DATABASE_NAME} \
    "
elif [[ "${TIPO_DATABASE}" == "SQLite3" ]]; then
    PREPARAZIONE_DATABASE="\
        sed -i \"s/RDS_DB_NAME/DISABLED_RDS_DB_NAME/\" /root/config/settings.ini \
    "
fi

if [[ "${MODALITA_ESECUZIONE}" == "exec" ]]; then
    if [[ "${TIPO_DATABASE}" == "PostgreSQL" ]]; then
        FILE_ID_CONTENITORE=".id_contenitore"
        ID_CONTENITORE=$(cat "${FILE_ID_CONTENITORE}")
        docker exec ${ID_CONTENITORE} /bin/bash -c "${PREPARAZIONE_DATABASE} && ${COMANDO_TEST}"
    elif [[ "${TIPO_DATABASE}" == "SQLite3" ]]; then
        echo "Non è possibile usare docker exec e cambiare il tipo di database in SQLite3, perché modificherebbe il contenitore esistente"
        exit 1
    fi
elif [[ "${MODALITA_ESECUZIONE}" == "run" ]]; then
    docker run --rm ghcr.io/dmf-unicatt/mersenne:latest \
    /bin/bash -c "${PREPARAZIONE_DATABASE} && ${COMANDO_TEST}"
fi
