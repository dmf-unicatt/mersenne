# Copyright (C) 2024-2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT
"""Configurazione delle URL per il progetto."""

import django.contrib.admin
import django.urls

urlpatterns = [
    django.urls.path("admin/", django.contrib.admin.site.urls),
]
