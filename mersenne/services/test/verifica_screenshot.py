# Copyright (C) 2024-2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT
"""Restituisce una fixture per creare e verificare uno screenshot."""

import os
import pathlib
import shutil
import typing

import PIL.Image
import PIL.ImageChops
import playwright.sync_api
import pytest


class VerificaScreenshotType(typing.Protocol):
    """Protocollo per la funzione di verifica dello screenshot."""

    def __call__(
        self,
        target: playwright.sync_api.Page | playwright.sync_api.ElementHandle,
        max_diff_ratio: float = 0.001,
        cleanup: bool = True,
    ) -> None:
        """Crea uno screenshot del target e lo confronta con quello atteso."""
        ...


@pytest.fixture
def verifica_screenshot(
    request: pytest.FixtureRequest,
) -> VerificaScreenshotType:  # pragma: no cover
    """
    Fornisce una funzione per creare e verificare screenshot.

    Legge lo screenshot atteso da `data_dir/screenshots/<nome_file_test>_py/`
    con nome `<nome_test>[_<contatore>].png`. Se il file non esiste,
    viene creato e il test restituisce un errore.

    Effettua un confronto tra lo screenshot atteso e quello ottenuto nel testo.
    In caso di differenze maggiori di `max_diff_pixels`, viene salvato anche
    un file di diff in `tests/browser/<nome_file_test>_py/` con le differenze
    evidenziate in rosso.
    """
    # Determina il percorso della cartella principale del repository
    repo_root = pathlib.Path(__file__).parents[3]
    # Determina il percorso del file di test
    test_path = request.path.resolve()
    test_dir_name = test_path.relative_to(
        repo_root / "tests" / "browser"
    ).parent
    test_file_stem = test_path.stem + "_py"
    current_dir = test_path.parent
    # Determina la cartella per lo screenshot atteso
    baseline_dir = (
        repo_root
        / "data"
        / "screenshots"
        / "tests"
        / "browser"
        / test_dir_name
        / test_file_stem
    )
    baseline_dir.mkdir(parents=True, exist_ok=True)

    def _(
        target: playwright.sync_api.Page | playwright.sync_api.ElementHandle,
        max_diff_ratio: float = 0.001,
        cleanup: bool = True,
    ) -> None:
        """Crea uno screenshot del target e lo confronta con quello atteso."""
        # Determina i nomi dei file per lo screenshot atteso, quello corrente
        # e quello di diff
        counter_attr = "_screenshot_counter"
        counter = getattr(request.node, counter_attr, 0) + 1
        setattr(request.node, counter_attr, counter)
        basename = f"{request.node.name}_{counter}"
        baseline_path = baseline_dir / f"{basename}.png"
        current_path = current_dir / f"{basename}.png"
        diff_path = current_dir / f"{basename}_diff.png"
        # Salva lo screenshot corrente
        if isinstance(target, playwright.sync_api.Page):
            target.screenshot(path=str(current_path), full_page=True)
        elif isinstance(target, playwright.sync_api.ElementHandle):
            target.screenshot(path=str(current_path))
        else:
            raise TypeError(
                "Impossibile creare lo screenshot: target deve essere "
                "di tipo Page o ElementHandle."
            )
        # Se lo screenshot di riferimento non esiste, copia quello appena
        # creato e fallisci il test
        if not baseline_path.exists():  # pragma: no cover
            shutil.copy(current_path, baseline_path)
            if cleanup:
                os.remove(current_path)
            raise RuntimeError(f"Creato nuovo screenshot: {baseline_path}")
        else:
            # Altrimenti fai un confronto tra lo screenshot atteso
            # e quello effettivo
            with (
                PIL.Image.open(baseline_path) as a,
                PIL.Image.open(current_path) as b,
            ):
                if a.size != b.size:
                    raise AssertionError(
                        "Le dimensioni dello screenshot differiscono: "
                        f"atteso {a.size}, ottenuto {b.size}"
                    )
                else:
                    diff = PIL.ImageChops.difference(
                        a.convert("RGBA"), b.convert("RGBA")
                    )
                    diff_gray = diff.convert("L")
                    hist = diff_gray.histogram()
                    non_zero = sum(hist[1:])
                    if non_zero > max_diff_ratio * a.size[0] * a.size[1]:
                        mask = diff.convert("L").point(
                            lambda x: 255 if x > 0 else 0
                        )
                        overlay = a.copy()
                        overlay.paste((255, 0, 0), mask=mask)
                        overlay.save(diff_path)
                        raise AssertionError(
                            f"Gli screenshot differiscono di {non_zero} pixels "
                            f"(> {max_diff_ratio * a.size[0] * a.size[1]}), "
                            "controlla il file con la loro differenza: "
                            f"{diff_path}"
                        )
                    else:
                        if cleanup:
                            os.remove(current_path)

    return _
