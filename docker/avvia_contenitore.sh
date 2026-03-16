#!/bin/bash
# Copyright (C) 2024-2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT

set -e
set -u

FILE_ID_CONTENITORE=".id_contenitore"
ID_CONTENITORE=$(cat "${FILE_ID_CONTENITORE}")
if [ "$(docker container inspect -f '{{.State.Running}}' ${ID_CONTENITORE})" == "true" ]; then
    echo "Il contenitore è già in esecuzione!"
    echo "Se vuoi collegare un terminale, esegui ./collega_terminale.sh"
    exit 1
else
    TEMPO_AVVIO=$(date +%s)
    docker start ${ID_CONTENITORE}
    MASSIMO_NUMERO_TENTATIVI=10
    INTERVALLO=1
    for TENTATIVO in $(seq 1 ${MASSIMO_NUMERO_TENTATIVI}); do
        LOG_DOCKER=$(
            docker logs --since "${TEMPO_AVVIO}" --timestamps ${ID_CONTENITORE} 2>&1
        )
        if [[ "${LOG_DOCKER}" == *"Application startup complete"* ]]; then
            echo "${LOG_DOCKER}"
            break
        else
            if [[ ${TENTATIVO} != ${MASSIMO_NUMERO_TENTATIVI} ]]; then
                sleep ${INTERVALLO}
            else
                echo "${LOG_DOCKER}"
                echo "Il server non si è ancora avviato dopo "\
                     "${MASSIMO_NUMERO_TENTATIVI} tentativi. " \
                     "L'output dei log potrebbe essere incompleto."
            fi
        fi
    done
fi
