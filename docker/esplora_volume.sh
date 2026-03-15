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
docker run -it --rm -v ${ID_VOLUME}:/mnt --workdir=/mnt debian:latest
