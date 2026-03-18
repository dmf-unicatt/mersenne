#!/usr/bin/env node
/*
Copyright (C) 2024-2026 degli autori di mersenne

Questo file fa parte di mersenne.

SPDX-License-Identifier: MIT
*/
// Script helper per eseguire `biome check` sui file di template.
// Il problema è che biome non riesce a processare correttamente i template
// a causa della sintassi `{%`, che biome sostituirebbe in `{ %` (aggiungendo
// quindi uno spazio) e causando errori di parsing in Django.
// Per aggirare questo problema, questo script esegue una sostituzione
// temporanea `{%` -> `{ %` prima di eseguire `biome check`, e poi
// ripristina `{ %` -> `{%` dopo l'esecuzione.

const fs = require("node:fs");
const path = require("node:path");
const { execSync } = require("node:child_process");

// Utilità per racchiudere i path con doppi apici quando passati a shell
function shellEscape(s) {
    return `"${String(s).replace(/"/g, '\\"')}"`;
}

// Lista centralizzata di sostituzioni: ogni elemento è [find, replace].
// Viene usata prima del check e riutilizzata invertita per il ripristino.
function getReplacements() {
    return [
        ["{%", "{ %"],
        ["c-heroicon.", "c-heroicon ."],
    ];
}

// Parsing argomenti: --write è opzionale, il primo argomento non-flag
// è il path
const argv = process.argv.slice(2);
const write = argv.includes("--write");
const others = argv.filter((a) => a !== "--write");
const target = others.length > 0 ? others[0] : ".";

// Processa ricorsivamente i file di template
function collectFiles(start, exts = [".html"]) {
    const files = [];
    if (!fs.existsSync(start)) return files;
    const stat = fs.statSync(start);
    if (stat.isFile()) {
        if (exts.includes(path.extname(start))) files.push(start);
        return files;
    }
    const entries = fs.readdirSync(start, { withFileTypes: true });
    for (const e of entries) {
        const p = path.join(start, e.name);
        if (e.isDirectory()) files.push(...collectFiles(p, exts));
        else if (exts.includes(path.extname(p))) files.push(p);
    }
    return files;
}

// Esegue `biome check` con gli argomenti forniti, restituisce il codice
// di uscita
function runBiome(args) {
    const cmd = ["npx", "biome", "check", ...args].join(" ");
    try {
        execSync(cmd, { stdio: "inherit" });
        return 0;
    } catch (e) {
        return e.status || 1;
    }
}

(async function main() {
    const cwd = process.cwd();
    const absTarget = path.resolve(cwd, target);

    const files = collectFiles(absTarget);
    const modified = new Set();
    let exitCode = 0;

    try {
        const replacements = getReplacements();
        for (const f of files) {
            let txt = fs.readFileSync(f, "utf8");
            let changed = false;
            for (const [find, repl] of replacements) {
                if (txt.includes(find)) {
                    txt = txt.split(find).join(repl);
                    changed = true;
                }
            }
            if (changed) {
                modified.add(f);
                fs.writeFileSync(f, txt, "utf8");
            }
        }

        const args = write
            ? ["--write", shellEscape(target)]
            : [shellEscape(target)];
        exitCode = runBiome(args);
    } catch (err) {
        console.error("Errore durante l'esecuzione del lint helper:", err);
        exitCode = 2;
    } finally {
        const reverseReplacements = getReplacements()
            .slice()
            .reverse()
            .map(([a, b]) => [b, a]);
        for (const f of modified) {
            try {
                let current = fs.readFileSync(f, "utf8");
                let changed = false;
                for (const [find, repl] of reverseReplacements) {
                    if (current.includes(find)) {
                        current = current.split(find).join(repl);
                        changed = true;
                    }
                }
                if (changed) fs.writeFileSync(f, current, "utf8");
            } catch (e) {
                console.error("Impossibile ripristinare", f, e);
            }
        }
    }

    if (write) process.exit(exitCode);
    process.exitCode = exitCode;
})();
