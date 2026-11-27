# 04 · Events, police, army and costumes – research notes for Live mode

Status: v0.1 (2026-11-21). Feeds the character/costume work (`web/src/data/history.ts` CLOTHING, people tints) and the
event scenes (`web/src/sim/scenes.ts`). Every item says what it is used for and how sure we are.
Confidence tags as in docs/DATA-SOURCES.md: **documented** · **inferred** · **conjectural** (incl. "reenactment-derived").

---

## 1. Scoppio del Carro and the colombina (Easter Sunday, Piazza del Duomo)

**What happens (documented, modern form)**
- Tradition: Pazzino de' Pazzi, first over the walls of Jerusalem in the First Crusade (1099), brought home three
  flint fragments of the Holy Sepulchre. They are kept today in Santi Apostoli (earlier in Palazzo Pazzi, Santa Maria
  Sopra Porta, San Biagio). The crusade story itself is legend.
- From the late 12th century the Easter fire was struck from these flints. Later the "holy fire" was carried in a silver
  Renaissance lantern (the *porta fuoco*).
- Easter morning: fire struck at Santi Apostoli → procession of clergy and officials, opened by the city banner and the
  Pazzi flag, to Piazza del Duomo.
- The cart, nicknamed **Brindellone**: a tall painted tower covered with Florentine arms; first built **1622**; kept in a
  long narrow shed in Via il Prato; drawn by (white) oxen to the square.
- ~11:00 the archbishop lights the **colombina** (a dove-shaped rocket) at the high altar; it runs on a wire down the
  nave, out of the main door to the cart, sets off coloured smokes, bangs and a pinwheel on top, then runs back.
  A clean flight = good harvest (omen).
- Modern: armed men in period costume line the square (Corteo storico).

**Implemented (v0.3)**: costume kit (`blender/scripts/build_characters.py` → `web/public/models/costumes.glb` + `hats.glb`): garments cut from the shared Mixamo body and skinned to its skeleton (shirt, doublet, hose, breeches, tunic, boots, bodice, skirt, robe, apron, cloak; beret, hood, brimmed hat, helmet, top hat), dressed by era/sex/wealth in `web/src/sim/people.ts`; Calcio Storico players in doublet + breeches + hose (1530) or modern kit, guards, vendors, boatmen, fishermen.

**Implemented (v0.2)**: `scoppio` scene, from 1622, on the computed Easter date (Julian computus before 1583,
Gregorian after), 08–13 h. Brindellone + colombina assets from Blender; wire from Duomo door to the cart; 45 s cycle:
flight → sparks + smoke → return. Crowd ring kept off the wire corridor; red-clad procession group.
**Gaps / next**: oxen team + entry procession from Santi Apostoli; the earlier pre-1622 cart (form unknown →
conjectural, so we start the event at 1622); Pazzi + city banners; *giglio* heraldry on the cart panels.

### In the app (Live mode)
When the colombina reaches the cart, about 10 s of fireworks go off on it: bursts at points on the cart and two spinning
wheels (girandole); small smoke puffs grow to a fixed size, rise a few metres and fade near the cart. Then it stops.
Effects live in `web/src/sim/fx.ts` (shared with the 1944 explosions).

## 1b. The move of the David (14–18 May 1504) and the Night of the Bridges (3–4 August 1944)
- **David**: left the Opera del Duomo yard at sunset on 14 May 1504 through the wall broken above the gate; 40+ men,
  timber frame on greased beams with the statue hung inside; arrived 18 May, set on the ringhiera 8 June (Luca Landucci,
  quoted by Opera di Santa Maria del Fiore, Opera Magazine post 4693). Route not documented – presumed in the app.
- **Night of the Bridges**: from the evening of 3 August to dawn on 4 August 1944 the retreating German army blew up
  Ponte alle Grazie, Santa Trinita, alla Carraia, San Niccolò and alla Vittoria; Ponte Vecchio was spared but Por Santa
  Maria, Via de' Bardi, Borgo San Jacopo and Via Guicciardini were mined (La Nazione; Uffizi "The Night of the Bridges").
  The app plays the blasts one after another in a loop (order and timing compressed; hours per bridge not documented).

