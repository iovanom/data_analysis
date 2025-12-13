# Laboratorul 2 - Wine Explorer

**Autor**: Ivan Majeru

**Titular disciplina**: Anatol Poiata

**Disciplină**: Analiza si Vizualizarea Datelor

**2025**

--------------

### Raport de analiză – Wine Explorer

#### 1. Contextul proiectului

Acest proiect pornește de la un set de date de aproximativ 57.000 de vinuri (`wines_raw.csv`), fiecare observație conținând informații despre:

- Țară (`country`), provincie/regiune (`province`, `region_1`, `region_2`)
- Soi (`variety`), categorie de vin (`category` – Red, White, Rose etc.)
- Vinărie (`winery`) și titlu (`title`)
- Punctaj (`points`)
- Preț (`price`)
- An de recoltă (`vintage`)
- Conținut de alcool (`alcohol`)
- Descriere text (`description`)

Obiectivele principale:

1. Curățarea și explorarea datelor (EDA) – numeric și categorial.
2. Definirea unei noi metrici `quality_price = points / price` pentru raportul preț/calitate.
3. Analiza pe țări, regiuni și soiuri.
4. Analiza textelor de descriere (wordcloud, cuvinte frecvente, legătura cu preț/punctaj).
5. Analiza corelațiilor între variabile.
6. Construirea unei aplicații interactive Streamlit pentru explorare și căutare de vinuri după descriere.

---

#### 2. Preprocesare și curățare date

- Datele sunt citite din `./datasets/wines_raw.csv`.
- Nu există valori lipsă pe coloanele principale – toate câmpurile relevante sunt complete.
- A fost creată o nouă variabilă:
  
  - `quality_price = points / price` – măsoară câte puncte obținem per unitate de preț.

- Standardizări de categorii:
  - Țări:
    - `Bosnia - Herzegovina` → `Bosnia and Herzegovina`
    - `China` → `China (Mainland)`
    - `Macedonia` → `North Macedonia`
    - `Russia` → `Russian Federation`
    - `US`, `USA` → `United States`
  - Categorii de vin:
    - `Rosé` → `Rose`

- Eliminarea outlierilor:
  - Pentru `alcohol` s-au păstrat doar valori între 5% și 25%.
  - Pentru `price`, `points` și `quality_price` s-au păstrat doar valori între percentila 1% și 99%.
  - După filtrare, au rămas **53.940** de înregistrări.

---

#### 3. Analiza descriptivă a variabilelor numerice

Variabile analizate: `price`, `points`, `alcohol`, `quality_price`.

Caracteristici globale (după eliminarea outlierilor):

- **Preț (`price`)**
  - Medie ≈ 29.9 USD
  - Mediană ≈ 25 USD
  - Interval tipic: 20–35 USD (Q1–Q3)
  - Interval după filtrare: 9–100 USD

- **Punctaj (`points`)**
  - Medie ≈ 88.5 puncte
  - Interval tipic: 87–91
  - Interval după filtrare: 82–95

- **Alcool (`alcohol`)**
  - Medie ≈ 13.55%
  - Majoritatea vinurilor între 13.5% și 14% alcool.

- **Raport preț/calitate (`quality_price`)**
  - Medie ≈ 3.73
  - Interval după filtrare: aproximativ 0.9–9.4

Figura de mai jos prezintă histograme + boxplot-uri pentru fiecare variabilă numerică (după curățare):

![Statistici descriptive variabile numerice](./figures/stat_descriptiva_numerice.pdf)

---

#### 4. Analiza pe țări

Setul de date acoperă vinuri din zeci de țări, însă distribuția este foarte dezechilibrată.

- Țările cu cele mai multe vinuri:
  - **United States** (~24.900)
  - **France**, **Italy**, **Spain**
  - Urmate de **Portugal**, **Australia**, **Chile**, **Argentina**, **South Africa**, **New Zealand** etc.

Distribuția generală pe țări:

![Distribuția vinurilor pe țări – dashboard](./figures/distributie_tari.pdf)

