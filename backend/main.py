# Copyright (C) 2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT
"""Punto di ingresso dell'applicazione FastAPI per il backend di mersenne."""

import importlib.metadata

import fastapi

metadata = importlib.metadata.metadata("mersenne-backend")

app = fastapi.FastAPI(
    title=metadata["Name"],
    description=metadata["Summary"],
    version=metadata["Version"],
)