## 1c. The flood of 4 November 1966
- The Arno rises through the night, comes over the lungarni about 5 a.m., reaches Piazza del Duomo by 9:45, stands highest in
  the afternoon and falls from 8 p.m.; the streets clear on 6 November. The water's surface is calibrated on the Via dei Neri
  plaque (4.92 m) and Piazza del Duomo (≈1.8 m); a 100 s loop, with a clock naming the hour (`web/src/sim/flood.ts`).
  Heights, timings and sources: [landmarks/LUNGARNI.md](landmarks/LUNGARNI.md#the-flood-of-4-november-1966).

## 2. Florentine carnival (Carnevale)

**Documented**
- Medici period: allegorical floats (*trionfi*) and masked groups paraded the streets, with **canti carnascialeschi**
  (carnival songs). Lorenzo il Magnifico's *Trionfo di Bacco e Arianna* ("Quant'è bella giovinezza…") was written for
  the carnival of 1490, sung on Bacchus' float with Ariadne, nymphs and satyrs. Heinrich Isaac wrote carnival songs
  for Lorenzo c. 1480 (music lost).
- 1513: two companies staged about ten floats. Cosimo I sent out 21 *trionfi* on 21 February (Lapini's diary).
  The genre continued through the 16th century (*mascherate* under Cosimo I).
- Savonarola years (1496–1498): his *fanciulli* (boys' brigades) went door to door collecting "vanities" (cards, dice,
  mirrors, cosmetics, books, instruments) and alms instead of the usual carnival pranks. On 7 Feb 1497 the
  "bonfire of the vanities": a stepped pyramid in Piazza della Signoria, burnt on the last day of carnival.
  On the day his followers wore white robes, garlands and red crosses.

**Scene design (inferred)**
- `carnevale` 1470–1530 (Jan → Shrove Tuesday, evening): 3–6 floats moving along the Via Larga → Duomo →
  Signoria route; masked figures (masks = small prop), torch-bearers, singers around each float; crowd lining streets.
- `vanita` 7 Feb 1497 (and 1498): pyramid in Piazza della Signoria; boys in white with red crosses walking door to door
  in the surrounding streets; fire + smoke at dusk (reuse the Scoppio spark/smoke system).
- Gap: float shapes are only known from texts and later prints → **conjectural** geometry.

## 3. Police and public order

**Documented**
- Commune (13th–14th c.): policing was a duty of the foreign magistrates – the **Podestà** and the **Capitano del
  Popolo** – each with an armed household (*famiglia*). They controlled who carried weapons, who was out at night,
  and gambling.
- 1355: a night guard of 600 *custodi della notte* recruited by the gonfalonieri from the 16 gonfaloni (half on duty
  each night). The evening bell started the **coprifuoco** (curfew) and the gates were shut. They supported the
  magistrates' guards but apparently could not arrest.
- 1378, after the Ciompi revolt: the **Otto di Guardia (e Balìa)** – first political police, then the main criminal
  court – sat in the Bargello and lasted until 1777 (then the Supremo Tribunale di Giustizia).
- The enforcers – *birri / sbirri*, led by a *bargello* (captain) – had a bad reputation for violent, arbitrary
  policing. Justice also had fixed places (Bargello, Stinche prison, execution sites).
- Corteo storico costume of the *Sergenti degli Otto*: raw-leather corslet over the doublet, red hose and shoes,
  Florentine *bacinetto* helmet. These are 20th-century reenactment replicas (**reenactment-derived**).

**Scene design**
- `ronda` (patrol), all periods 1250–1800, after dark: groups of 4–6 armed men walking a loop through the street graph
  near the Bargello / Palazzo del Podestà; one carries a lantern (point light in high quality mode); they stop and
  "question" a lone walker (agents face each other + headShake). Before 1378: *famiglia* of the Podestà/Capitano;
  1378–1777: birri of the Otto. Curfew: after the evening bell the civilian density drops, patrols increase.
- Costume (**inferred**): dull wool doublet + hose, leather jerkin / brigandine, iron cap (bacinetto/cervelliera),
  halberd or partisan, sword. No standard uniform before the modern era → we tint by role, not by "uniform".

## 4. The army and militia

**Documented**
- Communal army: citizen levies by *sesto/quartiere* and gonfalone, carroccio (13th c.); from the 14th c. mostly
  mercenaries (*condottieri*).
- **Ordinanza** (militia) of 1506: Machiavelli's project, run by the new magistracy *Nove di Ordinanza e Milizia*
  (Machiavelli its secretary); re-established under the last republic, 1527–1530. Target of about 20,000 men; in
  1506 about 10,000 foot, mainly pikes, with arquebusiers, halberds, crossbows, sword-and-buckler men (secondary
  source for the mix). Muster rolls describe men "per peli e per segni" (by hair and marks).
- Landucci links the fashion for slashed breeches to soldiers' clothing in wartime.
- **Bande Nere**: Giovanni de' Medici's mercenary companies (c. 1517–1528, 1,000–4,000 men, many arquebusiers) took
  black mourning bands/banners after Leo X died (1521).
- Corteo storico (since 1930): *Fanti dell'Ordinanza* wear a green sash across the chest (sign of the city militia);
  *Bombardieri* in red/blue striped doublets with yellow trimming, yellow breeches with red-blue slashes, plumed red
  caps, red hose and shoes; arquebusiers in olive-green slashed doublets, wine-red breeches, red caps with plumes,
  iron gorget; crossbowmen in red doublets, black slashed breeches, black caps edged red. Costume designers worked
  from mid-16th-century sources (**reenactment-derived**).

**Scene design**
- 1529–30 siege: Ordinanza companies on the walls/bastions (San Miniato!), drilling in squares; pikes upright.
- Calcio 1530: spectators include militiamen (green sashes).
- `rassegna` (muster) of the Ordinanza in Piazza della Signoria, 1506 (exact date of the first parade: to check in Landucci).

## 5. Costume palette by period (for the people system)

| Period | Men (common) | Women (common) | Elite / officials | Soldiers / police | Confidence |
|---|---|---|---|---|---|
| Roman (–5th c.) | tunic, cloak | stola, palla | toga (rare in street) | legionary kit | inferred |
| 1000–1300 | knee tunic, hose, hood | long gown, veil | fur-lined *lucco* (later) | mail, kettle hat | inferred |
| 1300–1500 | *farsetto* + hose, *cappuccio* | *gamurra* + *cioppa* | red *lucco* (citizens of rank), priors in crimson | brigandine, bacinetto | inferred (paintings: Ghirlandaio, Masaccio) |
| 1500–1600 | slashed doublet, breeches | bodice + sleeves | black Spanish style under Cosimo I | Ordinanza (green sash), Bande Nere (black) | inferred / reenactment-derived |
| 1600–1800 | coat, waistcoat, breeches | stays, skirts, shawl | wigs (18th c.) | grand-ducal guard | inferred |
| 1800–1900 | frock coat, top hat | crinoline → bustle | | carabinieri / national guard | documented (photos from 1850s) |
| 1900– | modern | modern | | | documented |

## 6. Interactions to animate (requested list → building blocks)

| Interaction | Needs | Asset/anim source |
|---|---|---|
| buying | vendor + customer facing, hand-over | stalls (done), *agree/headShake* (have), "give" clip (Mixamo/Blender) |
| walking / running | on the street graph | have (walk/run) |
| talking | pairs/groups facing, idle + gestures | idle/agree/headShake; add "talk" clip |
| sitting | benches, steps, taverns | bench + table props (done); "sit" clip needed |
| eating / drinking | tavern tables, cups | table prop (done); "drink" clip needed |
| fighting | calcio, brawls, militia drill | "punch", "push" clips needed |
| playing | dice, cards, ball games, children | "crouch", "throw" clips needed |

Practical path: rig period characters in Blender (MPFB/MakeHuman base, CC0), add clothing per row of §5, share
one skeleton so Mixamo-style clips can be retargeted. The current Xbot remains the placeholder.

## Sources
- David move: https://duomo.firenze.it/it/opera-magazine/post/4693/quando-il-david-si-mosse · Night of the Bridges: lanazione.it ("La notte dei ponti"), uffizi.it (The Night of the Bridges), storiadifirenze.org (agosto 1944).
- Scoppio: visittuscany.com (EN/IT event pages); duomo.firenze.it (Opera di Santa Maria del Fiore, event page);
  lanazione.it (2026 report; Pazzino legend); visitflorence.com (Brindellone 1622); Wikipedia "Scoppio del carro".
- Carnival: firenzemadeintuscany.com ("Il carnevale al tempo dei Medici"); Wikipedia/Britannica "Carnival song";
  Cambridge Urban History, "Courtiers and musicians meet in the streets: the Florentine mascherata under Cosimo I"
  (Lapini diary, Grazzini *Tutti i trionfi*); Paola Ventrone (ed.), *Le tems revient* (1992);
  Smithsonian, History Today, Wikipedia "Bonfire of the vanities"; Renaissance & Reformation 46/2 (2023) on the fanciulli.
- Police: hiddenflorence.org (Ercole, crime and punishment); Archivio di Stato di Firenze fonds descriptions
  "Otto di guardia e balìa della Repubblica / del Principato" (via the DHLab roadmap); naibi.net (Capitano's
  *famiglia*, 1405 condemnations); Przegląd Historyczny 75/3 (1984) on the 1355 night guards; unifi PhD thesis on
  the Otto di Guardia; Catalogo generale dei Beni Culturali (sigecweb ICCD14955478, ICCD15055774: Sergenti degli Otto).
- Army: Wikipedia "Florentine military reforms"; Cambridge Renaissance Quarterly (2018) "Machiavelli and the
  Florentine Militia of 1506"; A. Guidi, *Historical Research* 89 (2016) "Per peli e per segni"; myarmoury.com
  "Renaissance Armies: The Italians"; Wikipedia/Britannica "Black Bands", "Giovanni delle Bande Nere";
  sigecweb ICCD14876653 (Bandieraio dei Fanti dell'Ordinanza), all4shooters.com (Corteo storico weapons and uniforms);
  FUP volume citing Landucci 1883 on slashed breeches.