Au fost analizate:

1. **Top țări după număr de vinuri**, **preț mediu** și **punctaj mediu**.
2. Raportul dintre prețul mediu și punctajul mediu la nivel de țară.
3. Țările cu cel mai bun raport preț/calitate.

Dashboard pentru:
- top țări după număr de vinuri,
- top țări după preț mediu,
- top țări după punctaj mediu,
- scatter `mean_price` vs. `mean_points` (mărimea punctului = nr. de vinuri):

![Dashboard distribuție pe țări](./figures/distributie_tari.pdf)

Analiza comparativă punctaj/preț pe țări:

![Punctaj și preț mediu pe țări](./figures/distributie_punctaj_pret_tari.pdf)

Relația preț mediu – punctaj mediu pe țări (mărimea bulinei = număr de vinuri, culoarea = număr de vinuri sau punctaj mediu):

![Preț mediu vs. punctaj mediu pe țări](./figures/pret_vs_punctaj_tari.pdf)

##### Raport preț/calitate pe țări

A fost calculată media `quality_price` pe țări (filtrând țările cu un număr minim de vinuri, ex. ≥ 10):

- Țările cu **cel mai bun** `quality_price` mediu includ:
  - **Chile**, **Argentina**, **South Africa**, **Portugal**, **Spain**, **Australia** etc.
- Țările cu `quality_price` mediu mai mic tind să aibă vinuri mai scumpe sau orientate spre premium (ex.: **England**, **Canada**, **United States** etc.).

Dashboard raport preț/calitate pe țări:

![Raport preț/calitate per țară](./figures/raport_pret_calitate_per_tari.pdf)

---

#### 5. Analiza pe categorii de vin

Câmpul `category` include: `Red`, `White`, `Rose`, `Sparkling`, `Dessert`, `Port/Sherry`, `Orange`, `Fortified`.

Distribuția numerică:

- **Red**: ~68.4% din eșantion
- **White**: ~24.8%
- **Rose**: ~3.1%
- **Sparkling**: ~2.4%
- Restul categoriilor: sub 1% fiecare.

Figura de sinteză pe categorii (număr, punctaj mediu, preț mediu și `quality_price` mediu):

![Distributia și statistici pe categorii](./figures/distributia_per_categorie.pdf)

Observații generale:

- Vinurile **Red** domină numeric și au un punctaj mediu solid (~88.6) cu preț mediu ~32 USD.
- Vinurile **White** și **Rose** tind să aibă:
  - prețuri medii mai mici,
  - valori medii `quality_price` mai bune (mai multe puncte pe dolar).
- **Dessert** și **Port/Sherry** au prețuri mai mari în medie și punctaje ridicate, dar `quality_price` ceva mai mic (vinuri scumpe și premium).

---

#### 6. Analiza pe regiuni (province)

Pentru provincii (ex.: **California**, **Washington**, **Bordeaux**, **Tuscany**, **Piedmont**, **Burgundy** etc.), au fost analizate:

- Punctajul mediu pe provincie
- Prețul mediu pe provincie
- Numărul de vinuri per provincie (cu filtrare la minim 20–30 vinuri/provincie)

Top regiuni după număr de vinuri: **California**, **Washington**, **Oregon**, **Bordeaux**, **Tuscany**, **Piedmont**, **Burgundy**, **Veneto**, etc.

Punctaj mediu pe regiune:

![Punctaj mediu pe regiune](./figures/punctaj_med_pe_regiune.pdf)

Preț mediu pe regiune:

![Preț mediu pe regiune](./figures/pret_mediu_pe_regiune.pdf)

---

#### 7. Analiza pe soiuri (variety)

Au fost analizate soiurile cu cel puțin 30 de vinuri:

- Soiuri foarte frecvente:
  - **Pinot Noir**, **Chardonnay**, **Cabernet Sauvignon**, **Red Blend**,
  - **Bordeaux-style Red Blend**, **Syrah**, **Sauvignon Blanc**, **Merlot**, **Riesling**, **Zinfandel** etc.

