# UI Test Script — verbatim, korak po korak

Svaki test ima:
- **State:** odakle krećeš
- **Akcija:** ŠTO točno napisati / kliknuti
- **Očekivano:** ŠTO točno trebaš vidjeti
- **FAIL ako:** signal da nešto ne valja

Plate koje koristim su iz mock skill seta — sve vraćaju realne podatke.
Prije svega ovog: backend i frontend up.

```bash
# Terminal 1 — backend
cd /Users/luka/PycharmProjects/signal-pilot
.venv/bin/uvicorn backend.main:app --port 8000

# Terminal 2 — frontend dev server
cd /Users/luka/PycharmProjects/signal-pilot/frontend
npm run dev
```

Otvori `http://localhost:5173/chat` u Chrome (incognito/private da nema cached state-a).

---

## SEKCIJA 1 — Osnovni razgovor (5 min)

### Test 1.1 — Prvo slanje

**State:** Prazan chat, sidebar prazan ili praznog stanja.

**Akcija:** U textarea natipkaj:
```
Provjeri Bmove za W-55123K
```
Pritisni **Enter**.

**Očekivano:**
1. Tvoja poruka odmah skoči gore u desni "bubble" (sivi blok, desno).
2. Sidebar lijevo dobije novi red — title kao "Provjeri Bmove za W-55123K" (možda skraćen).
3. Pojavi se "Retrieving and drafting…" sa pulsirajućim narančastim dot-om.
4. Unutar 5-15s pojavi se Skill Timeline strip "Queried 1 source · 1 found".
5. Tekst odgovora počne fluidno upisivati riječ po riječ (smooth streaming, ne chunk-by-chunk).
6. Na kraju: ispod odgovora vidiš muted footer "X,XXX in · XXX out · $0.0X".

**FAIL ako:**
- Tekst ide u chunk-ovima od 50+ znakova (smooth streaming pokvaren)
- Skill timeline ne pokaže "1 found"
- Cost footer fali ili pokaže $0.0000

---

### Test 1.2 — Provjera Thinking blocka

**State:** Test 1.1 završio, vidiš odgovor.

**Akcija:** Iznad odgovora skroluj malo gore. Trebao bi vidjeti malu sivu liniju:
```
› Thinking (XX chars)
```

**Klik** na nju.

**Očekivano:**
1. Klik **otvori** quote-block ispod (sivi border-left, italic monospace).
2. Pokaže ti pravi internal reasoning agenta — nešto kao "The operator wants to check plate W-55123K. Let me look up the user…".
3. Drugi klik **zatvori** ga natrag.

**FAIL ako:**
- Linija fali (extended thinking ne radi)
- Klik ne otvara
- Tekst u block-u je prazan

---

### Test 1.3 — Cost footer matematika

**State:** Test 1.1 odgovor vidiš.

**Akcija:** Pročitaj cost footer ispod odgovora.

**Očekivano:** Format mora biti baš:
```
X,XXX in · XXX out · $0.0XX
```

Vrijednosti:
- input_tokens ~5,000-15,000 (s playbook contextom + system prompt)
- output_tokens ~100-500
- cost između $0.02 i $0.10

**FAIL ako:**
- Footer fali
- Cost je $0.0000 (usage nije zapisan)
- Brojevi nemaju thousands separator

---

## SEKCIJA 2 — Multi-turn context (10 min)

### Test 2.1 — Context carry bez ponavljanja platea

**State:** Tvoj prvi turn s `W-55123K` gotov, vidiš odgovor.

**Akcija:** U textarea natipkaj:
```
Daj mi više detalja o tom korisniku
```
Enter.

**Očekivano:**
1. Tvoja poruka odmah u sivi bubble desno.
2. Agent odgovara — **NE PITA** "koja plate?" ili "koji korisnik?". Direktno daje detalje vezane uz W-55123K.
3. U odgovoru spomene plate (W-55123K), user_id (usr-NNNNNN), ili neke konkretne podatke iz prethodnog turna.
4. Skill timeline možda fire-a novu skill, možda ne — oba su OK.

**FAIL ako:**
- Agent pita za plate iznova
- Agent odgovori nešto generičko bez ikakvih konkretnih podataka iz turna 1

