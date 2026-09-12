## Contesto

`clip.exe` accetta dati da stdin e decide da sé come interpretarli. Sui byte grezzi applica la codepage ANSI della macchina, che non è UTF-8: da qui la corruzione. Riconosce invece il testo UTF-16LE.

## Decisioni

**D1: UTF-16LE invece di riconfigurare la codepage**
Cambiare la codepage della console Windows (`chcp 65001`) è uno stato globale e non attraversa in modo affidabile il confine dell'interop WSL. La conversione a monte è locale al comando e non tocca nulla fuori dal processo.

**D2: senza BOM**
La ricetta diffusa antepone `\xff\xfe`. Misurato su questa macchina: con il BOM il primo code point negli appunti risulta `65279` (U+FEFF), cioè ogni incolla si porta dietro un carattere invisibile. Senza BOM `clip.exe` riconosce lo stesso l'UTF-16LE - verificato su ASCII puro (`ls`, `a`), italiano accentato, giapponese, emoji con coppia surrogata e testo lungo. Vince il no-BOM.

**D3: file temporaneo invece della pipe diretta**
`{ ... } | clip.exe` manda a `clip.exe` i byte già convertiti mentre `iconv` sta ancora leggendo: su un file non valido a metà, la clipboard resta troncata. Scrivere prima su file temporaneo rende la copia atomica. Effetto collaterale utile: la conversione non è più in pipe, sta dentro un `if`, quindi l'exit status valutato è già quello di `iconv` e non serve `PIPESTATUS`.

**D4: fallback ai byte grezzi, non errore**
`iconv` fallisce su file non UTF-8. Uscire con errore regredirebbe casi che oggi passano - file latin-1, file binari - che il comando accetta. Il fallback conserva il comportamento precedente e l'exit code 0; l'avviso su stderr dice che i caratteri non ASCII possono essere corrotti. Nota: quei file non si incollano correttamente nemmeno oggi (`caffè` latin-1 torna `caff` + `Þ`), il fallback non li promuove a corretti, li lascia dov'erano.

## Rischi

- [Risk] `iconv` assente → Mitigation: `command -v iconv`, si prosegue con il percorso precedente
- [Risk] `clip.exe` potrebbe non riconoscere l'UTF-16LE senza BOM su altre versioni di Windows → Mitigation: verificato dal vivo su questa macchina leggendo i code point con `Get-Clipboard`; il caso peggiore è la corruzione che c'era già