Punctaj mediu pe soi:

![Punctaj mediu pe soi](./figures/punctaj_med_pe_soi.pdf)

Preț mediu pe soi:

![Preț mediu pe soi](./figures/pret_med_pe_soi.pdf)

Observații:
- Anumite soiuri (ex. anumite Pinot Noir, Bordeaux-style blends) tind să combine punctaj mediu ridicat cu prețuri ridicate.
- Soiuri cu bun raport preț/punctaj pot fi identificate comparând aceste două diagrame.

---

#### 8. Distribuția punctajelor

Distribuția `points` arată o concentrație puternică în intervalul 86–92 puncte, cu coadă spre 95+ puncte.

![Distribuția punctajelor](./figures/distributia_punctajelor.pdf)

---

#### 9. Analiza descrierilor text (NLP simplu)

##### 9.1. Curățare și tokenizare

- Descrierile sunt transformate la lowercase.
- Se păstrează doar litere și spații, se elimină caractere speciale.
- Se aplică tokenizare (`word_tokenize`).
- Se elimină stopwords în engleză și un set de cuvinte specifice domeniului:
  - `wine`, `wines`, `flavors`, `aromas`, `drink`, `note`, `notes`, `finish`,
  - `palate`, `nose`, `style`, `and`, `the`, `this` etc.

##### 9.2. Cuvinte cele mai frecvente (fără stopwords)

Cele mai frecvente cuvinte (top ~30) includ:

- `fruit`, `tannins`, `acidity`, `cherry`, `black`,
- `ripe`, `nose`, `red`, `oak`, `spice`,
- `rich`, `dry`, `fresh`, `full`, `sweet`,
- `berry`, `plum`, `blackberry`, `apple`, `vanilla`, `texture` etc.

##### 9.3. Lungimea descrierilor

- Lungime medie ≈ 39 de cuvinte.
- Lungime mediană ≈ 39 de cuvinte.
- Lungime medie în caractere ≈ 221.

Distribuția lungimii descrierilor (număr de cuvinte):

![Distribuția lungimii descrierilor](./figures/distributia_ligimii_descrierilor.pdf)

##### 9.4. Wordcloud

Wordcloud generat din toate cuvintele (fără stopwords), evidențiind termenii cei mai proeminenți:

![Wordcloud descrieri vinuri](./figures/worldcould_descrieri.pdf)

##### 9.5. Corelația între cuvinte din descriere și metrice (price, points, quality_price)

Pentru un set de cuvinte candidate (frecvente și relevante), a fost calculată diferența de medie între vinurile **care conțin** cuvântul și cele **care nu îl conțin**, pentru:

- `price`
- `points`
- `quality_price`

Exemple de pattern-uri:

- Cuvinte asociate cu **punctaj mai mare și preț mai mare**, dar raport preț/calitate mai slab:
  - `rich`, `black`, `tannins`, `cherry` – indică vinuri mai scumpe și cu punctaj mai mare, dar de multe ori cu `quality_price` mai mic (plătești mai mult pe punct).

- Cuvinte asociate cu **preț mai mic** și `quality_price` mai bun:
  - `fresh`, `sweet`, `berry` – tind să apară în descrieri de vinuri mai ieftine, uneori cu punctaj similar sau puțin mai mic, dar cu raport preț/calitate mai bun.

Heatmap cu diferențele de medii:

![Heatmap diferențe de medii cuvinte–metrice](./figures/heatmap_diff_med_candidate_words.pdf)

---

#### 10. Analiza corelațiilor între variabile numerice

A fost construită matricea de corelații pentru: `price`, `points`, `alcohol`, `quality_price`.

![Matricea de corelații (numerice)](./figures/matrice_corelatii.pdf)

Principalele corelații (după filtrarea outlierilor):

- `price` vs `points`: ~0.44  
  → Vinurile mai scumpe tind, în medie, să aibă punctaje mai mari, dar relația nu este foarte puternică.
