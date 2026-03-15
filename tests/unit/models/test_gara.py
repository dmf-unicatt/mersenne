# Copyright (C) 2024-2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT
"""Test di unità per il modello Gara."""

import datetime

import django.core.exceptions
import django.utils.timezone
import pytest

import mersenne.models
import mersenne.services.test


def test_creazione_gara() -> None:
    """Verifica la creazione di una gara."""
    gara, squadre, problemi = mersenne.services.test.crea_gara(
        django_db=False,
        nome="Gara di test",
        num_squadre=(2, 1),
        soluzioni=[123, 456, 789, 1000],
    )
    assert gara.pk is None
    assert all(squadra.pk is None for squadra in squadre)
    assert all(problema.pk is None for problema in problemi)
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


def test_gara_amministratore() -> None:
    """Verifica che un utente normale può essere amministratore di una gara."""
    utente = mersenne.services.test.crea_utente(
        django_db=False,
        username="user_test",
        is_superuser=False,
    )
    gara, _, _ = mersenne.services.test.crea_gara(
        django_db=False, nome="Gara di test", amministratore=utente
    )
    assert gara.amministratore == utente


def test_servizio_crea_gara_num_squadre_default() -> None:
    """Verifica il servizio crea_gara con valore di default per num_squadre."""
    _, squadre, _ = mersenne.services.test.crea_gara(
        django_db=False,
        nome="Gara di test",
        num_squadre=None,
    )
    assert len(squadre) == 7
    assert all(not sq.ospite for sq in squadre)


def test_servizio_crea_gara_num_squadre_int() -> None:
    """Verifica il servizio crea_gara con int per num_squadre."""
    _, squadre, _ = mersenne.services.test.crea_gara(
        django_db=False,
        nome="Gara di test",
        num_squadre=3,
    )
    assert len(squadre) == 3
    assert all(not sq.ospite for sq in squadre)


def test_servizio_crea_gara_num_squadre_tupla() -> None:
    """Verifica il servizio crea_gara con tupla per num_squadre."""
    _, squadre, _ = mersenne.services.test.crea_gara(
        django_db=False,
        nome="Gara di test",
        num_squadre=(2, 1),
    )
    assert len(squadre) == 3
    assert not squadre[0].ospite
    assert not squadre[1].ospite
    assert squadre[2].ospite


def test_servizio_crea_gara_soluzioni_default() -> None:
    """Verifica il servizio crea_gara con valore di default per soluzioni."""
    _, _, problemi = mersenne.services.test.crea_gara(
        django_db=False,
        nome="Gara di test",
        soluzioni=None,
    )
    assert len(problemi) == 9
    assert [pb.soluzione for pb in problemi] == [
        123,
        456,
        789,
        100,
        200,
        300,
        400,
        500,
        600,
    ]


def test_servizio_crea_gara_soluzioni_lista() -> None:
    """Verifica il servizio crea_gara con lista per soluzioni."""
    _, _, problemi = mersenne.services.test.crea_gara(
        django_db=False,
        nome="Gara di test",
        soluzioni=[123, 456, 789, 1000],
    )
    assert len(problemi) == 4
    assert [pb.soluzione for pb in problemi] == [123, 456, 789, 1000]


def test_gara_iniziata() -> None:
    """Verifica l'attributo Gara.iniziata per una gara iniziata."""
    orario_corrente = django.utils.timezone.now()
    gara, _, _ = mersenne.services.test.crea_gara(
        django_db=False,
        nome="Gara di test",
        orario_inizio=orario_corrente,
    )
    assert gara.iniziata
    assert not gara.sospesa
    assert not gara.terminata


@pytest.mark.parametrize("iniziata", [True, False])
def test_gara_sospesa(iniziata: bool) -> None:
    """Verifica l'attributo Gara.sospesa per una gara sospesa."""
    orario_corrente = django.utils.timezone.now()
    gara, _, _ = mersenne.services.test.crea_gara(
        django_db=False,
        nome="Gara di test",
        orario_inizio=(
            orario_corrente - datetime.timedelta(minutes=10)
            if iniziata
            else None
        ),
        orario_sospensione=orario_corrente,
    )
    assert gara.iniziata is iniziata
    assert gara.sospesa
    assert not gara.terminata


def test_gara_terminata() -> None:
    """Verifica l'attributo Gara.terminata per una gara terminata."""
    orario_corrente = django.utils.timezone.now()
    gara, _, _ = mersenne.services.test.crea_gara(
        django_db=False,
        nome="Gara di test",
        orario_inizio=orario_corrente - datetime.timedelta(minutes=10),
        durata=datetime.timedelta(minutes=5),
    )
    assert gara.iniziata
    assert not gara.sospesa
    assert gara.terminata


def test_gara_orario_fine_non_iniziata() -> None:
    """Verifica l'attributo Gara.orario_fine per una gara non iniziata."""
    gara, _, _ = mersenne.services.test.crea_gara(
        django_db=False,
        nome="Gara di test",
    )
    assert gara.orario_fine is None


def test_gara_orario_fine_sospesa() -> None:
    """Verifica l'attributo Gara.orario_fine per una gara sospesa."""
    orario_corrente = django.utils.timezone.now()
    gara, _, _ = mersenne.services.test.crea_gara(
        django_db=False,
        nome="Gara di test",
        orario_inizio=orario_corrente - datetime.timedelta(minutes=5),
        orario_sospensione=orario_corrente,
    )
    assert gara.orario_fine is None


