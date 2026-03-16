#!/bin/bash
# Copyright (C) 2024-2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT

set -e
set -u

# Versione di postgres installata
VERSIONE_POSTGRES=$(pg_config --version | awk '{print $2}' | cut -d. -f1)

## Parte 1: preparazione delle cartelle

# Cartelle dati persistenti
# (con /mnt montata come volume, quindi persistenti alla creazione
#  di un nuovo container)
CARTELLA_POSTGRES=/mnt/postgress
CARTELLA_SEGRETI=/mnt/segreti
CARTELLA_PROGRESSO_CONDIVISA=/mnt/progresso

# Cartelle dati temporanei
# (non montati come volume, quindi persi alla creazione di un nuovo container)
CARTELLA_PROGRESSO_LOCALE=/state/progresso

# Crea le cartelle dati, se non esistono
mkdir -p ${CARTELLA_POSTGRES}
mkdir -p ${CARTELLA_SEGRETI}
mkdir -p ${CARTELLA_PROGRESSO_LOCALE}
mkdir -p ${CARTELLA_PROGRESSO_CONDIVISA}

## Parte 2: preparazione del database postgres

# Imposta il nome database postgres
NOME_DATABASE_POSTGRES="mersenne-db"
if [[ "${NOME_DATABASE_POSTGRES}" != *"-db" ]]; then
    echo "Il nome del database ${NOME_DATABASE_POSTGRES} dovrebbe terminare " \
         "con -db"
    exit 1
fi

# Imposta il nome cluster postgres
NOME_CLUSTER_POSTGRES=${NOME_DATABASE_POSTGRES/-db/-cluster}
if [[ "${NOME_CLUSTER_POSTGRES}" != *"-cluster" ]]; then
    echo "Il nome del cluster ${NOME_CLUSTER_POSTGRES} dovrebbe terminare " \
         "con -cluster"
    exit 1
fi

