# Copyright (C) 2024-2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT
"""Verifica interattiva della pagina iniziale."""

import os

import django.conf
import pytest
import requests

import mersenne_test_utils.fixtures


@pytest.mark.skipif(
    not django.conf.settings.DEBUG,
    reason="Test valido solo per la modalità di sviluppo",
)
def test_liver_server_vite_se_debug_attivo(
    live_server: mersenne_test_utils.fixtures.LiveServer,
) -> None:
    """Verifica che in modalità di sviluppo il server Vite parta."""
    r = requests.get(
        os.environ["VITE_DEV_SERVER_URL"]
        + "/static/mersenne/frontend/js/main.js"
    )
    assert r.status_code == 200
    assert 'import "/static/mersenne/frontend/css/main.css"' in r.text