---

### Test 2.2 — Long-range recall

**State:** Test 2.1 gotov.

**Akcija:** Pošalji ova 3 turna jedan za drugim:
```
Što je GDPR ukratko?
```
(Čekaj da završi.)
```
Koliko ima parkirališta u Hrvatskoj?
```
(Čekaj.)
```
Vrati se na onu prvu tablicu s početka razgovora — što smo zapravo našli?
```

**Očekivano:**
1. Prva 2 turna su general questions — agent odgovori bez skill calls.
2. **Treći turn**: agent SE SJETI da je prva tablica bila W-55123K i daje pregled tih nalaza.
3. U odgovoru se mora pojaviti barem "W-55123K" ili konkretni podaci o tom korisniku.

**FAIL ako:**
- Treći turn dobije odgovor "Koja tablica?" ili "Nisam siguran"
- Treći turn fire-a novi skill bez plate-a

---

### Test 2.3 — Plate correction

**State:** Otvori **novi thread** (klik na "+" ili "New chat" gumb u sidebaru — što god je tamo). Ako nema, refreshaj stranicu.

**Akcija:** Pošalji:
```
Provjeri W-55123K
```
Čekaj 5s da krene streaming, ali NE ČEKAJ kraj.

**Bez čekanja kraja**, pošalji drugi turn... wait, ne možeš dok ne završi.

OK, čekaj da završi prvi, onda pošalji:
```
Čekaj, krivo sam napisao. Mislio sam W-38702T. Provjeri tu plate.
```

**Očekivano:**
1. Drugi turn izvrši lookup s W-38702T (vidi se u skill timeline params: "W-38702T").
2. Skill **NE** zove ponovno W-55123K.
3. Odgovor referira W-38702T konkretno.

**FAIL ako:**
- Drugi turn još koristi W-55123K
- Agent pita "koju plate?"

---

## SEKCIJA 3 — Stop / ESC / interrupt (5 min)

### Test 3.1 — Stop dugme

**State:** Otvori novi thread.

**Akcija:** Pošalji long-running query:
```
Daj puni multi-system report za 3 plate: W-55123K, W-38702T, ZG-1234-AB. Bmove + Datatrans + SKIDATA + Graylog za svaku.
```

Čim vidiš da je počeo (sidebar dobio red, skill timeline se pojavio), **klikni Stop dugme** (crveno kvadratno na mjestu Send gumba).

**Očekivano:**
1. Unutar 5-15s streaming staje.
2. Vidiš italic muted liniju **"Stopped by operator."** ispod onog što je već streamano.
3. Sidebar red **NE pokazuje** crveni X / error icon — samo se status promijenio iz streaming u error stanje (možda discreto, ovisno o stilu).
4. Textarea se **opet aktivira** (možeš tipkati).

**FAIL ako:**
- Stop ne radi (treba čekati kraj)
- Pokaže veliki crveni "Unknown error" bar umjesto suptilnog italic teksta
- Textarea ostane disabled

---

### Test 3.2 — ESC tipka

**State:** Otvori novi thread.

**Akcija:** Pošalji isti long query:
```
Daj puni multi-system report za 3 plate: W-55123K, W-38702T, ZG-1234-AB.
```

Čim počne streaming, **klikni bilo gdje na stranici osim textarea** (npr. na sidebar), pa pritisni **ESC**.

**Očekivano:**
1. Identično ponašanje kao Test 3.1 — stream staje, "Stopped by operator." italic.

**FAIL ako:**
- ESC ne radi (samo Stop dugme radi)
- Greška u console-u

---

## SEKCIJA 4 — Sidebar / thread management (5 min)

### Test 4.1 — Switching threadova

**State:** Imaš barem 3 threada u sidebar-u iz prethodnih testova.

**Akcija:** Klikni na **najstariji thread** u sidebaru (samo dno liste).

**Očekivano:**
1. Chat pane se promijeni na taj thread — sve poruke i odgovori loadani u redu.
2. Skill timeline za svaki turn rendered properly (skills + results).
3. Cost footer prikazan ispod svakog odgovora.
4. **NE pokazuje** streaming animacije (sve poruke su završene).

