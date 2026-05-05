# PRD — Andy Tools

## Stato

Bozza iniziale di idea. Il repository non è ancora inizializzato come progetto operativo.

## Idea

Creare un repository personale in cui raccogliere piccoli tool sviluppati nel tempo per risolvere problemi pratici, automatizzare attività ripetitive o velocizzare flussi di lavoro quotidiani.

Il repo nasce come contenitore semplice, flessibile e personale: non come prodotto pubblico strutturato, ma come spazio ordinato dove salvare, documentare e riusare strumenti utili.

## Problema

Nel lavoro quotidiano emergono spesso micro-esigenze: conversioni, controlli, script di supporto, estrazioni dati, normalizzazioni, automazioni o utility specifiche.

Senza un posto unico dove conservarle, queste soluzioni rischiano di rimanere sparse, difficili da ritrovare o da riusare.

## Obiettivo

Avere un repository unico per:

- raccogliere piccoli tool personali;
- renderli facili da ritrovare;
- documentare rapidamente cosa fanno e come si usano;
- riusare soluzioni già create;
- far crescere il repo in modo organico, senza una struttura troppo rigida all’inizio.

## Pubblico di riferimento

Utente principale: l’autore del repository.

Possibili utenti secondari, in futuro:

- colleghi;
- collaboratori;
- persone con esigenze simili;
- chi trova utile uno specifico tool pubblicato nel repo.

## Ambito iniziale

Il repository potrà contenere, ad esempio:

- script da riga di comando;
- piccoli tool per dati e file;
- utility per conversioni o pulizia dati;
- automazioni personali;
- snippet riutilizzabili;
- mini-progetti indipendenti.

Ogni tool dovrebbe idealmente avere una descrizione minima: cosa fa, quando usarlo, dipendenze, esempio di utilizzo.

## Fuori ambito per ora

In questa fase non sono prioritari:

- packaging formale;
- pubblicazione su package manager;
- interfacce grafiche;
- documentazione estesa;
- architettura complessa;
- compatibilità garantita per utenti esterni.

## Principi guida

- Semplicità prima di tutto.
- Ogni tool deve risolvere un problema concreto.
- Meglio aggiungere poco, ma utile.
- La documentazione minima è parte del tool.
- La struttura del repo può evolvere con l’uso reale.

## Possibile struttura futura

Esempio indicativo, non vincolante:

```text
andy-tools/
├── README.md
├── PRD.md
├── tools/
│   ├── nome-tool-1/
│   └── nome-tool-2/
├── scripts/
└── docs/
```

## Criteri di successo

Il repository sarà utile se:

- permette di ritrovare rapidamente un tool già creato;
- riduce lavoro ripetitivo;
- rende più facile trasformare un’esigenza ricorrente in uno script riutilizzabile;
- resta semplice da mantenere;
- cresce solo quando c’è un bisogno reale.

## Domande aperte

- I tool saranno principalmente in Python, shell, Node.js o linguaggi misti?
- Ogni tool vivrà in una cartella autonoma o alcuni saranno semplici script singoli?
- Il repo resterà personale o potrà diventare pubblico e documentato per altri?
- Serve una convenzione minima per nomi, README e dipendenze?
