# gread — fix UI bugs

## Bug 1 — stelline sovrapposte ai pallini
- `flags` concatena `★●A` senza separazione; `★`/`●` sono glifi a larghezza ambigua → si toccano.
- Fix: spaziare i flag → `${star} ${read}`. Width-neutral (resta 3 celle), `FLAGS_W` invariato.

## Bug 2 — archiviato deve sparire dalla vista
- Causa: nessuna rimozione ottimistica + query senza `in:inbox` (un non-letto archiviato resta `is:unread` → riappare al reload).
- Fix A (`gmail.ts`): aggiungere `in:inbox` alla query → archiviare = uscire sempre dalla lista.
- Fix B (`ui.tsx`): rimozione ottimistica immediata dei target per `a` (archive) e `x` (read+archive), con clamp del cursore.

## Cleanup conseguente
- Con `in:inbox` il flag `arch` (`A`) è sempre vuoto → rimuovere `arch` e l'import `isInInbox`.

## Note
- `r`/`u`/`s` non toccati: il reload li gestisce; fuori scope (non segnalati).

## Verifica
- `make -C tools/gread check` (tsc --noEmit) deve passare.

## TODO
- [x] gmail.ts: aggiungere `in:inbox`
- [x] ui.tsx: rimozione ottimistica per `a` e `x`
- [x] ui.tsx: spaziare i flag + rimuovere `arch`/`isInInbox`
- [x] check tsc (exit 0)

## Review
- `gmail.ts`: query ora include `in:inbox` → archiviare rimuove sempre dalla lista.
- `ui.tsx`:
  - `runAction` accetta `removeFromView`; `a` e `x` rimuovono i target subito da `messages` con clamp del cursore. Il reload async conferma poi dal server.
  - flag spaziati `★ ●` (3 celle, width-neutral) → niente sovrapposizione.
  - rimossi flag `arch` e import `isInInbox` (vestigiali con `in:inbox`).
- Type-check OK. Verifica visiva a runtime ancora da fare con `gread gws/gwsb`.