- `price` vs `quality_price`: ~-0.82  
  → Cu cât vinul este mai scump, cu atât raportul puncte/preț este mai slab (plătești mai mult pe fiecare punct).
- `points` vs `quality_price`: ~-0.44  
  → Vinurile cu punctaj foarte mare tind să aibă un raport puncte/preț mai slab (sunt premium).
- `alcohol` are corelații modeste cu `price` și `points`.

---

#### 11. Distribuția vinurilor pe țări/regiuni și categorii

##### 11.1. Țări × categorii (număr absolut)

Distribuția numărului de vinuri pe **țară** și **categorie** (stacked bar):

![Distribuția vinurilor după categorii și țări](./figures/distributia_dupa_categorii_si_tari.pdf)

##### 11.2. Țări × categorii (proporții)

Aceeași analiză, dar în termeni procentuali (pe fiecare țară):

![Distribuția relativă a categoriilor pe țări](./figures/distributia_dupa_categorii_si_tari_relativ.pdf)

##### 11.3. Regiuni (province) × categorii (număr absolut)

![Distribuția vinurilor după categorii și regiuni](./figures/distributia_dupa_categorii_si_regiuni.pdf)

##### 11.4. Regiuni (province) × categorii (proporții)

![Distribuția relativă a categoriilor pe regiuni](./figures/distributia_dupa_categorii_si_regiuni_relativ.pdf)

Aceste grafice permit identificarea:

- Țărilor și regiunilor dominate de vinuri roșii vs. albe vs. spumante etc.
- Țărilor/regiunilor cu portofoliu mai divers sau mai specializat.

---

#### 12. Relația preț–punctaj (la nivel agregat de țară)

Relația `mean_price` vs `mean_points` pe țări este ilustrată în:

![Preț vs punctaj mediu pe țări](./figures/pret_vs_punctaj_tari.pdf)

Observații de ansamblu:

- Există o tendință clară: țările/zonele cu vinuri mai scumpe au în medie punctaje mai mari.
- Totuși, există țări (ex. Chile, Argentina) cu combinație avantajoasă între punctaj mediu bun și preț mediu relativ mic – deci `quality_price` ridicat.

---

#### 13. Concluzii și legătura cu aplicația Streamlit

1. **Structura datelor**:  
   - Dataset mare, bogat, bine structurat, fără valori lipsă pe coloanele cheie.
   - Prelucrarea outlierilor și definirea lui `quality_price` fac analizele mult mai robuste și interpretabile.

2. **Insight-uri principale**:
   - **Raport preț/calitate**: țări precum **Chile**, **Argentina**, **South Africa**, **Portugal** oferă, în medie, un `quality_price` ridicat.
   - **Distribuția categoriilor**: vinurile roșii domină numeric; vinurile albe și rose tind să ofere un raport puncte/preț mai bun în medie.
   - **Corelații**: prețul este moderat corelat cu punctajul, însă puternic negativ cu `quality_price`.
   - **Descrieri text**: anumite cuvinte din descriere pot fi indicii pentru poziționarea vinului (premium vs. bun raport calitate/preț).

3. **Aplicația Streamlit (`app.py`)**:
   - Încorporează toată logica de preprocesare definită în notebook.
   - Permite:
     - Filtrare interactivă după țară, categorie, interval de preț, punctaj, alcool, `quality_price`.
     - Vizualizări dinamice similare cu cele din notebook (distribuții, scatter, heatmap de corelații).
     - Analiză pe țări, regiuni, categorii și raport preț/calitate.
     - Analiză text (wordcloud, tabele cu cuvinte frecvente, heatmap cu cuvinte vs. metrice).
     - Căutare de vinuri după descriere text folosind TF‑IDF și cosine similarity – practic un motor de recomandări bazat pe textul dorit de utilizator.

Prin acest raport, notebook-ul și aplicația Streamlit sunt aliniate: notebook-ul documentează clar pașii de analiză și concluziile, iar aplicația oferă un mod interactiv de a explora aceleași idei pe subseturi de date sau pentru cazuri specifice.
