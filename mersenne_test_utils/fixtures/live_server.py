# Copyright (C) 2024-2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT
"""Fixture per il server Django di test."""

import os
import pathlib
import signal
import socket
import subprocess
import threading
import time
import typing

import django.contrib.staticfiles.handlers
import django.db
import django.test.testcases
import pytest


class LiveServer:  # pragma: no cover
    """
    Classe per la fixture per il server Django di test.

    Questa classe è ispirata alla classe LiveServer di pytest-django,
    ma contiene modifiche per replicare il comportamento impostato nel
    file management/commands/runserver.py, che in modalità di sviluppo avvia
    sia il server Django che il processo npm (Vite) in background, mentre
    in modalità di produzione avvia uvicorn per eseguire l'app ASGI.
    """

    def __init__(self) -> None:
        """Inizializza il server."""
        host = "localhost"

        # Avvia il server in modalità sviluppo o uvicorn a seconda del
        # valore di DEBUG.
        # In modalità sviluppo, avviamo il server Django e vite in background,
        # mentre in modalità di produzione avviamo uvicorn.
        self.DEBUG = django.conf.settings.DEBUG
        if self.DEBUG:
            # Scegli una porta libera per vite
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((host, 0))
                vite_port = s.getsockname()[1]

            # Avvia il processo npm (vite) in background
            self.npm_proc = subprocess.Popen(
                ["node_modules/.bin/vite", "--port", str(vite_port)],
                cwd=pathlib.Path(__file__).parents[2],
                preexec_fn=os.setsid,
            )

            # Esporta la variabile d'ambiente VITE_DEV_SERVER_URL,
            # in modo che il template tag vite possa usarla per includere
            # gli asset dal server di sviluppo di Vite.
            os.environ["VITE_DEV_SERVER_URL"] = f"http://{host}:{vite_port}"

            # Dizionario per le impostazione del server di Django.
            liveserver_kwargs: dict[str, typing.Any] = {}

            # Se il database è in-memory, passiamo le connessioni al thread
            # del server
            connections_override = {}
            for conn in django.db.connections.all():
                # If using in-memory sqlite databases, pass the connections to
                # the server thread.
                if conn.vendor == "sqlite" and conn.is_in_memory_db():  # type: ignore[attr-defined]
                    connections_override[conn.alias] = conn

            liveserver_kwargs["connections_override"] = connections_override

            # Imposta l'handler per i file statici
            liveserver_kwargs["static_handler"] = (
                django.contrib.staticfiles.handlers.StaticFilesHandler
            )

            # Prepara il server Django in un thread separato.
            self._django_thread = django.test.testcases.LiveServerThread(
                host, **liveserver_kwargs
            )
            self._django_thread.daemon = True

            # Marca le connessioni condivise, in modo che non vengano chiuse
            # quando il thread del server viene terminato. Le connessioni
            # condivise sono quelle che usiamo per i database in-memory,
            # che devono rimanere aperte finché il server è in esecuzione.
            for conn in self._django_thread.connections_override.values():
                conn.inc_thread_sharing()

            # Avvia il thread del server e aspetta che sia pronto.
            # Se c'è un errore durante l'avvio, lo segnaliamo e usciamo.
            self._django_thread.start()
            self._django_thread.is_ready.wait()
            if self._django_thread.error:
                error = self._django_thread.error
                self.stop()
                raise error

            # Memorizza l'host e la porta su cui è in ascolto il server
            self._host = self._django_thread.host
            self._port = self._django_thread.port
        else:
            # Avvia uvicorn in modalità produzione. L'import di uvicorn
            # è locale per evitare dipendenza da uvicorn in sviluppo
            import uvicorn

            # Scegli una porta libera per uvicorn
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((host, 0))
                port = s.getsockname()[1]

            # Configura e avvia uvicorn in un thread separato
            config = uvicorn.Config(
                "config.asgi:application", host=host, port=port, workers=1
            )

            self._uvicorn_server = uvicorn.Server(config)

            def _run_uvicorn() -> None:
                """
                Funzione per eseguire uvicorn in un thread separato.

                Questa funzione blocca il thread fino allo shutdown di uvicorn.
                """
                # run() blocca fino allo shutdown
                self._uvicorn_server.run()

            self._uvicorn_thread = threading.Thread(
                target=_run_uvicorn, daemon=True
            )
            self._uvicorn_thread.start()

            # Verifica che il processo uvicorn sia avviato e raggiungibile
            timeout = 10.0
            deadline = time.time() + timeout
            avviato = False
            while time.time() < deadline:
                try:
                    with socket.create_connection((host, port), timeout=0.5):
                        avviato = True
                        break
                except Exception:
                    time.sleep(0.1)
            if not avviato:
                raise RuntimeError(
                    "uvicorn non è riuscito ad avviarsi sulla porta {port} "
                    f"entro {timeout} secondi"
                )

            # Memorizza l'host e la porta su cui è in ascolto uvicorn
            self._host = host
            self._port = port

        # Mock per _live_server_modified_settings, che viene usato
        # dalla fixture _live_server_helper in pytest-django.abs
        # Nei nostri test non è necessario, ma non si può togliere perché
        # la fixture _live_server_helper ha autouse=True e lo chiamerebbe
        self._live_server_modified_settings = MockLiveServerModifiedSettings()

    def stop(self) -> None:
        """Ferma il server."""
        if self.DEBUG:
            # Ferma il server Django
            self._django_thread.terminate()
            # Rimuove la modifica alla condivisione dalle connessioni
            # con i database in-memory
            for conn in self._django_thread.connections_override.values():
                conn.dec_thread_sharing()

            # Ferma il processo npm (vite)
            del os.environ["VITE_DEV_SERVER_URL"]
            try:
                os.killpg(self.npm_proc.pid, signal.SIGTERM)
            except Exception:
                self.npm_proc.terminate()
        else:
            # Ferma il server uvicorn
            self._uvicorn_server.should_exit = True
            self._uvicorn_thread.join(timeout=5)

    @property
    def url(self) -> str:
        """Restituisce l'URL su cui è in ascolto il server HTML."""
        return f"http://{self._host}:{self._port}"

    def __str__(self) -> str:
        """Restituisce la rappresentazione stringa, pari all'URL."""
        return self.url

    def __add__(self, other: str) -> str:
        """Permette di concatenare l'URL del server con un path."""
        return f"{self}{other}"

    def __truediv__(self, other: str) -> str:
        """Permette di concatenare l'URL del server con un path."""
        return f"{self}/{other}"

    def __repr__(self) -> str:
        """Restituisce la rappresentazione stringa per il debug."""
        return f"<LiveServer listening at {self.url}>"


class MockLiveServerModifiedSettings:  # pragma: no cover
    """Classe mock per _live_server_modified_settings."""

    def enable(self) -> None:
        """
        Abilita la modifica delle impostazioni per il live server.

        In realtà, non c'è nessuna modifica da fare, perché il nostro
        LiveServer non modifica le impostazioni di Django, quindi questa
        funzione è vuota.
        """
        pass

    def disable(self) -> None:
        """
        Disabilita la modifica delle impostazioni per il live server.

        In realtà, non c'è nessuna modifica da fare, perché il nostro
        LiveServer non modifica le impostazioni di Django, quindi questa
        funzione è vuota.
        """
        pass


@pytest.fixture(scope="session")
def live_server(
    request: pytest.FixtureRequest,
) -> typing.Generator[LiveServer, None, None]:  # pragma: no cover
    """
    Fai girare un server Django in background durante i test.

    Questa fixture è copiata dalla fixture live_server di pytest-django,
    ma contiene la chiamata alla nostra implementazione di LiveServer,
    anziché a quella di pytest-django.
    """
    server = LiveServer()
    yield server
    server.stop()
