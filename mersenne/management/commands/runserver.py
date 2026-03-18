# Copyright (C) 2024-2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT
"""Comando per eseguire il server in modalità sviluppo o uvicorn."""

import atexit
import os
import pathlib
import signal
import subprocess
import typing

import django.conf
import django.contrib.staticfiles.management.commands.runserver
import django.core.management.base


class Command(django.contrib.staticfiles.management.commands.runserver.Command):
    """
    Comando per eseguire il server in modalità sviluppo o uvicorn.

    In modalità di sviluppo, questo comando avvia sia il server Django
    che il processo npm (Vite) in background. In modalità di produzione,
    invece, avvia uvicorn per eseguire l'app ASGI.
    """

    help = "Esegui il server in modalità sviluppo o uvicorn"

    def add_arguments(
        self, parser: django.core.management.base.CommandParser
    ) -> None:
        """Aggiunge l'argomento opzionale --workers."""
        super().add_arguments(parser)
        parser.add_argument(
            "--workers",
            type=int,
            default=1,
            help="Numero di worker da usare con uvicorn (default: 1)",
        )

    def handle(
        self, *args: tuple[typing.Any, ...], **options: dict[str, typing.Any]
    ) -> None:
        """Esegue il server in base alla valore di DEBUG."""
        DEBUG = django.conf.settings.DEBUG  # noqa: N806
        if DEBUG:
            # Nell'autoreloader di Django vengono creati un processo padre
            # e uno figlio che si occupa di ricaricare il server in caso
            # di modifiche al codice.
            # Il processo padre ha la variabile d'ambiente RUN_MAIN
            # non impostata (cioè None), mentre il processo figlio
            # ha RUN_MAIN impostata a 'true'. Siccome il reload di Django
            # è indipendente dal processo npm, avviamo npm solo nel processo
            # padre.
            run_main = os.environ.get("RUN_MAIN")
            if run_main is not None and run_main.lower() == "true":
                run_npm = False
            else:
                run_npm = True
            if run_npm:
                # Avvia il processo npm (vite) in background
                print("Avvio del processo npm (vite) in background...")
                npm_proc = subprocess.Popen(
                    ["npm", "run", "dev"],
                    cwd=pathlib.Path(__file__).parents[3],
                    preexec_fn=os.setsid,
                )

                # Registra una funzione di cleanup per terminare anche
                # il processo npm quando il server si chiude
                def _stop_npm() -> None:
                    """Termina il processo npm se è ancora in esecuzione."""
                    try:
                        os.killpg(npm_proc.pid, signal.SIGTERM)
                    except Exception:
                        try:
                            npm_proc.terminate()
                        except Exception:
                            pass
            else:
                # Registra una funzione di cleanup vuota quando non
                # si avvia npm. Questo serve perché il blocco "finally:"
                # qui sotto viene eseguito sia nel processo padre
                # sia in quello figlio
                def _stop_npm() -> None:
                    """Funzione di cleanup vuota quando non si avvia npm."""
                    pass

            atexit.register(_stop_npm)

            try:
                super().handle(*args, **options)
            finally:
                _stop_npm()
        else:
            # Avvia uvicorn in modalità produzione. L'import di uvicorn
            # è locale per evitare dipendenza da uvicorn in sviluppo
            import uvicorn

            addrport = options.get("addrport", None)
            if addrport is None:
                addrport = "127.0.0.1:8000"  # type: ignore[assignment]
            assert isinstance(addrport, str)
            host, port = addrport.split(":")
            workers = options["workers"]

            uvicorn.run(
                "config.asgi:application",
                host=host,
                port=int(port),
                workers=workers,
            )
