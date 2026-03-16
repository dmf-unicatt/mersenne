/*
Copyright (C) 2024-2026 degli autori di mersenne

Questo file fa parte di mersenne.

SPDX-License-Identifier: MIT
*/
import path from "node:path";
import { defineConfig } from "vite";

export default defineConfig({
    base: "/static/",
    build: {
        manifest: true,
        outDir: path.resolve(__dirname, "config/static/mersenne"),
        rollupOptions: {
            input: {
                main: path.resolve(__dirname, "mersenne/frontend/js/main.js"),
            },
        },
    },
    server: {
        port: 5173,
    },
});
