# Copyright (C) 2024-2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT
"""Modello per la gestione degli utenti del sistema."""

import django.contrib.auth.models
import django.db.models


class Utente(django.contrib.auth.models.AbstractUser):
    """
    Modello che descrive un utente del sistema.

    Eredita da AbstractUser di Django senza aggiungere alcuna funzionalità.
    Questa scelta è fatta per mantenere flessibilità in futuro.
    """

    pass
