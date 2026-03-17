# Copyright (C) 2024-2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT
"""Verifica dei marker per i test di unità."""

import importlib.util
import pathlib
import types

import pytest


def _load_conftest_module() -> types.ModuleType:
    """
    Carica il modulo conftest.py dei test di unità.

    Il modulo non può essere importato direttamente perché pytest lo carica
    in modo speciale, quindi usiamo importlib per caricarlo manualmente.
    """
    spec = importlib.util.spec_from_file_location(
        "conftest", pathlib.Path(__file__).parent / ".." / "conftest.py"
    )
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


_conftest = _load_conftest_module()


def test_pytest_django_marker_disabilitati(pytest_django_marker: str) -> None:
    """Verifica che l'uso di marker disabilitati restituisca un errore."""

    class MockPytestMarker:
        def __init__(self, name: str) -> None:
            self.name = name

    class MockPytestItem:
        def __init__(self, name: str, markers: list[str]) -> None:
            self.name = name
            self.own_markers = [MockPytestMarker(m) for m in markers]

    item = MockPytestItem("dummy_test", [pytest_django_marker])
    with pytest.raises(
        RuntimeError, match=f"con @pytest.mark.{pytest_django_marker}, ma"
    ):
        _conftest.pytest_collection_modifyitems(None, None, [item])
