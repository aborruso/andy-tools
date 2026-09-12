# ISTATDATA_AI — how the backend works

Everything here was verified live against `esploradati.istat.it` on 2026-08-24,
by reading the Data Browser bundle (`static/js/main.671a3c9f.js`) and by
intercepting the XHR the page actually sends.

## The one call that matters

```
POST https://esploradati.istat.it/databrowserhub/api/core/nodes/1/AI/ExecuteSearch
Content-Type: application/json
UserLang: it

{
  "session_id": null,
  "request": "qual è il reddito medio del comune di Bagheria",
  "aiSearchMaxResults": 20,
  "aiRateLimiting": {"limit": 10, "seconds": 60, "maxMessageLength": 204800},
  "action": {"type": "query"}
}
```

Public, no authentication, no cookie.

Three things are easy to get wrong:

- **`aiRateLimiting` is mandatory.** Omit it and the backend answers
  `{"errorCode": "INTERNAL_ERROR_SERVER", "message": ""}` with HTTP 200. The
  values are the ones the node itself declares in its `AIRateLimiting` extra.
- **`UserLang` is the language switch**, not `Accept-Language`. Without it the
  descriptions come back in English and `title`/`ai_title` come back empty.
- **`action.type`** is `query`. The bundle also uses `refresh_questions` and
  `changeView`; neither is wrapped here.

The answer:

```json
{
  "session_id": "4utgi3DkEWHLHf0pUeG6l",
  "request": "...",
  "response": "Sono disponibili nella sezione dedicata i risultati per la tua ricerca",
  "chatContext": {
    "conversation": [{"sender": "user", "message": "..."}, ...],
    "dataproducts": [
      {"id": "IT1,30_1008_DF_MEF_REDDITIIRPEF_COM_2,1.0",
       "title": "Contribuenti e reddito complessivo per classi di importo",
       "ai_title": "Distribuzione del reddito delle persone fisiche ...",
       "description": "Le dimensioni di analisi presenti nella tavola sono ...",
       "motivation": "I", "similarity": 1.54, "enablePreview": true}
    ],
    "suggested_questions": ["ISTAT1", "ISTAT2", "ISTAT3"]
  }
}
```

`response` is always the same sentence: the real answer is the dataset list.

`suggested_questions` returns unresolved i18n keys, not questions. Dropped.

`motivation` is a single letter (`I`, `S`, `T`, `A`). In the bundle it is
assigned to `aiDescription`, but no legend for it exists anywhere in the app, so
it is passed through raw.

## Conversation

Sending back the `session_id` of a previous answer keeps the context. Verified:
"quanti sono gli occupati in Sicilia" then "e per le donne?" with the same id
gives a four-turn `conversation` and a different result set.

## Titles: the catalogue join

`GET nodes/1/catalog` (about 1.9 MB, ~2 s, 3282 datasets) returns
`datasetMap` (id → title, `referenceMetadata`, layout) and `categoryGroups`
(the category tree, each leaf listing its `datasetIdentifiers`).

Over 100 ids returned by five different questions, zero were missing from
`datasetMap`, so a plain join is enough — no per-dataset fallback.

The join is load-bearing because with `UserLang: en` the AI endpoint returns
empty `title` and `ai_title`, while the catalogue still has English titles.

## Links

**Table in the Data Browser.** The category path is required — the group id
first, then the chain of category ids:

```
https://esploradati.istat.it/databrowser/#/it/dw/categories/IT1,HOU,1.0/MEF_REDDITIIRPEF_COM/IT1,30_1008_DF_MEF_REDDITIIRPEF_COM_2,1.0
```

Without the group id the app answers "the requested page is not available".
Both a two-segment and a three-segment path were opened in a browser to check.

**SDMX web service.** The dataset id is `agency,id,version`:

```
https://esploradati.istat.it/SDMXWS/rest/dataflow/IT1/30_1008_DF_MEF_REDDITIIRPEF_COM_2/1.0?references=all
https://esploradati.istat.it/SDMXWS/rest/data/IT1,30_1008_DF_MEF_REDDITIIRPEF_COM_2,1.0/?format=csv
```

The data URL returns SDMX-CSV. It downloads the whole dataflow: on a medium
table that is ~10 s and 125 kB, on a large one it exceeded a 120 s timeout.
Narrow it with an SDMX key or `startPeriod`/`endPeriod` — for instance
`.../data/IT1,30_1008_DF_MEF_REDDITIIRPEF_COM_2,1.0/A.082006...?format=csv&startPeriod=2022`
(082006 is Bagheria).

## Node settings worth knowing

From `GET nodes/1` extras: `AISearchEnabled=true`, `AISearchMaxResults=20`,
`AISearchPageSize=10`, `AIRateLimiting={"limit":10,"seconds":60,"maxMessageLength":204800}`.

Ten requests per minute is the declared budget: ask serially.

## Not wrapped

`POST nodes/{node}/AI/GeneratePreview` exists and would return the data preview
shown next to a result. Its payload was not reverse engineered.
