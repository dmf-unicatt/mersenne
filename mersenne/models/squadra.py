# Copyright (C) 2024-2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT
"""Modello che descrive una squadra che partecipa ad una gara."""

import django.db.models


class Squadra(django.db.models.Model):
    """Modello che descrive una squadra che partecipa ad una gara."""

    gara = django.db.models.ForeignKey(
        "mersenne.Gara",
        on_delete=django.db.models.CASCADE,
        related_name="squadre",
    )
    num = django.db.models.PositiveSmallIntegerField(
        verbose_name="Numero", help_text="Identificativo della squadra"
    )
    nome = django.db.models.CharField(
        max_length=200, help_text="Nome della squadra"
    )
    ospite = django.db.models.BooleanField(
        default=False, help_text="Squadra ospite"
    )

    class Meta:
        """Meta class per il modello Squadra."""

        verbose_name_plural = "squadre"
        ordering = (
            "gara",
            "num",
        )
        constraints = (
            django.db.models.CheckConstraint(
                condition=django.db.models.Q(num__gte=1),
                name="squadra_num_gte_1",
            ),
            django.db.models.UniqueConstraint(
                fields=["gara", "num"], name="squadra_unique_gara_num"
            ),
        )
