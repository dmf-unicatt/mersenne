# Copyright (C) 2024-2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT
"""Verifica che la forma 'from ... import ...' non è usata nel progetto."""

import ast
import pathlib


def test_from_import() -> None:
    """Verifica che la forma 'from ... import ...' non è usata nel progetto."""
    root_dir = pathlib.Path(__file__).resolve().parents[3]

    for cartella, accetta_file, moduli_ammessi in (
        (
            root_dir / "mersenne",
            lambda f: "migrations" not in f.parts,
            ("mersenne",),
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

                    if modulo.split(".")[0] not in moduli_ammessi:
                        errori.append(
                            f"{file}:{nodo.lineno} -> from {modulo} import ..."
                        )

        assert not errori, (
            "Per favore utilizza 'import module' invece di "
            "'from module import ...' nei seguenti file"
            + (
                f" (ammessi {', '.join(moduli_ammessi)})"
                if len(moduli_ammessi) > 0
                else ""
            )
            + ":\n"
            + "\n".join(errori)
        )
