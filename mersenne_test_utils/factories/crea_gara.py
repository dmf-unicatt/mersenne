# Copyright (C) 2024-2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT
"""Crea una gara di test, senza necessariamente salvarla nel database."""

import typing

import mersenne.models


def crea_gara(
    django_db: bool,
    nome: str,
    num_squadre: int | tuple[int, int] | None = None,
    soluzioni: list[int] | None = None,
    **kwargs: typing.Any,  # noqa: ANN401
) -> tuple[
    mersenne.models.Gara,
    list[mersenne.models.Squadra],
    list[mersenne.models.Problema],
]:
    """
    Crea una gara di test.

    Parameters
    ----------
    django_db
        Se True, la gara viene salvata nel database.
        Se False, viene creata un'istanza di gara senza salvarla.
    nome
        Nome della gara.
    num_squadre
        Il numero di squadre partecipanti.
        Se intero, tutte le squadre saranno considerate non ospiti.
        Se tupla con due componenti, la prima entrata sarà il numero
        di squadre non ospiti, mentre la seconda sarà il numero
        di squadre ospiti.
        Se None, verrà creata una gara con 7 squadre non ospiti e 0 ospiti.
    soluzioni
        Lista delle risposte ai problemi.
        Se None, verranno create 9 soluzioni con risposte predefinite.
    kwargs
        Eventuali altri argomenti, che verranno passati al modello Gara.

    Returns
    -------
    :
        Una tupla contentente l'istanza della gara creata, la lista delle
        squadre partecipanti, e la lista dei problemi della gara.
    """
    if num_squadre is None:
        num_squadre = (7, 0)
    elif isinstance(num_squadre, int):
        num_squadre = (num_squadre, 0)
    if soluzioni is None:
        soluzioni = [123, 456, 789, 100, 200, 300, 400, 500, 600]

    if django_db:
        crea_squadra = mersenne.models.Squadra.objects.create
        crea_problema = mersenne.models.Problema.objects.create
        crea_gara = mersenne.models.Gara.objects.create
    else:
        crea_squadra = mersenne.models.Squadra
        crea_problema = mersenne.models.Problema
        crea_gara = mersenne.models.Gara

    # Crea l'oggetto gara
    gara = crea_gara(nome=nome, **kwargs)

    # Crea squadre partecipanti
    squadre = [
        crea_squadra(
            gara=gara,
            num=i + 1,
            nome=f"Squadra {i + 1}",
            ospite=i >= num_squadre[0],
        )
        for i in range(num_squadre[0] + num_squadre[1])
    ]

    # Crea problemi
    problemi = [
        crea_problema(
            gara=gara,
            num=i + 1,
            nome=f"Problema {i + 1}",
            soluzione=sol,
        )
        for i, sol in enumerate(soluzioni)
    ]

    return gara, squadre, problemi
