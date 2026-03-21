# Copyright (C) 2024-2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT
"""Restituisce la cartella contenente i dati di gare passate."""

import pathlib

import pytest

_data_dir = pathlib.Path(__file__).parents[2] / "data"


@pytest.fixture
def data_dir() -> pathlib.Path:
    """Restituisce la cartella contenente i dati di gare passate."""
    return _data_dir
