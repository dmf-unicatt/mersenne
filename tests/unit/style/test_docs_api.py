# Copyright (C) 2024-2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT
"""Verifica la coerenza di docs/api.rst con i moduli della libreria."""

import os
import pathlib


def test_docs_api() -> None:
    """Verifica la coerenza di docs/api.rst con i moduli della libreria."""
    root_dir = pathlib.Path(__file__).parent.parent.parent.parent
    docs_dir = root_dir / "docs"
    source_dir = root_dir / "mersenne"
    # Estrai la lista dei moduli riportati in docs/api.rst
    moduli_in_api_rst = []
    with open(docs_dir / "api.rst") as api_rst_stream:
        for linea in api_rst_stream:
            linea = linea.strip("\n").strip(" ")
            if linea.startswith("mersenne"):
                moduli_in_api_rst.append(linea)
    # Estrai la lista dei moduli esportati dalla libreria
    moduli_in_source_dir = []
    for file in source_dir.rglob("*__init__.py"):
        assert file.is_file()
        if "migrations" in file.parts:
            continue
        moduli_in_source_dir.append(
            str(file.relative_to(root_dir).parent).replace(os.sep, ".")
        )
    # Confronta le due liste
    confronto_moduli = set(moduli_in_api_rst).symmetric_difference(
        moduli_in_source_dir
    )
    assert len(confronto_moduli) == 0, (
        "docs/api.rst non è corente con i moduli presenti nella liberia:"
        f" risultato del confronto {confronto_moduli}"
    )
    # Garantisci che i moduli riportati in docs/api.rst sono ordinati
    # in ordine alfabetico
    moduli_in_api_rst_riordinati = list(sorted(moduli_in_api_rst))
    assert moduli_in_api_rst == moduli_in_api_rst_riordinati, (
        "docs/api.rst non è ordinato in ordine alfabetico."
    )
