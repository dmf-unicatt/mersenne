# Copyright (C) 2024-2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT
"""Pacchetto con i servizi relativi ai test dell'applicazione."""

from mersenne.services.test.crea_gara import crea_gara
from mersenne.services.test.crea_utente import crea_utente
from mersenne.services.test.data_dir import data_dir
from mersenne.services.test.disabilita_fixture import disabilita_fixture
from mersenne.services.test.live_server import LiveServer, live_server
from mersenne.services.test.verifica_screenshot import (
    VerificaScreenshotType,
    verifica_screenshot,
)
