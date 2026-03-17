# Copyright (C) 2024-2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT
"""Verifica delle fixture per i test di unità."""

import django.db
import pytest


def test_pytest_django_fixture_disabilitate(
    request: pytest.FixtureRequest, pytest_django_fixture: str
) -> None:
    """Verifica che l'uso di fixture disabilitate restituisca un errore."""
    with pytest.raises(
        RuntimeError,
        match=(
            f"Fixture '{pytest_django_fixture}' disabilitata nei test di unità"
        ),
    ):
        request.getfixturevalue(pytest_django_fixture)


def test_accesso_db_bloccato_default() -> None:
    """
    Verifica che l'accesso al database sia bloccato.

    Il blocco avviene di default tramite pytest-django.
    """
    with pytest.raises(RuntimeError, match="Database access not allowed"):
        with django.db.connection.cursor() as cursor:
            cursor.execute("SELECT 1")
