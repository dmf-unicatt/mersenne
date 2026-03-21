# Copyright (C) 2024-2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT
"""File vuoto in attesa che vengano aggiunti test reali."""

import os
import pathlib
import socket

import playwright.sync_api
import pytest

import mersenne_test_utils.fixtures


@pytest.fixture
def necessita_internet() -> None:
    """Fixture che salta il test se non c'è connessione Internet."""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
    except OSError:
        pytest.skip("Test richiede connessione Internet")


def test_verifica_screenshot_example_org_successo(
    page: playwright.sync_api.Page,
    verifica_screenshot: mersenne_test_utils.fixtures.VerificaScreenshotType,
    necessita_internet: None,
) -> None:
    """Verifica la fixture con uno screenshot di confronto corretto."""
    page.goto("http://www.example.org/")
    page.wait_for_load_state("networkidle")
    verifica_screenshot(page)


def test_verifica_screenshot_example_org_dimensione_errata(
    page: playwright.sync_api.Page,
    verifica_screenshot: mersenne_test_utils.fixtures.VerificaScreenshotType,
    necessita_internet: None,
) -> None:
    """Verifica la fixture rispetto uno screenshot di dimensioni errate."""
    page.goto("http://www.example.org/")
    page.wait_for_load_state("networkidle")
    with pytest.raises(
        AssertionError,
        match="Le dimensioni dello screenshot differiscono",
    ):
        verifica_screenshot(page)
    os.remove(
        pathlib.Path(__file__).parent
        / "test_verifica_screenshot_example_org_dimensione_errata_1.png"
    )


def test_verifica_screenshot_example_org_contenuto_diverso(
    page: playwright.sync_api.Page,
    verifica_screenshot: mersenne_test_utils.fixtures.VerificaScreenshotType,
    necessita_internet: None,
) -> None:
    """Verifica la fixture rispetto uno screenshot di contenuto diverso."""
    page.goto("http://www.example.org/")
    page.wait_for_load_state("networkidle")
    with pytest.raises(AssertionError, match="Gli screenshot differiscono di"):
        verifica_screenshot(page)
    os.remove(
        pathlib.Path(__file__).parent
        / "test_verifica_screenshot_example_org_contenuto_diverso_1.png"
    )
    os.remove(
        pathlib.Path(__file__).parent
        / "test_verifica_screenshot_example_org_contenuto_diverso_1_diff.png"
    )
