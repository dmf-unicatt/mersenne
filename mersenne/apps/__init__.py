# Copyright (C) 2024-2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT
"""Configurazione dell'applicazione mersenne."""

import django.apps


class MersenneConfig(django.apps.AppConfig):  # pragma: no cover
    """AppConfig per l'applicazione mersenne."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "mersenne"
    verbose_name = "mersenne"
