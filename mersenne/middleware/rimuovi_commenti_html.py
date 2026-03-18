# Copyright (C) 2024-2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT
"""Middleware che rimuove i commenti HTML <!-- ... --> dalle risposte HTML."""

import re
import typing

import django.http

_COMMENT_RE = re.compile(r"<!--(?!\[if).*?-->", re.DOTALL)


class RimuoviCommentiHTML:
    """
    Middleware che rimuove i commenti HTML dalle risposte HTML.

    Questo middleware rimuove i frammenti `<!-- ... -->` dalle risposte il cui
    header `Content-Type` contiene `text/html`. I commenti condizionali
    tipo `<!--[if ...]> ... <![endif]-->` sono preservati.
    """

    def __init__(
        self,
        get_response: typing.Callable[
            [django.http.HttpRequest], django.http.HttpResponse
        ],
    ) -> None:
        """Inizializza il middleware."""
        self.get_response = get_response

    def __call__(
        self, request: django.http.HttpRequest
    ) -> django.http.HttpResponse:
        """Esegue la richiesta e poi processa la response."""
        response = self.get_response(request)
        return self.process_response(request, response)

    def process_response(
        self,
        request: django.http.HttpRequest,
        response: django.http.HttpResponse,
    ) -> django.http.HttpResponse:
        """
        Rimuove i commenti HTML dalla `response` quando applicabile.

        Restituisce la response originale quando il `Content-Type` non è
        HTML o se la response non è decodificabile in testo.
        """
        content_type = response.get("Content-Type", "")
        if "text/html" not in content_type:
            return response

        # Ottieni il contenuto come bytes; alcune response streaming non
        # espongono `.content` e in quel caso non modifichiamo nulla.
        try:
            raw = response.content
        except AttributeError:
            return response

        # Decodifica usando la charset della response quando presente
        try:
            charset = getattr(response, "charset", None) or "utf-8"
            text = raw.decode(charset)
        except (LookupError, UnicodeDecodeError):
            return response

        new_text = _COMMENT_RE.sub("", text)
        if new_text == text:
            return response

        new_raw = new_text.encode(charset)
        response.content = new_raw
        if response.has_header("Content-Length"):
            response["Content-Length"] = str(len(new_raw))

        return response
