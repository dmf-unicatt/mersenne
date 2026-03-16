# Copyright (C) 2024-2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT
"""Pagina principale dell'applicazione."""

import typing

import django.contrib.messages
import django.http
import django.views.generic


class Index(django.views.generic.TemplateView):
    """Pagina principale dell'applicazione."""

    template_name: str = "mersenne/index.html"

    def get(
        self,
        request: django.http.HttpRequest,
        *args: typing.Any,  # noqa: ANN401
        **kwargs: typing.Any,  # noqa: ANN401
    ) -> django.http.HttpResponse:
        """Esempio di vista che mostra messaggi di prova."""
        django.contrib.messages.error(request, "C'è stato un errore di esempio")
        django.contrib.messages.warning(
            request, "C'è stato un warning di esempio"
        )
        django.contrib.messages.success(
            request, "C'è stato un messaggio di successo di esempio"
        )
        django.contrib.messages.info(
            request, "C'è stato un messaggio informativo di esempio"
        )
        return super().get(request, *args, **kwargs)


index = Index.as_view()