def test_gara_orario_fine_iniziata() -> None:
    """Verifica l'attributo Gara.orario_fine per una gara iniziata."""
    orario_corrente = django.utils.timezone.now()
    gara, _, _ = mersenne.services.test.crea_gara(
        django_db=False,
        nome="Gara di test",
        orario_inizio=orario_corrente,
        durata=datetime.timedelta(minutes=5),
    )
    assert gara.orario_fine == orario_corrente + datetime.timedelta(minutes=5)


def test_gara_tempo_rimanente_non_iniziata() -> None:
    """Verifica l'attributo Gara.tempo_rimanente per una gara non iniziata."""
    gara, _, _ = mersenne.services.test.crea_gara(
        django_db=False,
        nome="Gara di test",
    )
    assert gara.tempo_rimanente is None


def test_gara_tempo_rimanente_sospesa() -> None:
    """Verifica l'attributo Gara.orario_fine per una gara sospesa."""
    orario_corrente = django.utils.timezone.now()
    gara, _, _ = mersenne.services.test.crea_gara(
        django_db=False,
        nome="Gara di test",
        orario_inizio=orario_corrente - datetime.timedelta(minutes=7),
        orario_sospensione=orario_corrente - datetime.timedelta(minutes=5),
        durata=datetime.timedelta(minutes=10),
    )
    assert gara.tempo_rimanente == datetime.timedelta(minutes=8)


def test_gara_tempo_rimanente_non_finita() -> None:
    """Verifica l'attributo Gara.tempo_rimanente per una gara non finita."""
    orario_corrente = django.utils.timezone.now()
    gara, _, _ = mersenne.services.test.crea_gara(
        django_db=False,
        nome="Gara di test",
        orario_inizio=orario_corrente - datetime.timedelta(minutes=2),
        durata=datetime.timedelta(minutes=5),
    )
    assert gara.tempo_rimanente <= datetime.timedelta(minutes=3)  # type: ignore[operator]
    assert gara.tempo_rimanente >= datetime.timedelta(minutes=2, seconds=55)  # type: ignore[operator]


def test_gara_tempo_rimanente_finita() -> None:
    """Verifica l'attributo Gara.tempo_rimanente per una gara finita."""
    orario_corrente = django.utils.timezone.now()
    gara, _, _ = mersenne.services.test.crea_gara(
        django_db=False,
        nome="Gara di test",
        orario_inizio=orario_corrente - datetime.timedelta(minutes=10),
        durata=datetime.timedelta(minutes=5),
    )
    assert gara.tempo_rimanente == datetime.timedelta(0)


def test_gara_validazioni_bonus_successo() -> None:
    """Valida con successo i campi bonus problema/finale."""
    gara, _, _ = mersenne.services.test.crea_gara(
        django_db=False,
        nome="Gara di test",
        bonus_problema=[3, 2, 1],
        bonus_finale=[20, 10],
    )
    for campo_str in ("bonus_problema", "bonus_finale"):
        campo = mersenne.models.Gara._meta.get_field(campo_str)
        campo.clean(getattr(gara, campo_str), gara)  # type: ignore[union-attr]


@pytest.mark.parametrize("campo_str", ("bonus_problema", "bonus_finale"))
def test_gara_validazioni_bonus_fallimento_tipo_esterno_errato(
    campo_str: str,
) -> None:
    """Fallimento nella validazione dei campi bonus per tipo esterno errato."""
    gara, _, _ = mersenne.services.test.crea_gara(
        django_db=False,
        nome="Gara di test",
        **{campo_str: (3, 2, 1)},  # type: ignore[arg-type]
    )
    campo = mersenne.models.Gara._meta.get_field(campo_str)
    with pytest.raises(
        django.core.exceptions.ValidationError,
        match="Il bonus deve essere una lista",
    ):
        campo.clean(getattr(gara, campo_str), gara)  # type: ignore[union-attr]


@pytest.mark.parametrize("campo_str", ("bonus_problema", "bonus_finale"))
def test_gara_validazioni_bonus_fallimento_tipo_interno_errato(
    campo_str: str,
) -> None:
    """Fallimento nella validazione dei campi bonus per tipo interno errato."""
    gara, _, _ = mersenne.services.test.crea_gara(
        django_db=False,
        nome="Gara di test",
        **{campo_str: [3.5, 2.6, 1.7]},  # type: ignore[arg-type]
    )
    campo = mersenne.models.Gara._meta.get_field(campo_str)
    with pytest.raises(
        django.core.exceptions.ValidationError,
        match=r"L'elemento 3.5 non è un intero",
    ):
        campo.clean(getattr(gara, campo_str), gara)  # type: ignore[union-attr]


@pytest.mark.parametrize("campo_str", ("bonus_problema", "bonus_finale"))
def test_gara_validazioni_bonus_fallimento_segno_errato(
    campo_str: str,
) -> None:
    """Fallimento nella validazione dei campi bonus per segno errato."""
    gara, _, _ = mersenne.services.test.crea_gara(
        django_db=False,
        nome="Gara di test",
        **{campo_str: [3, -2, 1]},  # type: ignore[arg-type]
    )
    campo = mersenne.models.Gara._meta.get_field(campo_str)
    with pytest.raises(
        django.core.exceptions.ValidationError,
        match="L'elemento -2 è un intero negativo",
    ):
        campo.clean(getattr(gara, campo_str), gara)  # type: ignore[union-attr]
