# Copyright (C) 2024-2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT
"""Verifica la coerenza dei file nella cartella dei dati per i test."""

import pathlib

import pytest


def test_presenza_cartella_dati(data_dir: pathlib.Path) -> None:
    """Verifica la presenza della cartella con i dati per i test."""
    assert data_dir.exists()
    assert data_dir.is_dir()
    for elemento in data_dir.glob("*"):
        assert elemento.is_dir()
        assert elemento.name in ("gare", "screenshots")


@pytest.mark.parametrize("estensione_gara", [".journal", ".json"])
def test_presenza_file_punteggi_per_ogni_file_gara(
    data_dir: pathlib.Path, estensione_gara: str
) -> None:
    """Verifica che ogni file di gara abbia un file punteggi corrispondente."""
    file_trovati = 0
    for file in (data_dir / "gare").rglob(f"*{estensione_gara}"):
        assert file.is_file() or file.is_dir()
        if file.is_file():
            assert file.with_suffix(".score").exists()
            file_trovati += 1
        else:
            raise RuntimeError(f"File non valido: {file}")
    assert file_trovati > 0


def test_presenza_file_gara_per_ogni_file_punteggi(
    data_dir: pathlib.Path,
) -> None:
    """Verifica che ogni file punteggi abbia un file di gara corrispondente."""
    file_trovati = 0
    for file in (data_dir / "gare").rglob("*.score"):
        assert file.is_file() or file.is_dir()
        if file.is_file():
            journal_esiste = file.with_suffix(".journal").exists()
            json_esiste = file.with_suffix(".json").exists()
            assert int(journal_esiste) + int(json_esiste) == 1
            file_trovati += 1
        else:
            raise RuntimeError(f"File non valido: {file}")
    assert file_trovati > 0


def test_cartella_gare_contiene_solo_file_di_gara(
    data_dir: pathlib.Path,
) -> None:
    """Verifica che la cartella contenga solo file .journal, .json e .score."""
    for elemento in (data_dir / "gare").rglob("*"):
        assert elemento.is_file() or elemento.is_dir()
        if elemento.is_file():
            assert elemento.suffix in (".journal", ".json", ".score")
        elif elemento.is_dir():
            pass
        else:
            raise RuntimeError(f"Elemento non valido: {elemento}")


def test_cartella_screenshots_contiene_solo_immagini(
    data_dir: pathlib.Path,
) -> None:
    """Verifica che la cartella contenga solo file .png."""
    for elemento in (data_dir / "screenshots").rglob("*"):
        assert elemento.is_file() or elemento.is_dir()
        if elemento.is_file():
            assert elemento.suffix == ".png"
        elif elemento.is_dir():
            pass
        else:
            raise RuntimeError(f"Elemento non valido: {elemento}")
