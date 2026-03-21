# Copyright (C) 2024-2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT
"""Configurazione pytest per i test con browser di mersenne."""

import typing

import playwright.sync_api
import pytest

import mersenne_test_utils.fixtures

data_dir = mersenne_test_utils.fixtures.data_dir
live_server = mersenne_test_utils.fixtures.live_server
verifica_screenshot = mersenne_test_utils.fixtures.verifica_screenshot


@pytest.fixture(scope="session")
def browser() -> typing.Generator[playwright.sync_api.Browser, None, None]:
    """Crea un'istanza browser Playwright per tutti i test."""
    with playwright.sync_api.sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture
def page(
    browser: playwright.sync_api.Browser,
) -> typing.Generator[playwright.sync_api.Page, None, None]:
    """Crea una nuova pagina per ogni test."""
    page = browser.new_page()
    yield page
    page.close()


@pytest.fixture
def viewport_size_desktop() -> dict[str, int]:
    """Restituisce la dimensione della viewport per un desktop."""
    return {"width": 1920, "height": 1080}


@pytest.fixture
def viewport_size_tablet_landscape() -> dict[str, int]:
    """Restituisce la dimensione della viewport per un tablet in orizzontale."""
    return {"width": 1024, "height": 768}


@pytest.fixture
def viewport_size_tablet_portrait() -> dict[str, int]:
    """Restituisce la dimensione della viewport per un tablet in verticale."""
    return {"width": 768, "height": 1024}


@pytest.fixture
def viewport_size_mobile_landscape() -> dict[str, int]:
    """Restituisce la dimensione della viewport per un telefono in orizzontale."""  # noqa: E501, W505
    return {"width": 667, "height": 375}


@pytest.fixture
def viewport_size_mobile_portrait() -> dict[str, int]:
    """Restituisce la dimensione della viewport per un telefono in verticale."""
    return {"width": 375, "height": 667}
