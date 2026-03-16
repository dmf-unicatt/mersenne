# Copyright (C) 2024-2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT
"""Impostazioni di Django per il progetto."""

import configparser
import logging
import os
import pathlib

import django.contrib.messages

BASE_DIR = pathlib.Path(__file__).resolve().parent

# Leggi la configurazione da settings.ini
config = configparser.ConfigParser()
config.read(BASE_DIR / "settings.ini")

# Impostazioni di base
if "settings" in config:
    SECRET_KEY = config["settings"].get("SECRET_KEY")
    DEBUG = config["settings"].getboolean("DEBUG", fallback=False)
    ALLOWED_HOSTS = (
        config["settings"].get("ALLOWED_HOSTS", fallback="*").split(",")
    )
else:
    SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
    DEBUG = os.environ.get("DJANGO_DEBUG", "false").lower() == "true"
    ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",")

# Definizione applicazione
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_cotton.apps.SimpleAppConfig",
    "cotton_icons",
    "mersenne.apps.MersenneConfig",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
if not DEBUG:
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
ROOT_URLCONF = "config.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "OPTIONS": {
            "loaders": [
                (
                    "django.template.loaders.cached.Loader",
                    [
                        "django_cotton.cotton_loader.Loader",
                        "django.template.loaders.filesystem.Loader",
                        "django.template.loaders.app_directories.Loader",
                    ],
                )
            ],
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "builtins": ["django_cotton.templatetags.cotton"],
        },
    },
]
ASGI_APPLICATION = "config.asgi.application"
WSGI_APPLICATION = "config.wsgi.application"


# Database
if "settings" in config:
    DB_NAME = config["settings"].get("RDS_DB_NAME", None)
    DB_USER = config["settings"].get("RDS_USERNAME", "")
    DB_PASSWORD = config["settings"].get("RDS_PASSWORD", "")
    DB_HOSTNAME = config["settings"].get("RDS_HOSTNAME", "")
    DB_PORT = config["settings"].getint("RDS_PORT", fallback=5432)
else:
    DB_NAME = os.environ.get("DJANGO_RDS_DB_NAME", None)
    DB_USER = os.environ.get("DJANGO_RDS_USERNAME", "")
    DB_PASSWORD = os.environ.get("DJANGO_RDS_PASSWORD", "")
    DB_HOSTNAME = os.environ.get("DJANGO_RDS_HOSTNAME", "")
    DB_PORT = int(os.environ.get("DJANGO_RDS_PORT", "5432"))
if DB_NAME:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": DB_NAME,
            "USER": DB_USER,
            "PASSWORD": DB_PASSWORD,
            "HOST": DB_HOSTNAME,
            "PORT": DB_PORT,
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# Validazione password
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation.MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation.CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation.NumericPasswordValidator"
        ),
    },
]
AUTH_USER_MODEL = "mersenne.Utente"


# Logging
class IPAddressFilter(logging.Filter):
    """Filtro di logging per aggiungere l'indirizzo IP del client."""

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Aggiunge l'indirizzo IP del client al record di log in modo sicuro.

        Alcuni record non contengono una HttpRequest (es. logging del server
        wsgiref) e possono fornire un oggetto socket come `request`. Qui
        controlliamo la presenza di `request` e di `META` in modo robusto e
        impostiamo `record.ip` a `None` quando non è possibile estrarre l'IP.
        """
        ip = None
        request = getattr(record, "request", None)
        if request is not None:
            try:
                meta = getattr(request, "META", None)
                if isinstance(meta, dict):
                    x_forwarded_for = meta.get("HTTP_X_FORWARDED_FOR")
                    if x_forwarded_for:
                        ip = x_forwarded_for.split(",")[0]
                    else:
                        ip = meta.get("REMOTE_ADDR")
            except Exception:
                ip = None
        record.ip = ip
        return True


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"add_ip_address": {"()": "config.settings.IPAddressFilter"}},
    "formatters": {
        "log_formatter": {
            "format": "{asctime} {name} {ip} {levelname} {message}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "file": {
            "level": "WARNING",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "django.log",
            "filters": ["add_ip_address"],
            "formatter": "log_formatter",
        }
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "WARNING",
            "propagate": True,
        },
    },
    "root": {
        "level": "DEBUG",
    },
}


# Internazionalizzazione
LANGUAGE_CODE = "it"
TIME_ZONE = "Europe/Rome"
USE_I18N = True
USE_TZ = True


# File statici (CSS, JavaScript, immagini)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"
if not DEBUG:
    STORAGES = {
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
        },
    }


# Caricamento file
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# Messaggi
MESSAGE_TAGS = {django.contrib.messages.constants.ERROR: "danger"}
