# Copyright (C) 2024-2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT
"""Verifica le forme di import usate nel progetto."""

import ast
import pathlib


def test_importa() -> None:
    """
    Verifica il corretto utilizzo delle forme di import nel progetto.

    La forma di import 'from ... import ...' è in generale non ammessa, mentre
    'import ...' è la forma preferita.
    L'unica eccezione sono i moduli 'mersenne' e 'mersenne_test_utils', ma solo
    quando si importa dal modulo stesso. In tal caso è necessario utilizzare
    la forma 'from ... import ...' anziché 'import ...'.
    """
    root_dir = pathlib.Path(__file__).resolve().parents[3]

    for cartella, accetta_file, moduli_interni in (
        (
            root_dir / "mersenne",
            lambda f: "migrations" not in f.parts,
            ("mersenne",),
        ),
        (
            root_dir / "mersenne_test_utils",
            lambda f: True,
            ("mersenne_test_utils",),
        ),
        (root_dir / "tests", lambda f: True, ()),
    ):
        errori = []

        for file in cartella.rglob("*.py"):
            if not accetta_file(file):  # type: ignore[no-untyped-call]
                continue

            albero = ast.parse(file.read_text())

            for nodo in ast.walk(albero):
                if isinstance(nodo, ast.ImportFrom):
                    modulo = nodo.module or ""

                    if modulo.split(".")[0] not in moduli_interni:
                        errori.append(
                            f"{file}:{nodo.lineno} -> from {modulo} import ..."
                        )
                elif isinstance(nodo, ast.Import):
                    for alias in nodo.names:
                        modulo = alias.name.split(".")[0]

                        if modulo in moduli_interni:
                            errori.append(
                                f"{file}:{nodo.lineno} -> import {modulo}"
                            )

        assert not errori, (
            "Forme di import non ammesse trovate nei seguenti file:\n\n".join(
                errori
            )
        )
