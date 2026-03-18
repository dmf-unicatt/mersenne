#!/usr/bin/env node
/*
Copyright (C) 2024-2026 degli autori di mersenne

Questo file fa parte di mersenne.

SPDX-License-Identifier: MIT
*/
// Script che genera temporaneamente la CSS di Tailwind a partire dai contenuti
// del progetto, estrae tutte le classi generate e confronta con le classi
// effettivamente usate nei template. Se trova classi usate ma non generate,
// esce con codice 1 e stampa l'elenco.

const fs = require("node:fs");
const path = require("node:path");
const os = require("node:os");

// Usa PostCSS + plugin Tailwind per generare la CSS senza dipendere dal bin CLI
const postcss = require("postcss");
const tailwindPlugin = require("@tailwindcss/postcss");

// Usa una cartella temporanea in /tmp per non sporcare il repo
const root = path.resolve(__dirname, "../../..");
const tmpRoot = os.tmpdir();
const tmpDir = fs.mkdtempSync(path.join(tmpRoot, "mersenne-tailwind-"));

// Usa il file principale CSS del progetto se disponibile, risolvendo i
// path relativi nelle direttive @source in percorsi assoluti perché il
// processo viene eseguito dalla tmp dir.
const inputCss = path.join(tmpDir, "input.css");
const outCss = path.join(tmpDir, "output.css");
const projectMainCss = path.join(root, "mersenne/frontend/css/main.css");
const mainDir = path.dirname(projectMainCss);
let mainCssContent = fs.readFileSync(projectMainCss, "utf8");
// Risolvi @source "..." o @source '...'
mainCssContent = mainCssContent.replace(
    /@source\s+(["'])(.*?)\1/g,
    (_m, q, pth) => {
        const abs = path.resolve(mainDir, pth);
        return `@source ${q}${abs}${q}`;
    }
);
// Risolvi @import "tailwindcss" -> import assoluto al pacchetto installato
const twIndex = require.resolve("tailwindcss/index.css");
mainCssContent = mainCssContent.replace(
    /@import\s+(["'])tailwindcss\1/g,
    `@import "${twIndex}"`
);
// Risolvi @plugin "daisyui" e @plugin "daisyui/theme" verso percorsi assoluti
mainCssContent = mainCssContent.replace(
    /@plugin\s+["'](daisyui(?:\/theme)?)["']/g,
    (_m, mod) => {
        const resolved = require.resolve(mod);
        return `@plugin "${resolved}"`;
    }
);
fs.writeFileSync(inputCss, mainCssContent, "utf8");

(async function main() {
    console.log("Generazione temporanea della CSS di Tailwind...");

    // Carica configurazione Tailwind e genera il CSS
    const cfgPath = path.join(root, "tailwind.config.js");
    const tailwindConfig = require(cfgPath);
    const inputCssContent = fs.readFileSync(inputCss, "utf8");

    // Per permettere la risoluzione dei moduli (es. daisyui, tailwindcss)
    // usiamo temporaneamente la root del progetto come cwd così che
    // require/resolve trovi node_modules del repo.
    const prevCwd = process.cwd();
    try {
        process.chdir(root);
        const plugin = tailwindPlugin(tailwindConfig);
        const result = await postcss([plugin]).process(inputCssContent, {
            from: inputCss,
            to: outCss,
            map: false,
        });
        fs.writeFileSync(outCss, result.css, "utf8");
    } finally {
        process.chdir(prevCwd);
    }

    // Estrae i selettori di classe dalla CSS generata
    const css = fs.readFileSync(outCss, "utf8");
    const classSet = new Set();
    const selectorRegex = /\.([^\s,{]+)/g;
    let m = selectorRegex.exec(css);
    while (m !== null) {
        const cls = m[1];
        // decodifica escape comuni usati da Tailwind (es. \: per i separatori)
        const decoded = cls
            .replace(/\\:/g, ":")
            .replace(/\\\//g, "/")
            .replace(/\\\./g, ".");
        // rimuove pseudoselettori come :after
        const base = decoded.split(":")[0];
        if (base) classSet.add(base);
        m = selectorRegex.exec(css);
    }

    // Esplora le directory dei template per raccogliere i file HTML
    function walk(dir, cb) {
        const entries = fs.readdirSync(dir, { withFileTypes: true });
        for (const e of entries) {
            const p = path.join(dir, e.name);
            if (e.isDirectory()) walk(p, cb);
            else cb(p);
        }
    }

    const templateFiles = [];
    ["mersenne/templates"].forEach((base) => {
        const p = path.join(root, base);
        if (fs.existsSync(p))
            walk(p, (file) => {
                if (file.endsWith(".html")) templateFiles.push(file);
            });
    });

    // Estrae le classi usate negli attributi `class` delle template
    const used = new Set();
    const classAttrRegex = /class\s*=\s*"([^"]*)"|class\s*=\s*'([^']*)'/g;

    for (const f of templateFiles) {
        const content = fs.readFileSync(f, "utf8");
        let mm = classAttrRegex.exec(content);
        while (mm !== null) {
            const val = mm[1] || mm[2] || "";
            // Ignora espressioni template che contengono { o %
            if (val.includes("{") || val.includes("%")) {
                mm = classAttrRegex.exec(content);
                continue;
            }
            const parts = val.split(/\s+/);
            for (const token of parts) {
                const t = token.trim();
                if (!t) continue;
                // rimuove punteggiatura ai bordi
                const clean = t.replace(/^\W+|\W+$/g, "");
                if (clean) used.add(clean);
            }
            mm = classAttrRegex.exec(content);
        }
    }

    // Confronto e output
    const unknown = [...used].filter((u) => !classSet.has(u));

    if (unknown.length === 0) {
        console.log("Tutte le classi trovate nel CSS generato di Tailwind.");
        cleanupAndExit(0);
    } else {
        console.error("Trovate classi usate ma non presenti nel CSS generato:");
        for (const c of unknown) console.error("  -", c);
        cleanupAndExit(1);
    }
})().catch((e) => {
    console.error("Errore nello script di verifica classi:", e);
    cleanupAndExit(2);
});

// Rimuove la cartella temporanea e poi esce col codice fornito in caso di
// successo, altrimenti lascia la cartella per ispezione.
function cleanupAndExit(code) {
    if (code === 0) {
        if (fs.existsSync(tmpDir))
            fs.rmSync(tmpDir, { recursive: true, force: true });
    } else {
        console.error(`I file generati sono disponibili in ${tmpDir}`);
    }
    process.exit(code);
}
