# Statues, columns and fountains in the squares

Most Florentine squares have had a statue, a column or a fountain at some point. Until each gets its own model, the app
shows a plain stone stand-in (base and figure, column, basin, obelisk or cross) for the years it stood, so the squares are
not empty and the list below is the work list for the refinement pass.

Data: `web/src/data/statues.ts` (positions from OpenStreetMap unless noted). Drawing: `web/src/scene/statues.ts`.
Statues that are already part of a landmark model (the Loggia dei Lanzi sculptures, the David and Hercules by
Palazzo Vecchio's door, the Uffizi niche statues) are not repeated here.

## Placeholders in the app (27)

| Statue / fountain | Square | Years | Kind | Confidence | Notes |
|---|---|---|---|---|---|
| Fountain of Neptune | Piazza della Signoria | 1565– | fountain | documented | Ammannati; giant unveiled 1565, fountain finished 1574. |
| Cosimo I | Piazza della Signoria | 1594– | equestrian | documented | Giambologna, bronze on a marble base. |
| Marzocco | Piazza della Signoria | 1420– | figure | documented | Donatello's lion on the ringhiera; a copy since 1885. |
| Colonna dell'Abbondanza | Mercato Vecchio / Piazza della Repubblica | 1431–1890 | column | documented | Removed with the Mercato Vecchio demolition. |
| Colonna dell'Abbondanza (put back) | Piazza della Repubblica | 1956– | column | documented |  |
| Vittorio Emanuele II | Piazza Vittorio Emanuele (Repubblica) | 1890–1932 | equestrian | inferred | Position in the middle of the square inferred; moved to the Cascine in 1932. |
| Vittorio Emanuele II | Piazzale Vittorio Veneto (Cascine) | 1932– | equestrian | documented |  |
| Porcellino | Mercato Nuovo | 1640– | figure | documented | Pietro Tacca's bronze boar. |
| Colonna della Giustizia | Piazza Santa Trinita | 1565– | column | documented | Column from the Baths of Caracalla; Justice on top from 1581. |
| Colonna di San Zanobi | Piazza San Giovanni | 1384– | column | documented |  |
| Giovanni delle Bande Nere | Piazza San Lorenzo | 1850– | monument | documented | Bandinelli 1540; set up in the square in 1850. |
| Croce al Trebbio | Piazza del Trebbio | 1338– | cross | documented |  |
| Ferdinando I | Piazza Santissima Annunziata | 1608– | equestrian | documented | Giambologna and Tacca. |
| Fountain of the sea monsters (east) | Piazza Santissima Annunziata | 1629– | fountain | documented | Pietro Tacca. |
| Fountain of the sea monsters (west) | Piazza Santissima Annunziata | 1629– | fountain | documented | Pietro Tacca. |
| Manfredo Fanti | Piazza San Marco | 1873– | monument | documented |  |
| Monument to the Fallen of Independence | Piazza dell'Unità Italiana | 1882– | obelisk | documented |  |
| Dante | Piazza Santa Croce | 1865– | monument | documented | Stood in the middle of the square 1865–1968, then moved beside the church steps; placeholder at today's spot. |
| Fountain of Piazza Santa Croce | Piazza Santa Croce | 1816– | fountain | inferred |  |
| Bettino Ricasoli | Piazza dell'Indipendenza | 1898– | monument | documented |  |
| Ubaldino Peruzzi | Piazza dell'Indipendenza | 1897– | monument | documented |  |
| Giuseppe Garibaldi | Piazza Garibaldi | 1890– | monument | documented |  |
| Colonna di San Felice | Piazza San Felice | 1572– | column | documented |  |
| Colonna di Santa Felicita | Piazza Santa Felicita | 1381– | column | inferred |  |
| Fontana dello Sprone | Borgo San Jacopo / Via dello Sprone | 1608– | fountain | documented | Buontalenti. |
| Monument to the fallen of Mentana | Piazza Mentana | 1902– | monument | documented |  |
| Girolamo Savonarola | Piazza Savonarola | 1920– | monument | documented | Pazzi 1882, in Palazzo Vecchio until 1920. |

## Still to add (not found in OpenStreetMap, or no position yet)

- The two obelisks of Piazza Santa Maria Novella (1608, on Giambologna's bronze tortoises), race posts of the Palio dei
  Cocchi.
- Vittorio Emanuele II in Piazza della Repubblica: the position in the middle of the square is inferred; check against
  photographs of 1890–1932.
- Dante in Piazza Santa Croce: stood in the middle of the square 1865–1968; the placeholder is at today's spot for the
  whole period.
- Fountains in Piazza Santo Spirito, Piazza del Carmine, Piazza Pitti; the Biancone's earlier site; the Fontana del
  Porcellino's first place (Boboli copy).
- Equestrian monument and fountains outside the study squares (Fortezza, Piazza della Libertà) when those areas are
  modelled.

## Refinement (later)

Replace each placeholder with a model from photographs (materials collection, `docs/materials/manifest.json`), with the
same dates; give each a card and a library entry, as for the landmarks.
