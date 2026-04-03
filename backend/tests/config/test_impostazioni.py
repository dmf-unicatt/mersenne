# Copyright (C) 2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT
"""Verifica le impostazioni lette dalle variabili d'ambiente e dal file .env."""

import pathlib
import typing

import pydantic
import pytest

import mersenne_backend.config
import mersenne_backend.config.impostazioni

ENV_FILE_DEFAULT = pathlib.Path(__file__).parents[3] / ".env"


def crea_impostazioni() -> mersenne_backend.config.Impostazioni:
    """Crea un'istanza di Impostazioni per i test presenti in questo file.

    I test in questo file sovrascrivono le variabili d'ambiente per verificare
    il comportamento della classe Impostazioni, ma con il costruttore normale
    il valore passato a model_config(env_file=...) viene letto dalle variabili
    d'ambiente al momento dell'importazione del modulo, non quelle modificate
    nei test. Per questo motivo, invece di usare il costruttore normale, usiamo
    questa funzione che sovrascrive esplicitamente il valore di env_file con
    quello restituito da una chiamata a _determina_env_file() con le variabili
    d'ambiente correnti.
    """
    return mersenne_backend.config.Impostazioni(
        _env_file=mersenne_backend.config.impostazioni._determina_env_file(),  # ty: ignore[unknown-argument]
    )


def test_determina_env_file_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verifica il file .env utilizzato in assenza di variabili d'ambiente."""
    monkeypatch.delenv("IN_DOCKER", raising=False)
    monkeypatch.delenv("ENV_FILE", raising=False)
    env_file = mersenne_backend.config.impostazioni._determina_env_file()
    assert env_file == "../.env"


