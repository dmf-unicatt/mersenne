# Copyright (C) 2024-2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT
"""Test di unità per la vista dell'home page."""

import django.test


def test_index_client(client: django.test.Client) -> None:
    """Verifica che la vista dell'home page restituisca il contenuto atteso."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Home page di prova" in response.content.decode()
