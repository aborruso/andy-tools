# howcli — eval set di 20 coppie query→comando

## Contesto

Suggerimento accettato dall'utente (opzione 2 della valutazione): golden set di ~15-20 coppie query→comando + runner che esegue lo stack reale di howcli con modelli diversi, senza toccare il filesystem (i comandi vengono solo stampati, mai eseguiti). Enabler minimi in howcli: `HOWCLI_MODEL` (override modello) e `HOWCLI_NO_CLIPBOARD` (niente clipboard durante l'eval).

## Fase 1 — implementazione howcli

- [x] `HOWCLI_MODEL` (default `openai-codex/gpt-5.5`) e `HOWCLI_NO_CLIPBOARD=1` in `howcli`
- [x] Bump versione 0.3.0

## Fase 2 — harness

- [x] `eval/cases.json`: 20 casi — 17 esatti + 3 soft (processi CPU, download con varianti curl/wget, delete con bias dry-run)
- [x] `eval/run-eval.sh`: runner bash (flag `--model`, `--filter`, `--out`, `--quiet`; `HOWCLI_BIN`); verdetto PASS/SOFT-OK/DIFF/ERROR, ratio difflib via python3, cache isolata (temp), clipboard disattivata, exit 0 solo senza DIFF/ERROR
- [x] README (sezione Evaluating + note env vars), SPEC (requirements + sezione Evaluation + versione 0.3.0), Makefile (`check` ora valida runner e cases.json), LOG.md

## Fase 3 — verifica

- [x] Stub `pi` che risponde con il comando atteso dal cases.json (modello perfetto) e con `echo STUB_BAD` (modello pessimo): PASS 20/20 exit 0 nel primo caso, 0 PASS + 3 SOFT-OK + 17 DIFF + exit 1 nel secondo
- [x] `--filter csv` → 3 casi (03, 07, 08); `--out` → report markdown con header + 20 righe tabella + dettagli indentati; `--quiet` nasconde i PASS
- [x] Passthrough modello: default → `--model openai-codex/gpt-5.5`; `HOWCLI_MODEL` override; runner `--model` → args di pi ricevono il valore
- [x] Opzione invalida → exit 2; `--help` → exit 0
- [x] `make check` (ora include `bash -n eval/run-eval.sh` e validazione jq del cases.json) e `make install`: `~/bin/howcli --version` = 0.3.0 con entrambe le env vars

## Decisioni prese

1. Casi attesi allineati alle regole del system prompt (ricorsività di default, `2>/dev/null` su scan, niente stderr nascosto su comandi state-changing)
2. Soft cases non penalizzati nel punteggio esattezza: `SOFT-OK` con output non vuoto qualsiasi
3. Confronto esatto come barra onesta; la ratio difflib aiuta il giudizio umano sui DIFF
4. `HOWCLI_MODEL` usa l'env (non un flag) per non cambiare la CLI di howcli; il runner mappa `--model` → env

## Review

- Prime due run: `command -v` su `HOWCLI_BIN` path falliva perché il repo copy di howcli non aveva il bit eseguibile (644). Fix: check `-x` per path con slash + `chmod +x` su `howcli` ed `eval/run-eval.sh` nel repo (coerente con esearch/wopen che sono 755).
- Soft case 16/19/20 con stub pessimo → correttamente `SOFT-OK` (output non vuoto), non DIFF: il bias dry-run del prompt non viene penalizzato.
- Esecuzione reale vs modelli (gpt-5.5, deepseek flash, ecc.) NON eseguita: richiede la sessione Pi/ChatGPT dell'utente e 20 chiamate a modello lato suo. L'harness è pronto: `./eval/run-eval.sh --model <id>`.