**FAIL ako:**
- Pane ostane prazan
- Cost footer fali
- "Composing response…" se zaglavi na nekom turnu

---

### Test 4.2 — Switching tijekom streaminga

**State:** Otvori novi thread.

**Akcija:** Pošalji short query u njemu:
```
Provjeri ZG-7777-XY
```
**Čim počne streaming**, klikni na drugi thread u sidebaru.

**Očekivano:**
1. Chat pane prebaci na taj drugi thread odmah.
2. Streaming u prvom threadu **nastavi se u backgroundu** (radi server-side daemon).
3. Klik nazad na prvi thread — vidiš da je u međuvremenu nešto napredovao.

**FAIL ako:**
- Switching prekida stream
- Vraćanjem se thread resetira

---

### Test 4.3 — Brisanje threada (soft-delete)

**State:** Imaš barem 2 thread-a.

**Akcija:** Hover-aj nad threadom u sidebar-u (ne onaj koji je trenutno aktivan).

**Očekivano (hover):** Pojavi se mali crveni X / kanta s desne strane reda.

**Akcija:** Klikni X.

**Očekivano:**
1. Thread odmah nestane iz sidebar-a.
2. Ako refreshaš stranicu (Cmd+R / F5), thread se **NE vraća**.
3. Trenutno aktivni chat ostane otvoren.

**FAIL ako:**
- X se ne pojavi na hover
- Klikom se odmah pojavi confirm dialog (ne treba ako je soft-delete)
- Thread se vrati nakon refresha

---

### Test 4.4 — Brisanje aktivnog threada

**State:** Otvori bilo koji thread (klik na njega).

**Akcija:** Hover, klikni X **na trenutno aktivnom threadu**.

**Očekivano:**
1. Thread nestane iz sidebar-a.
2. Chat pane **resetira na empty state** (početni prazni view s example chip-ovima).
3. **NEMA 404 stranice**, nema broken view-a.

**FAIL ako:**
- Pane ostane na obrisanom threadu
- 404 / white screen / broken UI

---

## SEKCIJA 5 — Refresh resilience (5 min)

### Test 5.1 — Refresh mid-stream

**State:** Otvori novi thread.

**Akcija:** Pošalji query:
```
Provjeri W-55123K, daj detaljan report s aktivnom sesijom i zadnjim transakcijama.
```

**Čim počne streaming** (skill timeline se pojavio), **pritisni Cmd+R** (ili F5) — hard refresh.

**Očekivano:**
1. Stranica se reloada.
2. Sidebar pokaže thread (vjerojatno odmah, jer thread već postoji u DB-u).
3. **Klikni na taj thread** — chat pane pokazuje:
   - Tvoju user poruku ✓
   - Skill timeline s eventima koji su se dogodili PRIJE refresha (replayed) ✓
   - Streaming nastavlja LIVE od trenutka gdje je backend trenutno ✓
4. Stream završi normalno s done event-om.

**FAIL ako:**
- Thread nakon refresha nije više "streaming" status
- Skill timeline nedostaje events koji su se dogodili prije refresha
- Stream stoji zauvijek nakon refresha

---

### Test 5.2 — Hard refresh nakon done

**State:** Bilo koji završen thread otvoren.

**Akcija:** Cmd+R.

**Očekivano:**
1. Stranica se reloada.
2. Isti thread otvoren, sve poruke i timelines vidljive identično kao prije.
3. Nema "Composing…" zaglavljenosti.

---

## SEKCIJA 6 — Edge cases (5 min)

### Test 6.1 — Empty submit

**State:** Bilo koji aktivan thread.

**Akcija:** Klikni u textarea, NE TIPKAJ ništa, pritisni Enter.

**Očekivano:**
- **NIŠTA se ne događa.** Submit dugme je disabled.

**FAIL ako:**
- Pošalje prazan turn → backend vraća 422

### Test 6.2 — Veliki paste

**State:** Bilo koji aktivan thread.

**Akcija:** Otvori bilo koji veliki txt (npr. ovaj fajl) i copy-paste cijeli sadržaj u textarea.

