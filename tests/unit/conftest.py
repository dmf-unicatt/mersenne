# Copyright (C) 2024-2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT
"""
Configurazione pytest per i test di unità di mersenne.

In questo file vengono inibite tutte le fixture di pytest-django che
consentono l'accesso al database, al client di test o al server live.
"""

import pytest

import mersenne_test_utils.fixtures

# Disabilita i marker di pytest-django

_pytest_django_markers = [
    "django_db",
]


def pytest_collection_modifyitems(
    session: pytest.Session, config: pytest.Config, items: list[pytest.Item]
) -> None:
    """Restituisce un errore se vengono usati i marker di pytest-django."""
    for item in items:
        for marker in item.own_markers:
            if marker.name in _pytest_django_markers:
                raise RuntimeError(
                    f"Il test '{item.name}' è marcato con "
                    f"@pytest.mark.{marker.name}, ma questo non è permesso "
                    "nei test di unità."
                )


# Disabilita la maggior parte delle fixture di pytest-django

_pytest_django_fixtures = [
    "admin_client",
    "admin_user",
    "async_client",
    "client",
    "db",
    "django_assert_num_queries",
    "django_assert_max_num_queries",
    "django_capture_on_commit_callbacks",
    "django_db_reset_sequences",
    "django_db_serialized_rollback",
    "live_server",
    "mailoutbox",
    "transactional_db",
]
for _ in _pytest_django_fixtures:
    globals()[_] = mersenne_test_utils.fixtures.disabilita_fixture(_)


# Esporta _pytest_django_markers e _pytest_django_fixtures per i test
# nella cartella conftest


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    """Parametrizza i test con i nomi di fixture e marker disabilitati."""
    if "pytest_django_fixture" in metafunc.fixturenames:
        metafunc.parametrize("pytest_django_fixture", _pytest_django_fixtures)
    if "pytest_django_marker" in metafunc.fixturenames:
        metafunc.parametrize("pytest_django_marker", _pytest_django_markers)
