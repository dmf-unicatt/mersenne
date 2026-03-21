# Copyright (C) 2024-2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT
"""Disabilita un elenco di fixture, caricate da un plugin di pytest."""

import typing

import pytest


def disabilita_fixture(nome: str) -> typing.Callable[[], None]:
    """Restituisce una fixture che restituisce un errore se viene usata."""

    def _() -> None:
        raise RuntimeError(f"Fixture '{nome}' disabilitata nei test di unità")

    _.__name__ = nome
    _.__doc__ = f"Restituisce un errore se viene usata la fixture '{nome}'."
    return pytest.fixture()(_)
