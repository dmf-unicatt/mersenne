# Copyright (C) 2024-2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT
"""Pacchetto con le fixture per i test dell'applicazione."""

from mersenne_test_utils.fixtures.data_dir import data_dir
from mersenne_test_utils.fixtures.disabilita_fixture import disabilita_fixture
from mersenne_test_utils.fixtures.live_server import LiveServer, live_server
from mersenne_test_utils.fixtures.verifica_screenshot import (
    VerificaScreenshotType,
    verifica_screenshot,
)
