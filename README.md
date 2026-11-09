# tribuna-dati

Risultati e classifiche per l'app Tribuna, aggiornati in automatico.

- `aggiornamenti.json`: i campionati aggiornati (classifica e, dove c'è, le giornate), uno per campionato.
  L'app lo scarica ogni volta che si apre, e con il tasto «Aggiorna ora».
- Lo aggiornano le attività programmate di Claude: il sabato e la domenica ogni ora dal primo pomeriggio
  alla sera, gli altri giorni verso le 22:30.

Formato di ogni campionato: `asOf`, `fonte`, `rows` (una riga per squadra: `Squadra|Punti|G|V|N|P|GF|GS`),
`rounds` facoltativo (`[{name, m: [{h, a, t, sh, sa, note}]}]`) e `updatedAt` (millisecondi).
