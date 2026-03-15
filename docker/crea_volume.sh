#!/bin/bash
# Copyright (C) 2024-2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT

set -e
set -u

FILE_ID_VOLUME=".id_volume"
if [[ -f "${FILE_ID_VOLUME}" ]]; then
    echo "Esiste già un volume per il database!"
    exit 1
else
    ID_VOLUME=$(docker volume create mersenne-database-$(date +%s))
    echo ${ID_VOLUME} > ${FILE_ID_VOLUME}
fi
