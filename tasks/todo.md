# projump — cache per avvio istantaneo

## Problema (misurato)

`projump-path` su `~` impiega ~6,2 s:

- `fd` a caldo: ~1,2 s (440 directory `.git`)
- resto (~5 s): 784 `spawnSync` di `git` seriali — `reflog -n1` + `for-each-ref` per ognuno dei 392 repo visibili

Il pre-filtro dei nascosti prima di git non serve (440 → 392, guadagno trascurabile). Il costo è intrinseco alla scansione: va evitata, non ottimizzata.

## Fase 1 — cache su file

- [x] File cache: `${XDG_CACHE_HOME:-~/.cache}/projump/<hash(root+all)>.json`
- [x] Formato: `{ version, generatedAt, root, all, repos: [{ path, sortMs }] }`
- [x] Chiave = `root` + `all`, **non** `limit`: si salva la lista completa ordinata, lo slice a `--limit` avviene in lettura
- [x] `version` bumpato se cambia la forma del record → cache vecchia ignorata, non crash
- [x] Scrittura atomica: `<file>.tmp` + `fs.renameSync`
- [x] In lettura: filtro `fs.existsSync` sui path (repo cancellati/rinominati non devono comparire né far fallire il `cd`)
- [x] Cache miss / corrotta / versione diversa → scansione live + scrittura cache

## Fase 2 — `--live` / `-l`

- [x] Flag booleano `live`, alias `-l` (nessuna collisione con `-r`, `-n`, `-a`)
- [x] Ignora la cache, riscansiona **e riscrive** la cache
- [x] `--live` è anche il modo documentato per invalidare la cache a mano

## Fase 3 — freschezza

- [x] TTL (default 24 h) come rete di sicurezza: oltre il TTL si riscansiona
- [x] Refresh in background: si mostra subito la lista da cache, poi si rilancia la scansione staccata (`spawn(..., { detached: true, stdio: "ignore" })` + `child.unref()`) che riscrive la cache per il lancio successivo
- [x] Verifica del detach cronometrando **la funzione shell `projump`**, non `node src/index.js`

## Fase 4 — documentazione (prima del commit)

- [x] `tools/projump/README.md`: sezione "Cache" + tabella opzioni con `--live` e `--refresh-only`
- [x] README principale: riga projump aggiornata
- [x] `LOG.md`: voce datata

## Fase 5 — git in parallelo

- [x] `execFile` + pool di 16 al posto di `spawnSync` seriale; ordinamento invariato
- [x] Le due chiamate git per repo (`reflog`, `for-each-ref`) girano anch'esse in parallelo

Da **non** fare: sostituire git con `fs.stat` su `.git/logs/HEAD` — regredirebbe l'ordinamento per attività introdotto in 39db5cb.

## Decisioni prese

1. Cache in `${XDG_CACHE_HOME:-~/.cache}/projump/` (non `/tmp`: sopravvive al riavvio WSL)
2. TTL 24 h
3. Refresh in background: sì
4. Git in parallelo (Fase 5): dentro scope

## Review

- Risultato su `~` (440 `.git`, 392 visibili): funzione shell `projump` da **6,2 s a 0,062 s** con cache calda; scansione live da 6,2 s a **2,7 s** (di cui 1,2 s è `fd`, il resto git).
- Il refresh in background parte solo se la cache ha più di 10 minuti (`CACHE_REFRESH_AFTER_MS`): senza questa soglia ogni singolo `projump` lancerebbe una scansione completa dell'intera home.
- `--refresh-only` è il meccanismo del refresh in background (il processo staccato richiama se stesso con quel flag) ed è anche utile a mano per pre-scaldare la cache.
- Test eseguiti: cache calda 56 ms; refresh staccato che non blocca il wrapper shell (0,062 s con bg refresh attivo) e che riscrive davvero il file; `--live` che riscrive `generatedAt`; cache separate per `--root` e `--all`; repo cancellato che sparisce dalla lista letta da cache senza riscansione; selettore interattivo verificato su pty.
- Non testato: cache corrotta/versione futura (percorso coperto dai `try/catch` e dal check `version`, ma senza test dedicato).
