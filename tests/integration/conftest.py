# Copyright (C) 2024-2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT
"""
Configurazione pytest per i test di integrazione di mersenne.

In questo file viene configurato l'accesso alla cartella con i dati
di gare passate, e viene disabilitata la fixture 'live_server'
di pytest-django (perché il server live verrà testato nei test con browser)
e le fixture 'rf' e 'async_rf' (perché test che necessitano di request factory
senza client fanno parte dei test di unità).
"""

import mersenne.services.test

data_dir = mersenne.services.test.data_dir


_pytest_django_fixtures = [
    "async_rf",
    "live_server",
    "rf",
]
for _ in _pytest_django_fixtures:
    globals()[_] = mersenne.services.test.disabilita_fixture(_)
