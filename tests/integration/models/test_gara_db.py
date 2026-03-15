# Copyright (C) 2024-2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT
"""Test di unità per il modello Gara."""

import pytest

import mersenne.models
import mersenne.services.test


@pytest.mark.django_db
def test_creazione_gara_db() -> None:
    """
    Verifica la creazione di una gara.

    I controlli sulle relazioni inverse necessitano di un database attivo.
    """
    gara, squadre, problemi = mersenne.services.test.crea_gara(
        django_db=True,
        nome="Gara di test",
        num_squadre=(2, 1),
        soluzioni=[123, 456, 789, 1000],
    )
    assert gara.pk is not None
    assert all(squadra.pk is not None for squadra in squadre)
    assert all(problema.pk is not None for problema in problemi)
    assert len(squadre) == 3
    assert squadre[0].num == 1
    assert squadre[1].num == 2
    assert squadre[2].num == 3
    assert squadre[0].nome == "Squadra 1"
    assert squadre[1].nome == "Squadra 2"
    assert squadre[2].nome == "Squadra 3"
    assert not squadre[0].ospite
    assert not squadre[1].ospite
    assert squadre[2].ospite
    for sq in squadre:
        assert sq.gara == gara
    assert len(problemi) == 4
    assert problemi[0].num == 1
    assert problemi[1].num == 2
    assert problemi[2].num == 3
    assert problemi[3].num == 4
    assert problemi[0].nome == "Problema 1"
    assert problemi[1].nome == "Problema 2"
    assert problemi[2].nome == "Problema 3"
    assert problemi[3].nome == "Problema 4"
    assert problemi[0].soluzione == 123
    assert problemi[1].soluzione == 456
    assert problemi[2].soluzione == 789
    assert problemi[3].soluzione == 1000
    for pb in problemi:
        assert pb.gara == gara


@pytest.mark.django_db
def test_gara_amministratore_inseritori_db() -> None:
    """
    Verifica assegnamento di amministratori e inseritori.

    Il campo inseritori, che è di tipo ManyToManyField, necessita
    di un database attivo per essere popolato.
    """
    amministratore = mersenne.services.test.crea_utente(
        django_db=True,
        username="admin_test",
        is_superuser=False,
    )
    utente1 = mersenne.services.test.crea_utente(
        django_db=True,
        username="user1_test",
        is_superuser=False,
    )
    utente2 = mersenne.services.test.crea_utente(
        django_db=True,
        username="user2_test",
        is_superuser=False,
    )
    gara, _, _ = mersenne.services.test.crea_gara(
        django_db=True, nome="Gara di test", amministratore=amministratore
    )
    gara.inseritori.set([utente1, utente2])
    assert gara.amministratore == amministratore
    assert len(gara.inseritori.all()) == 2
    assert list(gara.inseritori.all()) == [utente1, utente2]