# Genera una password per l'utente postgres
FILE_PASSWORD_UTENTE_POSTGRES="${CARTELLA_SEGRETI}/password_utente_postgres"
if [[ ! -f "${FILE_PASSWORD_UTENTE_POSTGRES}" ]]; then
    echo "Generazione di una password per l'utente postgres"
    PASSWORD_UTENTE_POSTGRES=$(cat /dev/urandom | tr -dc 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789' | head -c 50; echo)
    PASSWORD_UTENTE_POSTGRES=${PASSWORD_UTENTE_POSTGRES} sh -c "echo '${PASSWORD_UTENTE_POSTGRES}\n${PASSWORD_UTENTE_POSTGRES}' | passwd postgres"
    echo ${PASSWORD_UTENTE_POSTGRES} > ${FILE_PASSWORD_UTENTE_POSTGRES}
else
    echo "Riutilizzo della password esistente per l'utente postgres"
    PASSWORD_UTENTE_POSTGRES=$(cat "${FILE_PASSWORD_UTENTE_POSTGRES}")
fi

# Crea un nuovo cluster postgres.
# Nota: il cluster postgres va ricreato in ogni contenitore, anche se la
#       cartella che contiene i dati è montata su un volume condiviso tra più
#       contenitori!
#       Per questo motivo il file di progresso viene salvato nella cartella
#       ${CARTELLA_PROGRESSO_LOCALE} anziché quella condivisa
#       ${CARTELLA_PROGRESSO_CONDIVISA}
FILE_CLUSTER_POSTGRES_CREATO=${CARTELLA_PROGRESSO_LOCALE}/cluster_postgres_creato
if [[ ! -f ${FILE_CLUSTER_POSTGRES_CREATO} ]]; then
    echo "Creazione di un nuovo cluster postgres"
    pg_dropcluster ${VERSIONE_POSTGRES} main || true
    pg_createcluster ${VERSIONE_POSTGRES} --datadir=${CARTELLA_POSTGRES} ${NOME_CLUSTER_POSTGRES} -- -E UTF8 --locale=C.utf8 --lc-messages=C
    cp /etc/postgresql/${VERSIONE_POSTGRES}/${NOME_CLUSTER_POSTGRES}/*.conf ${CARTELLA_POSTGRES}/ || true
    touch ${FILE_CLUSTER_POSTGRES_CREATO}
else
    echo "Riutilizzo del cluster postgres esistente"
fi

# Avvia il servizio postgresql
echo "Avvio del servizio postgresql"
service postgresql start

# Inizializza il database postgres, se necessario
# Nota: il database va inizializzato solo una volta, e non va creato nuovamente
#       se viene utilizzato in un contenitore diverso da quello che l'ha creato.
#       Per questo motivo il file di progresso viene salvato nella cartella
#       ${CARTELLA_PROGRESSO_CONDIVISA} montata sul volume anziché nella cartella
#       ${CARTELLA_PROGRESSO_LOCALE}, che è solo locale al contenitore.
FILE_DATABASE_POSTGRES_INIZIALIZZATO=${CARTELLA_PROGRESSO_CONDIVISA}/database_postgres_inizializzato
if [[ ! -f ${FILE_DATABASE_POSTGRES_INIZIALIZZATO} ]]; then
    echo "Inizializzazione di un database postgres vuoto"
    sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD '${PASSWORD_UTENTE_POSTGRES}';"
    sudo -u postgres createdb ${NOME_DATABASE_POSTGRES}
    touch ${FILE_DATABASE_POSTGRES_INIZIALIZZATO}
else
    echo "Riutilizzo del database postgres esistente"
fi

## Parte 3: preparazione delle applicazione django

# Genera una chiave segreta django
CHIAVE_SEGRETA_DJANGO_FILE="${CARTELLA_SEGRETI}/chiave_segreta_django"
if [[ ! -f "${CHIAVE_SEGRETA_DJANGO_FILE}" ]]; then
    echo "Generazione di una nuova chiave segreta django"
    CHIAVE_SEGRETA_DJANGO=$(cat /dev/urandom | tr -dc 'abcdefghijklmnopqrstuvwxyz0123456789!@#$^&*-_=+' | head -c 50; echo)
    echo ${CHIAVE_SEGRETA_DJANGO} > ${CHIAVE_SEGRETA_DJANGO_FILE}
else
    echo "Riutilizzo della chiave segreta django esistente"
    CHIAVE_SEGRETA_DJANGO=$(cat "${CHIAVE_SEGRETA_DJANGO_FILE}")
fi

# Preparazione dell file settings.ini
FILE_IMPOSTAZIONI_MERSENNE=/root/config/settings.ini
if [[ ! -f ${FILE_IMPOSTAZIONI_MERSENNE} ]]; then
    echo "Inizializzazione del file settings.ini"
    cat <<EOF > ${FILE_IMPOSTAZIONI_MERSENNE}
[settings]
SECRET_KEY=${CHIAVE_SEGRETA_DJANGO}
DEBUG=False
ALLOWED_HOSTS=*
RDS_DB_NAME=${NOME_DATABASE_POSTGRES}
RDS_USERNAME=postgres
RDS_PASSWORD=${PASSWORD_UTENTE_POSTGRES}
RDS_HOSTNAME=localhost
EOF
else
    echo "Riutilizzo del file settings.ini esistente"
fi

# Avvia le migrazioni di django, se necessario
# Nota: le migrazioni avvengono sul database, che è su un volume condiviso.
#       Per questo motivo il file di progresso viene salvato nella cartella
#       ${CARTELLA_PROGRESSO_CONDIVISA} montata sul volume anziché nella cartella
#       ${CARTELLA_PROGRESSO_LOCALE}, che è solo locale al contenitore.
FILE_MIGRAZIONI_DJANGO_AVVIATE=${CARTELLA_PROGRESSO_CONDIVISA}/database_django_migrato
if [[ ! -f ${FILE_MIGRAZIONI_DJANGO_AVVIATE} ]]; then
    echo "Inizializzazione delle migrazioni del database django"
    cd /root
    python3 manage.py makemigrations
    python3 manage.py makemigrations mersenne
    python3 manage.py migrate
    touch ${FILE_MIGRAZIONI_DJANGO_AVVIATE}
else
    echo "Migrazioni django già inizializzate"
fi

# Crea i file statici di django, se necessario
# Nota: i file statici vengono creati localmente nella applicazione django.
#       Per questo motivo il file di progresso viene salvato nella cartella
#       ${CARTELLA_PROGRESSO_LOCALE} anziché quella condivisa
#       ${CARTELLA_PROGRESSO_CONDIVISA}
FILE_STATICI_DJANGO_CREATI=${CARTELLA_PROGRESSO_LOCALE}/django_static_inizializzato
if [[ ! -f ${FILE_STATICI_DJANGO_CREATI} ]]; then
    echo "Creazione dei file statici di django"
    cd /root
    python3 manage.py collectstatic --noinput
    touch ${FILE_STATICI_DJANGO_CREATI}
else
    echo "File statici di django già creati"
fi

# Crea un utente amministratore e un utente giuria, se necessario
# Nota: la creazione di utenti implica operazioni sul database, che è su
#       un volume condiviso.
#       Per questo motivo il file di progresso viene salvato nella cartella
#       ${CARTELLA_PROGRESSO_CONDIVISA} montata sul volume anziché nella cartella
#       ${CARTELLA_PROGRESSO_LOCALE}, che è solo locale al contenitore.
FILE_UTENTI_DJANGO_INIZIALIZZATI=${CARTELLA_PROGRESSO_CONDIVISA}/utenti_django_inizializzati
if [[ ! -f ${FILE_UTENTI_DJANGO_INIZIALIZZATI} ]]; then
    # Creazione amministratore
    export DJANGO_SUPERUSER_USERNAME=amministratore
    export DJANGO_SUPERUSER_PASSWORD=$(cat /dev/urandom | tr -dc 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$^&*-_=+' | head -c 10; echo)
    export DJANGO_SUPERUSER_EMAIL="amministratore@mersenne.docker"
    echo "Inizializzazione dell'utente amministratore di default con username ${DJANGO_SUPERUSER_USERNAME} e password ${DJANGO_SUPERUSER_PASSWORD}"
    cd /root
    python3 manage.py createsuperuser --no-input
    FILE_PASSWORD_AMMINISTRATORE=${CARTELLA_SEGRETI}/password_amministratore
    echo ${DJANGO_SUPERUSER_PASSWORD} > ${FILE_PASSWORD_AMMINISTRATORE}
    # Creazione giuria
    export DJANGO_USER_USERNAME=giuria
    export DJANGO_USER_PASSWORD=$(cat /dev/urandom | tr -dc 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$^&*-_=+' | head -c 10; echo)
    export DJANGO_USER_EMAIL="giuria@mersenne.docker"
    echo "Inizializzazione dell'utente giuria di default con username ${DJANGO_USER_USERNAME} e password ${DJANGO_USER_PASSWORD}"
    cd /root
    python3 manage.py createuser --no-input
    FILE_PASSWORD_GIURIA=${CARTELLA_SEGRETI}/password_giuria
    echo ${DJANGO_USER_PASSWORD} > ${FILE_PASSWORD_GIURIA}
    # Crea il file di progresso
    touch ${FILE_UTENTI_DJANGO_INIZIALIZZATI}
else
    echo "Utenti django già inizializzati"
fi

## Parte 4: avvia il server

cd /root
if [[ $# -eq 0 ]]; then
    echo "Avvio del server"
    uvicorn config.asgi:application --host 0.0.0.0 --port 80 --workers 3
else
    echo "NON avvio il server perché è stato fornito un comando: $@"
    exec "$@"
fi
