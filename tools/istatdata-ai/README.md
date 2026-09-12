# istatdata-ai

`istat-ask` porta a riga di comando la ricerca IA di IstatData, lo stesso form che sta su `https://esploradati.istat.it/databrowser/#/it/dw/search?ai=true`: una domanda in italiano, l'elenco dei dataset ISTAT che rispondono.

Il servizio è pubblico e non richiede autenticazione. Risponde però con soli identificativi di dataset, quindi il tool li incrocia con il catalogo del nodo: ogni risultato esce con titolo, percorso di categoria, link diretto alla tavola e URL SDMX per scaricare i dati.

## Installazione

```bash
cd tools/istatdata-ai/agent-harness
uv venv .venv
uv pip install --python .venv/bin/python -e .
```

Vengono installati due comandi: `istat-ask` e `cli-anything-istatdata-ai` (sono lo stesso programma; il secondo è il nome richiesto dalla metodologia CLI-Anything). Servono Python 3.9+ e `click`.

## Uso

```bash
istat-ask ask "qual è il reddito medio del comune di Bagheria"
```

```
 1. Contribuenti e reddito complessivo per classi di importo
    Distribuzione del reddito delle persone fisiche per classi di importo nei comuni italiani
    Condizioni economiche delle famiglie e disuguaglianze > Reddito delle persone fisiche (Irpef)  - comuni
    id: IT1,30_1008_DF_MEF_REDDITIIRPEF_COM_2,1.0
    Le dimensioni di analisi presenti nella tavola sono Frequenza, Territorio, Indicatore, Classe di importo, Tempo.
    tavola:  https://esploradati.istat.it/databrowser/#/it/dw/categories/IT1,HOU,1.0/MEF_REDDITIIRPEF_COM/IT1,30_1008_DF_MEF_REDDITIIRPEF_COM_2,1.0
    dati:    https://esploradati.istat.it/SDMXWS/rest/data/IT1,30_1008_DF_MEF_REDDITIIRPEF_COM_2,1.0/?format=csv
```

Altri comandi:

```bash
istat-ask ask "incidenti stradali in Sicilia" --limit 5 --json | jq -r '.results[].url'
istat-ask ask "e per le donne?" --session-id LafBBWBjvc7kz-7E-_ljU
istat-ask dataset "IT1,DF_BES_TERRIT_4,1.0"
istat-ask catalog info
istat-ask catalog refresh
istat-ask repl          # anche senza sottocomando
```

## Opzioni

| Opzione | Cosa fa |
| --- | --- |
| `--lang it\|en` | Imposta l'header `UserLang`. Con `en` il backend lascia vuoti `title` e `ai_title`: il titolo leggibile arriva comunque dal catalogo. La cache è separata per lingua. |
| `--limit N` | Quanti dataset chiedere. Il default del nodo è 20. |
| `--session-id ID` | Rimanda indietro il `session_id` di una risposta precedente per proseguire la conversazione. |
| `--json` | Output machine-readable, chiavi fisse. |
| `--no-description`, `--no-links` | Output umano più stretto. |
| `--no-cache`, `--refresh-catalog` | Governano la cache del catalogo. |
| `--node`, `--node-code`, `--base-url`, `--timeout` | Per puntare a un altro nodo Data Browser. |

## Cache

Il catalogo del nodo (1,9 MB, ~3300 dataset) viene scaricato una volta e tenuto in `${XDG_CACHE_HOME:-~/.cache}/istatdata-ai/`, una copia per nodo e lingua, scrittura atomica, TTL 24 ore. Senza cache ogni domanda costerebbe un paio di secondi in più. Anche `dataset` lo usa: la prima chiamata a cache fredda aspetta quel download, pur sembrando una consultazione locale.

Se il catalogo non è raggiungibile, `ask` risponde lo stesso: l'avviso va su stderr e i risultati escono senza percorso di categoria e senza link alla tavola (con `--lang it` il titolo arriva comunque dal backend).

## Codici di uscita

`0` risposta ottenuta (anche con zero risultati), `2` errore del backend o id di dataset sconosciuto, `3` rate limit.

## Limiti

- Il nodo dichiara un budget di 10 richieste ogni 60 secondi. Le domande vanno fatte in serie.
- L'URL SDMX dei dati scarica l'intero dataflow: su una tavola media sono ~10 secondi, su una grande va oltre i due minuti. Conviene restringerlo con una chiave SDMX o con `startPeriod`/`endPeriod`.
- Il campo `motivation` è una lettera (`I`, `S`, `T`, `A`) di cui non esiste una legenda nell'applicazione: compare solo nel `--json`, grezza.
- Le `suggested_questions` del backend non vengono mostrate: restituisce chiavi i18n non risolte (`ISTAT1`, `ISTAT2`, `ISTAT3`), non domande.
- L'endpoint `AI/GeneratePreview` (l'anteprima dei dati accanto a un risultato) non è coperto.

## Deviazioni dalla metodologia CLI-Anything

Il tool segue CLI-Anything nel layout a package, nell'entry point `cli-anything-istatdata-ai`, nei sottocomandi Click, nel REPL come comportamento di default, in `--json`, nel `TEST.md` scritto prima dei test e nella SKILL.md pacchettizzata. Non implementa la macchina di stato di sessione con undo/redo, il salvataggio automatico delle mutazioni, `--dry-run` e la scrittura con lock del file di sessione: il target è una ricerca in sola lettura e non c'è stato mutabile da proteggere.

Seconda deviazione, di collocazione: il progetto sta sotto `tools/istatdata-ai/` invece che nella radice del repo, per comparire nella tabella dei tool.

## Documentazione tecnica

`agent-harness/ISTATDATA_AI.md` descrive endpoint, payload, header e link, con le verifiche fatte. `agent-harness/TEST.md` contiene il piano di test e i risultati.

## Test

```bash
cd tools/istatdata-ai/agent-harness
.venv/bin/python -m pytest cli_anything/istatdata_ai/tests/test_core.py -q          # offline
PATH="$PWD/.venv/bin:$PATH" CLI_ANYTHING_FORCE_INSTALLED=1 ISTATDATA_AI_LIVE=1 \
  .venv/bin/python -m pytest cli_anything/istatdata_ai/tests -q                     # live
```
