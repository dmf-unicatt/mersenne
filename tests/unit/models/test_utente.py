# Copyright (C) 2024-2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT
"""Test di unità per il modello Utente."""

import django.contrib.auth

import mersenne.models
import mersenne_test_utils.factories


def test_get_user_model() -> None:
    """Verifica la configurazione del modello personalizzato di utente."""
    assert django.contrib.auth.get_user_model() == mersenne.models.Utente


def test_creazione_amministratore() -> None:
    """Verifica la creazione di un utente amministratore."""
    amministratore = mersenne_test_utils.factories.crea_utente(
        django_db=False,
        username="admin_test",
        email="admin@test.com",
        password="test_password_12345",
        is_superuser=True,
    )
    assert amministratore.pk is None
    assert amministratore.username == "admin_test"
    assert amministratore.is_superuser


def test_creazione_utente() -> None:
    """Verifica la creazione di un utente normale (non amministratore)."""
    utente = mersenne_test_utils.factories.crea_utente(
        django_db=False,
        username="user_test",
        email="user@test.com",
        password="test_password_ABCDE",
        is_superuser=False,
    )
    assert utente.pk is None
    assert utente.username == "user_test"
    assert not utente.is_superuser
