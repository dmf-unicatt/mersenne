# Copyright (C) 2024-2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT
"""Configurazione della documentazione di mersenne."""

import os
import sys

import django

# Inizializza django
sys.path.insert(0, os.path.abspath(".."))
django.setup()

# Informazioni sul progetto
project = "mersenne"
copyright = "2024-2026 degli autori di mersenne"
author = "Francesco Ballarin"

# Configurazione generale
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

# Configurazione delle estensioni
autodoc_default_options = {
    "exclude-members": "__dict__,__init__,__module__,__weakref__",
    "imported-members": True,
    "members": True,
    "show-inheritance": True,
    "special-members": True,
    "undoc-members": True,
}

# Opzioni per l'output HTML
html_theme = "nature"
