# Copyright (C) 2024-2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT
"""Pacchetto con gli URL dell'applicazione."""

import django.urls

from mersenne import views

urlpatterns = [
    django.urls.path("", views.index, name="index"),
]