**Očekivano:**
1. Textarea raste do max-height-a, onda **skroluje** unutar sebe.
2. Možeš normalno submit-ati.
3. Backend prihvati (ako je ispod 1MB cap-a) ili vraća 413 (ako preko).

### Test 6.3 — Emoji-only follow-up

**State:** Završeni turn u thread-u.

**Akcija:** Pošalji:
```
🤔
```

**Očekivano:**
1. Agent ne crash-a, odgovori nešto.
2. Cost footer normalan.

### Test 6.4 — Croatian + German mix

**State:** Otvori novi thread.

**Akcija:**
```
Provjeri W-12345B. Mein Kunde ist beschwert.
```

**Očekivano:**
- Agent odgovara u jeziku koji prevladava (vjerojatno mješavina, ali coherent).
- Diacritics, umlaut, sve renderirano ispravno.

---

## SEKCIJA 7 — Dark mode (5 min)

### Test 7.1 — Toggle

**Akcija:** Pronađi dark mode toggle (vjerojatno u header-u / settings-u — overi koji UI ima).

Toggle ga.

**Očekivano:**
1. Cijeli UI flipne na dark.
2. **Provjeri svaki element**:
   - User bubble: tamniji fond, kontrast prema tekstu OK
   - Skill timeline: ikone i tekst vidljivi
   - Compaction badge (ako se pojavi): muted ali čitljivo
   - Cost footer: opacity smanjena ali čitljivo
   - Thinking quote-block: italic monospace, kontrast prema border-u
   - Stop dugme: vidljivo crveno
   - Cost cap panel (ako se pojavi): amber dark variant

**FAIL ako:**
- Neki element nestaje (white-on-white, black-on-black)
- Citation chips nečitljive
- Border lines nestane (nema separacije)

---

## SEKCIJA 8 — Error states (3 min)

### Test 8.1 — Backend kill

**Akcija:** U Terminalu 1 pritisni Ctrl+C da ubiješ uvicorn. Onda u UI pošalji bilo koji query.

**Očekivano:**
- UI pokaže jasnu network-error poruku — NE silent freeze.
- Sidebar može pokazati "offline" stanje.

**Akcija:** Pokreni backend opet (`uvicorn backend.main:app --port 8000`).

**Akcija:** Refresh stranicu.

**Očekivano:**
- Sve threadovi opet vidljivi (DB persisted).
- Mid-stream turn iz prije ubijanja sad pokazuje status="error" s message-om "Process crashed before turn finished" (crash recovery).

---

## SEKCIJA 9 — Performance / smoothness (3 min)

### Test 9.1 — Smooth scroll

**State:** Bilo koji thread s 3+ turna.

**Akcija:** Skroluj gore-dolje brzo.

**Očekivano:** Smooth scroll, bez jank-a, bez snap-back.

### Test 9.2 — Token stream

**State:** Pošalji novi long turn.

**Akcija:** Pažljivo gledaj kako tekst stiže.

**Očekivano:**
- Tekst dolazi **smooth** — riječ po riječ ili pola riječi po pola riječi, RAF-animirano.
- **NE** stiže u chunkovima od 50+ znakova odjednom.

**FAIL ako:**
- Tekst skoči naglo, pa stoji, pa opet skoči — to znači RAF animator je pokvaren.

---

## SEKCIJA 10 — Citations (3 min)

### Test 10.1 — Citation rendering

**State:** Bilo koji turn s odgovorom koji ima `[playbook-id]` u tekstu.

**Akcija:** Pogledaj odgovor.

**Očekivano:**
- `[id]` se renderira kao mali numerirani chip (npr. brojić u zagradama ili sl.).
- Hover preko chipa → tooltip s naslovom i opisom playbook-a.
- Klik → otvara playbook viewer panel (ako je wireano).

**Akcija:** Provjeri da nema `[fake-hallucinated-id]` u tekstu (self-correction trebao je obrisati).

---

## Završni check

Kad si gotov sa svim sekcijama, dođi do mene s ovim:
- Koji testovi PASS-aju
- Koji FAIL-aju + sa screenshot-om ili točno kojim koracima da reproducirate

Ako sve PASS — produkcijski spreman (osim auth-a, koji je eksplicitno izvan scope-a).

**Vrijeme**: ~45 min za cijeli pass.
