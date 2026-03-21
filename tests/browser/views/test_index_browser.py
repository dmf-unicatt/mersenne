# Copyright (C) 2024-2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT
"""Verifica interattiva della pagina iniziale."""

import playwright.sync_api

import mersenne_test_utils.fixtures


def test_index_screenshot(
    live_server: mersenne_test_utils.fixtures.LiveServer,
    page: playwright.sync_api.Page,
    verifica_screenshot: mersenne_test_utils.fixtures.VerificaScreenshotType,
) -> None:
    """Verifica che l'home page corrisponda allo screenshot atteso."""
    page.goto(f"{live_server}")
    page.wait_for_load_state("networkidle")
    verifica_screenshot(page)
