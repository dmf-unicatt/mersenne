# Copyright (C) 2024-2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT
"""Comando per la creazione di un utente (normale)."""

import os
import typing

import django.contrib.auth
import django.core.management.base


class Command(django.core.management.base.BaseCommand):
    """Comando per la creazione di un utente (normale)."""

    help = "Crea un utente (normale)."

    def add_arguments(
        self, parser: django.core.management.base.CommandParser
    ) -> None:
        """Aggiunge argomenti al comando."""
        parser.add_argument("--username", type=str)
        parser.add_argument("--email", type=str)
        parser.add_argument("--password", type=str)
        parser.add_argument(
            "--no-input",
            action="store_true",
            help="Crea un utente usando variabili d'ambiente.",
        )

    def handle(self, *args: typing.Any, **options: typing.Any) -> None:  # noqa: ANN401
        """Esegue il comando."""
        Utente = django.contrib.auth.get_user_model()  # noqa: N806

        if options["no_input"]:
            username = os.environ.get("DJANGO_USER_USERNAME")
            email = os.environ.get("DJANGO_USER_EMAIL")
            password = os.environ.get("DJANGO_USER_PASSWORD")

            if not username or not password:
                raise django.core.management.base.CommandError(
                    "Mancano DJANGO_USER_USERNAME e DJANGO_USER_PASSWORD"
                )
        else:
            username = options["username"] or input("Username: ")
            email = options["email"] or input("Email: ")
            password = options["password"] or input("Password: ")

        if Utente.objects.filter(username=username).exists():
            raise django.core.management.base.CommandError(
                f"L'utente {username} esiste già."
            )
        else:
            utente = Utente.objects.create_user(
                username=username,
                email=email,
                password=password,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Utente '{utente.username}' creato con successo"
                )
            )
