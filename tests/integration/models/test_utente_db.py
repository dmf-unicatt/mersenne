# Copyright (C) 2024-2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT
"""Test di integrazione con database per il modello Utente."""

import pytest

import mersenne.models
import mersenne.services.test


@pytest.mark.django_db
def test_creazione_amministratore_db() -> None:
    """Verifica la creazione di un utente amministratore nel db."""
    amministratore = mersenne.services.test.crea_utente(
        django_db=True,
        username="admin_test",
        email="admin@test.com",
        password="test_password_12345",
        is_superuser=True,
    )
    assert amministratore.pk is not None
    assert amministratore.username == "admin_test"
    assert amministratore.is_superuser


@pytest.mark.django_db
def test_creazione_utente_db() -> None:
    """Verifica la creazione di un utente normale nel db."""
    utente = mersenne.services.test.crea_utente(
        django_db=True,
        username="user_test",
        email="user@test.com",
        password="test_password_ABCDE",
        is_superuser=False,
    )
    assert utente.pk is not None
    assert utente.username == "user_test"
    assert not utente.is_superuser
