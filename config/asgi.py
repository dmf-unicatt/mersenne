# Copyright (C) 2024-2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT
"""Configurazione ASGI del progetto."""

import os

import django.core.asgi

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
application = django.core.asgi.get_asgi_application()
