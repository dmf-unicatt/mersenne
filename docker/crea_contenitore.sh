#!/bin/bash
# Copyright (C) 2024-2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT

set -e
set -u

FILE_ID_VOLUME=".id_volume"
ID_VOLUME=$(cat "${FILE_ID_VOLUME}")

PROPRIETA_RETE="-p 80:80"

FILE_ID_CONTENITORE=".id_contenitore"
if [[ -f "${FILE_ID_CONTENITORE}" ]]; then
    echo "Esiste già un contenitore!"
    echo "Se vuoi avviarlo, esegui ./avvia_contenitore.sh"
    exit 1
else
    ID_CONTENITORE=$(docker create ${PROPRIETA_RETE} -v /tmp/shared-mersenne:/shared/host-tmp -v $(dirname ${PWD}):/shared/git-repo -v ${ID_VOLUME}:/mnt -e DOCKERHOSTNAME=$(cat /etc/hostname) -e TZ=$(timedatectl show --va -p Timezone) -e TERM=${TERM} ghcr.io/dmf-unicatt/mersenne:latest)
    echo ${ID_CONTENITORE} > ${FILE_ID_CONTENITORE}
fi
