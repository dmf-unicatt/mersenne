# Copyright (C) 2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT
FROM ghcr.io/astral-sh/uv:0.11.2-python3.14-trixie

WORKDIR /mersenne/

ENV PYTHONUNBUFFERED=1

# Compila il bytecode
# Riferimento: https://docs.astral.sh/uv/guides/integration/docker/#compiling-bytecode
ENV UV_COMPILE_BYTECODE=1

# Configura la cache di uv
# Riferimento: https://docs.astral.sh/uv/guides/integration/docker/#caching
ENV UV_LINK_MODE=copy

# Metti gli eseguibili dell'ambiente virtuale all'inizio del PATH
# Riferimento: https://docs.astral.sh/uv/guides/integration/docker/#using-the-environment
ENV PATH="/mersenne/.venv/bin:$PATH"

# Installa le dipendenze con cache e lock file montati dal context.
# Nota che facciamo un uv sync senza installare il workspace in modo da
# sfruttare la cache di docker e di uv per non dover reinstallare tutte
# le dipendenze ogni volta che cambiamo il codice del backend
# Riferimento: https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers
RUN --mount=type=cache,id=mersenne-uv-cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=backend/pyproject.toml,target=backend/pyproject.toml \
    uv sync --frozen --no-install-workspace

# Installa il backend
# Il comando è praticamente un copia-incolla di quello precedente, ma con
# la differenza che ora installiamo anche il workspace
RUN --mount=type=cache,id=mersenne-uv-cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=backend,target=backend \
    uv sync --frozen

# Copia il punto di ingresso dell'applicazione
# Nota che
# 1) non abbiamo bisogno di copiare tutto il codice del backend, ma solo
#    il punto di ingresso, perché il backend è già installato nell'ambiente
#    virtuale
# 2) grazie all'esportazione del PATH, è meglio usare "poe deploy" invece di
#    "uv run poe deploy", in quanto la seconda versione potrebbe reinstallare
#    tutte le dipendenze in /mersenne/backend/.venv (mentre attualmente sono
#    già installate in /mersenne/.venv) per via del campio di WORKDIR qui sotto
WORKDIR /mersenne/backend
COPY ./backend/main.py /mersenne/backend/main.py
COPY ./backend/pyproject.toml /mersenne/backend/pyproject.toml
CMD ["poe", "deploy"]
