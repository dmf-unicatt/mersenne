#!/bin/bash
# Copyright (C) 2024-2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT

set -e
set -u

# Non procedere oltre se non c'è connessione a internet
wget -q --spider https://www.google.com

# Determina la versione di debian per la quale costruire l'immagine
set +u
VERSIONE_DEBIAN=$1
set -u
if [[ -z "${VERSIONE_DEBIAN}" ]]; then
    VERSIONE_DEBIAN="13"
fi
if [[ "${VERSIONE_DEBIAN}" != "13" && "${VERSIONE_DEBIAN}" != "testing" && "${VERSIONE_DEBIAN}" != "unstable" ]]; then
    echo "Versione Debian non valida ${VERSIONE_DEBIAN}"
    exit 1
fi

# Costruisci l'immagine
docker build --pull -t ghcr.io/dmf-unicatt/mersenne:latest -f Dockerfile --build-arg VERSIONE_DEBIAN=${VERSIONE_DEBIAN} ..
