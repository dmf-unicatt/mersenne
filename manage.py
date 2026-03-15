#!/usr/bin/env python
# Copyright (C) 2024-2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT
"""Punto di ingresso per i comandi di gestione di Django."""

import os
import sys

import django.core.management


def main() -> None:
    """Esegui i comandi di gestione di Django."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.core.management.execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
