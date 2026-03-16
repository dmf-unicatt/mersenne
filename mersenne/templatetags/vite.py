# Copyright (C) 2024-2026 degli autori di mersenne
#
# Questo file fa parte di mersenne.
#
# SPDX-License-Identifier: MIT
"""Template tag per includere asset Vite nei template Django."""

import json

import django.conf
import django.template
import django.utils.safestring

register = django.template.Library()


@register.simple_tag
def vite(entry: str) -> django.utils.safestring.SafeString:
    """Restituisce i tag HTML per includere un asset Vite."""
    # Normalizza il nome dell'entrypoint
    entry = f"mersenne/frontend/js/{entry}.js"

    # In modalità di sviluppo, includiamo direttamente gli asset dal server
    # di sviluppo. In produzione, invece, ci aspettiamo che Vite abbia
    # generato un manifest.json
    DEBUG = django.conf.settings.DEBUG  # noqa: N806
    if not DEBUG:
        BASE_DIR = django.conf.settings.BASE_DIR  # noqa: N806
        manifest_file = (
            BASE_DIR / "static" / "mersenne" / ".vite" / "manifest.json"
        )
        if manifest_file.exists():
            with open(manifest_file) as fh:
                manifest = json.load(fh)

            # Costruisci i tag per includere il client di Vite e l'entrypoint
            # richiesto.
            if entry in manifest:
                data = manifest[entry]
                tags = [
                    '<script type="module" src="/static/mersenne/'
                    f'{data["file"]}"></script>'
                ]
                if "css" in data:
                    tags.extend(
                        [
                            '<link rel="stylesheet" '
                            f'href="/static/mersenne/{css}">'
                            for css in data.get("css", [])
                        ]
                    )
                return django.utils.safestring.mark_safe("\n".join(tags))
            else:  # pragma: no cover
                return django.utils.safestring.mark_safe(
                    f"<!-- vite entry not found in manifest: {entry} -->"
                )
        else:  # pragma: no cover
            return django.utils.safestring.mark_safe(
                f"<!-- vite manifest not found: {manifest_file} -->"
            )
    else:  # pragma: no cover
        # Indirizzo del server di sviluppo Vite. La porta 5173 è definita
        # nel file vite.config.js.
        VITE_DEV_SERVER_URL = "http://localhost:5173"  # noqa: N806

        # Costruisci i tag per includere il client di Vite e l'entrypoint
        # richiesto.
        tags = [
            f'<script type="module" src="{VITE_DEV_SERVER_URL}'
            '/static/@vite/client"></script>',
            f'<script type="module" src="{VITE_DEV_SERVER_URL}'
            f'/static/{entry}"></script>',
        ]
        return django.utils.safestring.mark_safe("\n".join(tags))
