# Copyright (C) 2024-2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT

ARG VERSIONE_DEBIAN=latest
FROM debian:${VERSIONE_DEBIAN}

ARG VERSIONE_DEBIAN

WORKDIR /root

## Parte 1: installa dipendenze da apt

# Installa utilità di base
RUN apt update -y -q && \
    apt install -y -qq curl git net-tools python3-pip sudo unzip vim wget

# Personalizza il colore del prompt della shell per mettere in evidenza
# che l'utente sta eseguendo comandi nel contenitore Docker
RUN echo 'PS1='"'"'\[\e]0;\u@\h: \w\a\]${debian_chroot:+($debian_chroot)}\[\033[01;38;5;27m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\$\[\033[00m\] '"'"'' >> /root/.bashrc && \
    echo "alias ls='ls --color=auto'"  >> /root/.bashrc && \
    echo "alias ll='ls -l'"  >> /root/.bashrc

# Permetti l'installazione di pacchetti Python a livello di sistema tramite pip
RUN rm /usr/lib/python3.*/EXTERNALLY-MANAGED

# Installa dipendenze per database
RUN apt install -y -qq libpq-dev postgresql postgresql-client postgresql-contrib python3-psycopg2

# L'installazione di postgres crea un nuovo utente; concedi a questo utente
# di accedere in sola lettura a /root
RUN chmod go+rx /root

# Installa dipendenze per la gestione dei file statici
RUN apt install -y -qq npm

# Installa dipendenze per browser
RUN python3 -m pip install playwright && \
    if [ "$VERSIONE_DEBIAN" = "13" ]; then \
        playwright install-deps; \
    elif [ "$VERSIONE_DEBIAN" = "testing" ] || [ "$VERSIONE_DEBIAN" = "unstable" ]; then \
        playwright install-deps --dry-run | sed "s/libasound2 //g" | sed "s/libxml2 /libxml2-16 /g" | bash -eux -; \
    else \
        echo "Versione di Debian non riconosciuta: $VERSIONE_DEBIAN. Non posso installare le dipendenze per Playwright."; \
    fi && \
    apt install -y -qq fonts-noto && \
    playwright install

## Parte 2: installazione di mersenne

COPY . .

RUN python3 -m pip install .[lint,tests] && \
    rm -rf build dist *.egg-info && \
    npm install && \
    npm run build

ENV DJANGO_SETTINGS_MODULE="config.settings"

## Parte 3: configurazione dell'entrypoint

RUN mv docker/_entrypoint.sh /usr/local/bin/docker-entrypoint.sh && \
    chmod +x /usr/local/bin/docker-entrypoint.sh && \
    rmdir docker
ENTRYPOINT ["docker-entrypoint.sh"]
