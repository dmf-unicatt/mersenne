# Copyright (C) 2024-2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT
"""Crea un utente di test, senza necessariamente salvarlo nel database."""

import mersenne.models


def crea_utente(
    django_db: bool,
    username: str,
    email: str | None = None,
    password: str | None = None,
    is_superuser: bool = False,
) -> mersenne.models.Utente:
    """
    Crea un utente di test.

    Parameters
    ----------
    django_db
        Se True, l'utente viene salvato nel database.
        Se False, viene creato un'istanza dell'oggetto utente senza salvarlo.
    username
        Il nome utente dell'utente.
    email
        L'indirizzo email dell'utente.
        Se None, l'indirizzo email verrà dedotto dal nome utente, nel formato
        {username}@mersenne.test.
    password
        La password dell'utente.
        Se None, la password verrà dedotta dal nome utente, nel formato
        password_{username}.
    is_superuser
        Se True, l'utente sarà un amministratore.

    Returns
    -------
    :
        L'istanza dell'utente creato.
    """
    if email is None:
        email = f"{username}@mersenne.test"
    if password is None:
        password = f"password_{username}"

    if django_db:
        _crea_utente = mersenne.models.Utente.objects.create
    else:
        _crea_utente = mersenne.models.Utente

    return _crea_utente(
        username=username,
        email=email,
        password=password,
        is_superuser=is_superuser,
    )
