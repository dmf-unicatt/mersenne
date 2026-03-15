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
    echo "Devi indicare il componente da controllare (ruff, mypy, spdx) come secondo argomento"
    exit 1
fi
if [[ "${COMPONENTE}" != "ruff" && "${COMPONENTE}" != "mypy" && "${COMPONENTE}" != "spdx" ]]; then
    echo "Componente non valido ${COMPONENTE}"
    exit 1
fi

COMANDO_PULIZIA="\
    find . -name '*.pyc' -exec rm {} \\; && \
    rm -rf .ruff_cache && \
    rm -rf .mypy_cache && \
    rm -rf .pytest_cache && \
    rm -rf docs/build \
"

if [[ "${COMPONENTE}" == "ruff" ]]; then
    COMANDO_LINT="\
        python3 -m ruff format --check --exclude=\"mersenne/migrations\" . && \
        python3 -m ruff check --exclude=\"mersenne/migrations\" . \
    "
elif [[ "${COMPONENTE}" == "mypy" ]]; then
    COMANDO_LINT="\
        python3 -m mypy --exclude=\"conftest.py|mersenne/migrations/.*\" . && \
        find . -type f -name conftest.py -exec python3 -m mypy {} \\; \
    "
elif [[ "${COMPONENTE}" == "spdx" ]]; then
    COMANDO_LINT="\
        find . -type f | grep -vE '^./.bashrc|^./.bash_history|^./.cache|^./config/settings.ini|^./config/static|^./.profile|^./mersenne/migrations|^./AUTHORS$|^./LICENSE$|\.dockerignore$|\.gitignore$|\.journal$|\.json$|\.log$|\.md$|\.rst$|\.score$|\.toml$|\.typed$' | while read -r f; do head -n 7 "\$f" | grep -q \"SPDX-License-Identifier:\" || echo \"SPDX mancante: \$f\"; done | grep \"SPDX mancante:\" && exit 1 || exit 0 \
    "
fi

if [[ "${MODALITA_ESECUZIONE}" == "exec" ]]; then
    FILE_ID_CONTENITORE=".id_contenitore"
    ID_CONTENITORE=$(cat "${FILE_ID_CONTENITORE}")
    docker exec ${ID_CONTENITORE} /bin/bash -c "${COMANDO_PULIZIA} && ${COMANDO_LINT}; ${COMANDO_PULIZIA}"
elif [[ "${MODALITA_ESECUZIONE}" == "run" ]]; then
    docker run --rm ghcr.io/dmf-unicatt/mersenne:latest /bin/bash -c "${COMANDO_PULIZIA} && ${COMANDO_LINT}; ${COMANDO_PULIZIA}"
fi
