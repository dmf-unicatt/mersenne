# Copyright (C) 2024-2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT
"""Modello Gara per la gestione delle competizioni."""

import datetime
import typing

import django.conf
import django.core.exceptions
import django.db.models
import django.utils.timezone


def bonus_problema_default() -> list[int]:
    """Valore di default per il campo bonus_problema."""
    return [20, 15, 10, 8, 6, 5, 4, 3, 2, 1]


def bonus_finale_default() -> list[int]:
    """Valore di default per il campo bonus_finale."""
    return [100, 60, 40, 30, 20, 10, 5, 3, 2, 1]


def validatore_bonus(bonus: typing.Any) -> None:  # noqa: ANN401
    """Valida che il valore sia una lista di interi non negativi."""
    if not isinstance(bonus, list):
        raise django.core.exceptions.ValidationError(
            "Il bonus deve essere una lista."
        )

    for e in bonus:
        if not isinstance(e, int):
            raise django.core.exceptions.ValidationError(
                f"L'elemento {e} non è un intero."
            )
        if e < 0:
            raise django.core.exceptions.ValidationError(
                f"L'elemento {e} è un intero negativo."
            )


class Gara(django.db.models.Model):
    """
    Modello che descrive una gara (gara a squadre).

    Una gara contiene:
    - Informazioni generali (ad esempio: nome, orari, durata)
    - Configurazione dei parametri di gioco (ad esempio: bonus, penalità)
    - Relazioni con i modelli relativi alle squadre e agli eventi
    - Informazioni di accesso (amministratore, inseritori)

    La gara ha uno stato che può essere:
    - Non iniziata (orario_inizio == NULL)
    - In corso (orario_inizio impostato, orario_sospensione == NULL)
    - Sospesa (orario_sospensione impostato)
    - Terminata (ora attuale > orario_fine)
    """

    nome = django.db.models.CharField(
        max_length=200, help_text="Nome della gara"
    )
    orario_inizio = django.db.models.DateTimeField(blank=True, null=True)
    orario_sospensione = django.db.models.DateTimeField(blank=True, null=True)
    durata = django.db.models.DurationField(
        default=datetime.timedelta(hours=2),
        help_text="Durata nel formato hh:mm:ss",
    )
    n_blocco = django.db.models.PositiveSmallIntegerField(
        blank=True,
        default=2,
        null=True,  # il valore NULL non fa bloccare mai il punteggio
        verbose_name="Parametro N (deriva)",
        help_text=(
            "Numero di risposte esatte che bloccano il punteggio di un problema"
        ),
    )
    k_blocco = django.db.models.PositiveSmallIntegerField(
        blank=True,
        default=1,
        null=True,  # il valore NULL fa aumentare sempre il punteggio
        verbose_name="Parametro K",
        help_text=(
            "Numero di risposte errate che aumentano il punteggio "
            "di un problema"
        ),
    )
    durata_blocco = django.db.models.DurationField(
        default=datetime.timedelta(minutes=20),
        help_text=(
            "Il punteggio dei problemi viene bloccato quando "
            "il tempo rimanente è quello indicato in questo campo "
            "nel formato hh:mm:ss"
        ),
    )
    punteggio_iniziale_squadre = django.db.models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name="Punteggio iniziale per squadra",
        help_text=(
            "Se lasciato bianco il punteggio verrà calcolato a partire dalla "
            "moltiplicazione tra il numero di quesiti e la penalità per "
            "risposta errata (senza il segno meno)"
        ),
    )
    penalita_risposta_errata = django.db.models.PositiveSmallIntegerField(
        default=10,
        verbose_name="Penalità per risposta errata",
        help_text="Omettere il segno meno",
    )
    bonus_problema = django.db.models.JSONField(
        default=bonus_problema_default,
        verbose_name="Bonus per ciascun problema",
        validators=[validatore_bonus],
        help_text=(
            "Bonus per le prime squadre che riescono a risolvere un problema"
        ),
    )
    bonus_finale = django.db.models.JSONField(
        default=bonus_finale_default,
        validators=[validatore_bonus],
        help_text=(
            "Bonus per le prime squadre che riescono a risolvere tutti "
            "i problemi",
        ),
    )
    jolly_abilitato = django.db.models.BooleanField(
        default=True, help_text="Possibilità di inserire il jolly"
    )
    scadenza_jolly = django.db.models.DurationField(
        default=datetime.timedelta(minutes=10),
        help_text=(
            "Tempo di scadenza inserimento delle scelte del jolly, "
            "nel formato hh:mm:ss"
        ),
    )
    periodo_incremento_punteggi = django.db.models.DurationField(
        default=datetime.timedelta(minutes=1),
        help_text=(
            "Ogni quanto tempo i punteggi dei problemi aumentano "
            "(a meno che non siano bloccati dai parametri N o K), "
            "nel formato hh:mm:ss"
        ),
    )
    amministratore = django.db.models.ForeignKey(
        "mersenne.Utente",
        on_delete=django.db.models.SET_NULL,
        null=True,
        related_name="+",  # disabilita relazione inversa
    )
    inseritori = django.db.models.ManyToManyField(
        "mersenne.Utente",
        blank=True,
        related_name="+",  # disabilita relazione inversa
    )

    class Meta:
        """Meta class per il modello Gara."""

        verbose_name_plural = "gare"

    @property
    def iniziata(self) -> bool:
        """Verifica se la gara è iniziata."""
        return self.orario_inizio is not None

    @property
    def sospesa(self) -> bool:
        """Verifica se la gara è sospesa."""
        return self.orario_sospensione is not None

    @property
    def terminata(self) -> bool:
        """Verifica se la gara è terminata."""
        if not self.iniziata or self.sospesa:
            return False
        else:
            orario_corrente = django.utils.timezone.now()
            return orario_corrente > self.orario_fine  # type: ignore[operator]

    @property
    def orario_fine(self) -> datetime.datetime | None:
        """Calcola l'orario di fine della gara."""
        if not self.iniziata or self.sospesa:
            return None
        else:
            return self.orario_inizio + self.durata  # type: ignore[operator, return-value]

    @property
    def tempo_rimanente(self) -> datetime.timedelta | None:
        """Calcola il tempo rimanente della gara."""
        if not self.iniziata:
            return None
        elif self.sospesa:
            return self.orario_inizio - self.orario_sospensione + self.durata  # type: ignore[operator]
        else:
            orario_corrente = django.utils.timezone.now()
            if orario_corrente >= self.orario_fine:  # type: ignore[operator]
                return datetime.timedelta(0)
            else:
                return self.orario_fine - orario_corrente  # type: ignore[operator]
