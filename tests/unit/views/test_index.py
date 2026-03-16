# Copyright (C) 2024-2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT
"""Test di unità per l'home page."""

import django.test
import pytest

import mersenne.views


@pytest.mark.xfail(
    reason=(
        "Al momento necessita di un middleware per mostrare i messaggi "
        "di prova, che poi verranno rimossi"
    )
)
def test_index_rf(rf: django.test.RequestFactory) -> None:
    """Verifica che l'home page restituisca il contenuto atteso."""
    request = rf.get("/")
    response = mersenne.views.index(request)
    assert response.status_code == 200
    assert "Home page di prova" in response.content.decode()  # type: ignore[attr-defined]
