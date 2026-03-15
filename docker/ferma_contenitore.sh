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
docker stop ${ID_CONTENITORE}
