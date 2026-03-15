# Copyright (C) 2024-2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT
"""Configurazione WSGI del progetto."""

import os

import django.core.wsgi

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
application = django.core.wsgi.get_wsgi_application()
