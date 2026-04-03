# Copyright (C) 2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT
"""Verifica le forme di import usate nel progetto."""

import ast
import pathlib


def verifica_stile_import(
    nome_file: str, sorgente: str, forma_preferita: dict[str, str]
) -> list[str]:
    """Verifica che la forma di import usata sia quella preferita."""
    albero = ast.parse(sorgente, filename=nome_file)
    errori: list[str] = []

    for nodo in ast.walk(albero):
        if isinstance(nodo, ast.ImportFrom):
            modulo = nodo.module
            assert modulo is not None, (
                "Hai forse usato un import relativo? Usa invece "
                "un import assoluto."
            )
            stile_atteso = forma_preferita.get(
                modulo.split(".")[0], forma_preferita["*"]
            )
            stile_effettivo = "from ... import ..."

            if stile_effettivo != stile_atteso:
                errori.append(
                    f"{nome_file}:{nodo.lineno} -> "
                    f"devi usare 'import {modulo}' invece di "
                    f"'from {modulo} import ...'"
                )
        elif isinstance(nodo, ast.Import):
            for alias in nodo.names:
                modulo = alias.name

                stile_atteso = forma_preferita.get(
                    modulo.split(".")[0], forma_preferita["*"]
                )
                stile_effettivo = "import ..."

                if stile_effettivo != stile_atteso:
                    errori.append(
                        f"{nome_file}:{nodo.lineno} -> "
                        f"devi usare 'from {modulo} import ...' "
                        f"invece di 'import {modulo}'"
                    )

    return errori


def test_verifica_stile_import_solo_forma_from_import() -> None:
    """Verifica sorgenti che contengono 'from ... import ...'."""
    sorgente = """\
from modulo1 import oggetto
from modulo2 import altro_oggetto
from modulo2.sottomodulo import terzo_oggetto
"""
    nome_file = "test_verifica_stile_import_solo_forma_from_import.py"

    forma_preferita = {"*": "from ... import ..."}
    errori = verifica_stile_import(nome_file, sorgente, forma_preferita)
    assert len(errori) == 0

    forma_preferita = {"*": "import ..."}
    errori = verifica_stile_import(nome_file, sorgente, forma_preferita)
    assert len(errori) == 3
    assert errori[0] == (
        f"{nome_file}:1 -> devi usare 'import modulo1' invece di "
        "'from modulo1 import ...'"
    )
    assert errori[1] == (
        f"{nome_file}:2 -> devi usare 'import modulo2' invece di "
        "'from modulo2 import ...'"
    )
    assert errori[2] == (
        f"{nome_file}:3 -> devi usare 'import modulo2.sottomodulo' invece di "
        "'from modulo2.sottomodulo import ...'"
    )


def test_verifica_stile_import_solo_forma_import() -> None:
    """Verifica sorgenti che contengono 'import ...'."""
    sorgente = """\
import modulo1
import modulo2
import modulo2.sottomodulo
"""
    nome_file = "test_verifica_stile_import_solo_forma_import.py"

    forma_preferita = {"*": "import ..."}
    errori = verifica_stile_import(nome_file, sorgente, forma_preferita)
    assert len(errori) == 0

    forma_preferita = {"*": "from ... import ..."}
    errori = verifica_stile_import(nome_file, sorgente, forma_preferita)
    assert len(errori) == 3
    assert errori[0] == (
        f"{nome_file}:1 -> devi usare 'from modulo1 import ...' invece di "
        "'import modulo1'"
    )
    assert errori[1] == (
        f"{nome_file}:2 -> devi usare 'from modulo2 import ...' invece di "
        "'import modulo2'"
    )
    assert errori[2] == (
        f"{nome_file}:3 -> devi usare 'from modulo2.sottomodulo import ...' "
        "invece di 'import modulo2.sottomodulo'"
    )


def test_verifica_stile_import_misto_forme() -> None:
    """Verifica sorgenti che contengono entrambe le forme di import."""
    sorgente = """\
import os

import modulo1
from modulo2 import altro_oggetto
from modulo2.sottomodulo import terzo_oggetto
"""
    nome_file = "test_verifica_stile_import_misto_forme.py"

    forma_preferita = {
        "*": "import ...",
        "modulo1": "import ...",
        "modulo2": "from ... import ...",
    }
    errori = verifica_stile_import(nome_file, sorgente, forma_preferita)
    assert len(errori) == 0

    forma_preferita = {
        "*": "import ...",
        "modulo1": "from ... import ...",
        "modulo2": "from ... import ...",
    }
    errori = verifica_stile_import(nome_file, sorgente, forma_preferita)
    assert len(errori) == 1
    assert errori[0] == (
        f"{nome_file}:3 -> devi usare 'from modulo1 import ...' invece di "
        "'import modulo1'"
    )

    forma_preferita = {
        "*": "import ...",
        "modulo1": "import ...",
        "modulo2": "import ...",
    }
    errori = verifica_stile_import(nome_file, sorgente, forma_preferita)
    assert len(errori) == 2
    assert errori[0] == (
        f"{nome_file}:4 -> devi usare 'import modulo2' invece di "
        "'from modulo2 import ...'"
    )
    assert errori[1] == (
        f"{nome_file}:5 -> devi usare 'import modulo2.sottomodulo' invece di "
        "'from modulo2.sottomodulo import ...'"
    )


def test_cartella_backend() -> None:
    """Verifica il corretto utilizzo delle forme di import nel backend.

    La forma di import 'from ... import ...' è in generale non ammessa,
    in favore della forma 'import ...'.
    L'unica eccezione sono i file __init__.py dei moduli di mersenne_backend.
    In tal caso è necessario utilizzare la forma 'from ... import ...'
    anziché 'import ...', in modo che sia possibile esportino correttamente
    il contenuto dei sottomoduli.
    """
    root_dir = pathlib.Path(__file__).resolve().parents[2]

    for cartella, accetta_file, forma_preferita in (
        (
            root_dir / "mersenne",
            lambda f: "__init__.py" not in f.parts,
            {"*": "import ...", "mersenne": "import ..."},
        ),
        (
            root_dir / "mersenne",
            lambda f: "__init__.py" in f.parts,
            {"*": "import ...", "mersenne": "from ... import ..."},
        ),
        (root_dir / "tests", lambda _f: True, {"*": "import ..."}),
    ):
        errori = []

        for file in cartella.rglob("*.py"):
            if not accetta_file(file):  # type: ignore[no-untyped-call]
                continue

            errori.extend(
                verifica_stile_import(
                    str(file), file.read_text(), forma_preferita
                )
            )

        assert len(errori) == 0, (
            "Forme di import non ammesse trovate nei seguenti file:\n\n\n".join(
                errori
            )
        )
