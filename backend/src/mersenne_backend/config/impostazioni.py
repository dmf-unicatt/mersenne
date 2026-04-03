# Copyright (C) 2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT
"""Configurazione dell'applicazione tramite variabili d'ambiente."""

import os
import typing

import pydantic
import pydantic_settings


def _determina_env_file() -> str | None:
    """Determina il percorso del file .env da caricare."""
    in_docker = os.getenv("IN_DOCKER", "false") == "true"
    return os.getenv("ENV_FILE", "../.env") if not in_docker else None


class Impostazioni(pydantic_settings.BaseSettings):
    """Impostazioni dell'applicazione lette dalle variabili d'ambiente.

    Tutti i campi devono essere definiti e non vuoti, riempiti o da variabili
    d'ambiente o da file .env. La notazione '= pydantic.Field(default=...)' che
    è presente in tutti i campi non imposta davvero un default, ma è un modo
    di aggirare il supporto limitato di type checker come ty, che altrimenti
    segnelarebbero un errore ogni volta che che viene istanziata la classe
    Impostazioni senza passare esplicitamente un valore per ogni campo.
    In realtà, se un campo è definito ma non è presente nelle variabili
    d'ambiente o nel file .env, o se è presente ma è vuoto, pydantic solleverà
    un errore di validazione.
    Riferimenti per la notazione '= pydantic.Field(default=...)':
    - https://github.com/astral-sh/ty/issues/1070
    - https://github.com/astral-sh/ty/issues/2130
    - https://github.com/pydantic/pydantic-settings/issues/201
    """

    model_config = pydantic_settings.SettingsConfigDict(
        # Quando non siamo in Docker (cioè, stiamo sviluppando l'applicazione
        # direttamente dall'host senza passare per Docker) è necessario
        # caricare le variabili d'ambiente dal file .env che si trova
        # nella directory principale del progetto.
        # Invece, quando siamo dentro Docker non vogliamo caricare nessun file
        # .env perché le variabili d'ambiente sono già esplicitamente passate
        # al container tramite il file compose.yml.
        env_file=_determina_env_file(),
        # Se una variabile d'ambiente o una configurazione letta da un file
        # .env è definita ma è vuota, ignorala.
        env_ignore_empty=True,
        # Se una configurazione letta da un file .env è definita ma non è tra
        # i campi definiti nella classe Impostazioni, solleva un errore.
        extra="forbid",
    )

    # Configurazione del database PostgreSQL
    UTENTE_POSTGRES: typing.Annotated[
        str,
        pydantic.StringConstraints(min_length=1),
        pydantic.Field(description="Nome utente per il database PostgreSQL."),
    ] = pydantic.Field(default=...)
    PASSWORD_POSTGRES: typing.Annotated[
        str,
        pydantic.StringConstraints(min_length=1),
        pydantic.Field(description="Password per il database PostgreSQL."),
    ] = pydantic.Field(default=...)
    DATABASE_POSTGRES: typing.Annotated[
        str,
        pydantic.StringConstraints(min_length=1),
        pydantic.Field(description="Nome del database PostgreSQL."),
    ] = pydantic.Field(default=...)

    # Configurazione di Redis
    PASSWORD_REDIS: typing.Annotated[
        str,
        pydantic.StringConstraints(min_length=1),
        pydantic.Field(description="Password per Redis."),
    ] = pydantic.Field(default=...)
