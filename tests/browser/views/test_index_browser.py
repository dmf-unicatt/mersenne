# Copyright (C) 2024-2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT
"""File vuoto in attesa che vengano aggiunti test reali."""

import playwright.sync_api

import mersenne.services.test


def test_index_screenshot(
    live_server: mersenne.services.test.LiveServer,
    page: playwright.sync_api.Page,
    verifica_screenshot: mersenne.services.test.VerificaScreenshotType,
) -> None:
    """Verifica che l'home page corrisponda allo screenshot atteso."""
    page.goto(f"{live_server}")
    page.wait_for_load_state("networkidle")
    verifica_screenshot(page)