def test_determina_env_file_variabile_ambiente(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verifica che la variabile d'ambiente ENV_FILE sovrascriva il default."""
    monkeypatch.delenv("IN_DOCKER", raising=False)
    monkeypatch.setenv("ENV_FILE", "/tmp/.env")
    env_file = mersenne_backend.config.impostazioni._determina_env_file()
    assert env_file == "/tmp/.env"


def test_determina_env_file_in_docker(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verifica che in ambiente Docker il file .env non venga utilizzato."""
    monkeypatch.setenv("IN_DOCKER", "true")
    monkeypatch.setenv("ENV_FILE", "/dev/null")
    env_file = mersenne_backend.config.impostazioni._determina_env_file()
    assert env_file is None


def test_default_env_file_contiene_tutti_i_campi() -> None:
    """Verifica che il file .env di default contenga tutti i campi necessari."""
    campi_presenti: list[str] = []
    with ENV_FILE_DEFAULT.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            campo, _ = line.split("=", 1)
            campi_presenti.append(campo)
    campi_necessari = set(
        mersenne_backend.config.Impostazioni.model_fields.keys()
    )
    assert set(campi_presenti) == campi_necessari, (
        "Il file .env non contiene tutti i campi necessari della classe "
        "Impostazioni. La differenza simmetrica è: "
        + str(set(campi_presenti) ^ campi_necessari)
    )


def test_default_env_file_costruisce_impostazioni_correttamente(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verifica che il file .env di default costruisca le impostazioni."""
    monkeypatch.delenv("IN_DOCKER", raising=False)
    monkeypatch.setenv("ENV_FILE", str(ENV_FILE_DEFAULT))
    impostazioni = crea_impostazioni()
    for campo in mersenne_backend.config.Impostazioni.model_fields.keys():
        assert hasattr(impostazioni, campo)


@pytest.mark.parametrize(
    "IN_DOCKER, sovrascrivi_env_file",
    [
        (None, False),
        (None, True),
        ("false", False),
        ("false", True),
        ("true", False),
        ("true", True),
    ],
)
def test_impostazioni_variabili_ambiente(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: pathlib.Path,
    IN_DOCKER: str | None,  # noqa: N803
    sovrascrivi_env_file: bool,
) -> None:
    """Verifica che le variabili d'ambiente abbiano la precedenza."""
    monkeypatch.delenv("IN_DOCKER", raising=False)
    monkeypatch.delenv("ENV_FILE", raising=False)

    sbagliato: dict[str, typing.Any] = {}
    giusto: dict[str, typing.Any] = {}
    for (
        campo,
        attributi,
    ) in mersenne_backend.config.Impostazioni.model_fields.items():
        if attributi.annotation is str:
            sbagliato[campo] = "sbagliato"
            giusto[campo] = "giusto"
        else:
            raise ValueError(f"Tipo {attributi.annotation} non supportato")

    if IN_DOCKER is not None:
        monkeypatch.setenv("IN_DOCKER", IN_DOCKER)
    if sovrascrivi_env_file:
        ENV_FILE = tmp_path / ".env"  # noqa: N806
        contenuto = ""
        for campo, valore in sbagliato.items():
            contenuto += f"{campo}={valore}\n"
        ENV_FILE.write_text(contenuto)
        monkeypatch.setenv("ENV_FILE", str(ENV_FILE))

    for campo, valore in giusto.items():
        monkeypatch.setenv(campo, valore)

    impostazioni = crea_impostazioni()
    for campo, valore in giusto.items():
        assert getattr(impostazioni, campo) == valore


@pytest.mark.parametrize(
    "IN_DOCKER, sovrascrivi_env, mancante_o_vuoto",
    [
        ("false", None, "mancante"),
        ("false", None, "vuoto"),
        ("false", "file", "mancante"),
        ("false", "file", "vuoto"),
        ("false", "ambiente", "mancante"),
        ("false", "ambiente", "vuoto"),
        ("true", None, "mancante"),
        ("true", None, "vuoto"),
        ("true", "file", "mancante"),
        ("true", "file", "vuoto"),
        ("true", "ambiente", "mancante"),
        ("true", "ambiente", "vuoto"),
    ],
)
def test_impostazioni_campo_mancante(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: pathlib.Path,
    IN_DOCKER: str | None,  # noqa: N803
    sovrascrivi_env: str,
    mancante_o_vuoto: str,
) -> None:
    """Verifica che campi mancanti o vuoti causino un errore di validazione."""
    monkeypatch.delenv("IN_DOCKER", raising=False)
    monkeypatch.delenv("ENV_FILE", raising=False)

    campi = set(mersenne_backend.config.Impostazioni.model_fields.keys())
    for campo in campi:
        monkeypatch.delenv(campo, raising=False)

    if IN_DOCKER is not None:
        monkeypatch.setenv("IN_DOCKER", IN_DOCKER)
    if sovrascrivi_env == "file":
        ENV_FILE = tmp_path / ".env"  # noqa: N806
        if mancante_o_vuoto == "vuoto":
            for campo in campi:
                ENV_FILE.write_text(f"{campo}=\n")
        else:
            assert mancante_o_vuoto == "mancante"
        monkeypatch.setenv("ENV_FILE", str(ENV_FILE))
    elif sovrascrivi_env == "ambiente":
        if mancante_o_vuoto == "vuoto":
            for campo in campi:
                monkeypatch.setenv(campo, "")
        else:
            assert mancante_o_vuoto == "mancante"
        monkeypatch.setenv("ENV_FILE", "/dev/null")
    else:
        assert sovrascrivi_env is None

    atteso_errore = True
    if (
        IN_DOCKER != "true"
        and sovrascrivi_env is None
        and ENV_FILE_DEFAULT.exists()
    ):
        # Se il file .env di default esiste e non lo stiamo né ignorando per
        # via di docker, né sovrascrivendolo con un altro file .env e né
        # sovascrivendolo con le variabili d'ambiente, allora ci aspettiamo
        # che le impostazioni vengano lette correttamente dal file .env di
        # default, e quindi il la creazione dell'istanza di Impostazioni
        # in realtà avrà successo anziché fallire con un errore di validazione.
        atteso_errore = False

    if atteso_errore:
        with pytest.raises(
            expected_exception=pydantic.ValidationError,
            match=r"Field required \[type=missing",
        ):
            crea_impostazioni()
    else:
        crea_impostazioni()
