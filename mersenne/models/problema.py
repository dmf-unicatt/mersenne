# Copyright (C) 2024-2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT
"""Modello che descrive un problema di gara."""

import django.core.validators
import django.db.models


class Problema(django.db.models.Model):
    """Modello che descrive un problema di una gara."""

    gara = django.db.models.ForeignKey(
        "mersenne.Gara",
        on_delete=django.db.models.CASCADE,
        related_name="problemi",
    )
    num = django.db.models.PositiveSmallIntegerField(
        verbose_name="Numero", help_text="Identificativo del problema"
    )
    nome = django.db.models.CharField(
        max_length=200, blank=True, null=True, help_text="Titolo del problema"
    )
    soluzione = django.db.models.PositiveSmallIntegerField(
        default=0,
        validators=[django.core.validators.MaxValueValidator(9999)],
        help_text="Soluzione del problema",
    )
    punteggio = django.db.models.PositiveSmallIntegerField(
        default=20, help_text="Punteggio iniziale del problema"
    )

    class Meta:
        """Meta class per il modello Problema."""

        verbose_name_plural = "problemi"
        ordering = (
            "gara",
            "num",
        )
        constraints = (
            django.db.models.CheckConstraint(
                condition=django.db.models.Q(num__gte=1),
                name="problema_num_gte_1",
            ),
            django.db.models.UniqueConstraint(
                fields=["gara", "num"], name="problema_unique_gara_num"
            ),
        )
