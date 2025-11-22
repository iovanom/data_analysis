# Analiza Interactivă a Energiei – Lucrare de laborator Nr. 1

**Autor:** _[Ivan Majeru](https://github.com/iovanom)_
**Data:** _\[2025-11-22\]_

## 1\. Obiectivul lucrării

Scopul acestei lucrări de laborator este analiza unui set de date reale despre producerea și consumul energiei electrice în România și realizarea unei aplicații web interactive pentru explorarea acestor date.\
Am urmărit:

* preprocesarea și îmbogățirea datelor cu componente de timp;

* analiza statistică și vizuală a principalelor tipuri de energie;

* explorarea relației dintre producție și consum;

* dezvoltarea unei aplicații în Streamlit cu filtre și grafice interactive, inclusiv generarea unui raport PDF automat.

## 2\. Setul de date și preprocesare

### 2.1. Sursa și perioada

Datele au fost preluate de pe site-ul oficial [sistemulenergetic.ro](http://sistemulenergetic.ro), folosind endpoint-ul de export:

* URL bază: `https://sistemulenergetic.ro/statistics/export/`

* Intervalul de timp este specificat în URL prin calea:

  `YYYY/MM/DD/HH/MM/YYYY/MM/DD/HH/MM`

În notebook am lucrat cu un fișier CSV (`data.csv`) care conține un eșantion de 1394 de înregistrări, cu perioada cuprinsă între anul 2024 și 2025.\
În aplicația Streamlit, perioada este aleasă din interfață, iar datele sunt descărcate direct la runtime, pentru intervalul selectat de utilizator.

### 2.2. Structura datelor

Dataset-ul conține inițial următoarele coloane:

* `date` – timestamp

* `carbune`

* `consum`

* `hidro`

* `hidrocarburi`

* `nuclear`

* `eolian`

* `productie`

* `fotovolt`

* `biomasa`

* `stocare`

* `sold`

După conversia `date` la `datetime64[ns]`, am extras componentele temporale:

* `an`, `luna`, `zi`, `ora`, `minute`, `ziSapt` (0 = luni, ..., 6 = duminică)

Toate coloanele numerice sunt de tip `int64`/`int32`. Nu au fost identificate:

* valori lipsă (`isnull().sum() == 0` pe toate coloanele);

* rânduri duplicate (`data[data.duplicated()]` este DataFrame gol).

### 2.3. Tipuri de energie și statistici de bază

Tipurile de energie considerate sunt:

* `carbune`, `hidro`, `hidrocarburi`, `nuclear`, `eolian`, `fotovolt`, `biomasa`.

Pentru aceste variabile am calculat:

* statistici descriptive (`describe().T`);

* agregări suplimentare: `min`, `max`, `sum`, `mean`, `median`, `std` și coeficientul de variație `cv = std / mean`;

* contribuția relativă la producția totală (prin raportarea sumei fiecărei surse la total).

Rezultatele arată, în linii mari, că:

* **hidro** și **nuclear** au cele mai mari volume totale de producție și contribuie semnificativ la mixul energetic;

* **hidrocarburi** și **carbune** sunt, de asemenea, surse importante;

* **eolian** și în special **fotovolt** au o variabilitate mult mai ridicată (coeficienți de variație mari);

* **biomasa** are o contribuție relativ mică la total.

## 3\. Analiză exploratorie și corelații

### 3.1. Profil orar pe tipuri de energie

În notebook și în aplicația Streamlit am construit un **heatmap orar**:

* am copiat datele în `df_clean` și am tăiat valorile negative la 0 pentru tipurile de energie;

* am agregat media pe oră: `df_clean.groupby("ora")[tipuri].mean()`;

* am reindexat orele 0–23 și am construit un heatmap cu valori absolute (MW) și procente relative față de maximul fiecărui tip.

Observații sintetice:

* producția **fotovoltaică** este concentrată între orele de zi, cu valori maxime la orele de prânz și practic zero noaptea;

* producția **eoliană** este mai variabilă, cu vârfuri în anumite intervale orare, dar poate avea și valori foarte mici;

* **nuclear** este relativ stabil în timp, cu variații mici pe ore;

* consumul mediu orar (analizat separat) are un profil tipic cu valori mai mici noaptea și mai mari în a doua parte a zilei.

### 3.2. Profil lunar pe tipuri de energie

Am construit un **heatmap lunar**:

* agregare pe luni: `df_clean.groupby("luna")[tipuri].mean()`;

* reindexare după lunile existente și reprezentare grafică cu valori absolute și procente relative.

Observații:

* producția **fotovoltaică** este mai mare în lunile cu mai multă lumină (primăvară–vară) și scade semnificativ în lunile de iarnă;

* producția **hidro** prezintă variații sezoniere, influențate probabil de regimul hidrologic (de ex. debitele râurilor);

* celelalte surse (nuclear, carbune, hidrocarburi) au variații mai moderate la nivel lunar.

### 3.3. Producția lunară pe tipuri

Am agregat datele la nivel **(an, lună)** și am creat o serie tip „YYYY-MM”:

* `monthly = data.groupby(['an', 'luna'])[tipuri].sum()`

* `monthly_melt` pentru a putea reprezenta toate tipurile pe același grafic cu Plotly.

Graficul „**Producția lunară pe tipuri**” permite compararea directă între sursele de energie de la o lună la alta și evidențiază:

* care surse cresc în anumite perioade (de ex. fotovoltaic primăvara–vara);

* surse care mențin un nivel mai constant (nuclear).

### 3.4. Sold energetic și medii mobile

Am studiat indicatorul `sold` (diferența dintre producție și consum) prin:

1. **Soldul zilnic pentru 2024 și 2025** – agregare la nivel de zi, linie comparativă între ani.

2. **Seria temporală pe sold** – grafic în timp la rezoluție orară, cu două medii mobile:

* `sold_ma7` – media mobilă pe 7 zile;

* `sold_ma30` – media mobilă pe 30 de zile.

1. **Sold energetic cu benzi de confidență** – pe baza unei ferestre de 7 zile:

* `sold_mean`, `sold_std`;

* benzi `upper_band = mean + 2*std`, `lower_band = mean - 2*std`.

Aceste vizualizări permit:

* identificarea perioadelor cu **surplus** sau **deficit** de energie;

* observarea dacă `sold` iese frecvent din benzile ±2σ (zone de potențială anomalie sau episoade extreme).

### 3.5. Consum, producție și corelații

Am analizat relația dintre consum și producție prin mai multe grafice:

* **Consum vs Producție în timp** – linii suprapuse `consum` și `productie`, cu posibilitate de zoom prin `rangeslider`;

* **Scatter Consum vs Producție** – puncte (`consum`, `productie`) cu trendline de regresie liniară;

* **Raport Producție / Consum** – linie în timp a raportului `productie / consum`, cu o linie de referință `y = 1`.

În plus, am calculat **consumul mediu pe zilele săptămânii**:

* maparea `ziSapt` → numele zilei (Luni–Duminică);

* agregare `mean` și reprezentare prin bar chart.

În general:

* există o **corelație pozitivă** clară între consum și producție (graficul scatter cu trendline);

* raportul producție/consum oscilează în jurul valorii 1, ceea ce indică alternanța perioadelor de **ușor surplus** cu cele de **ușor deficit**;

* consumul mediu este relativ similar între zile, cu mici variații între zile lucrătoare și weekend.

## 4\. Aplicația Streamlit

Aplicația poate fi accessat pe adresa [https://lab1-viz-date.monitor.majeru.org/](https://lab1-viz-date.monitor.majeru.org/).

### 4.1. Structura și filtre

Aplicația a fost dezvoltată în Streamlit și poartă titlul **„Analiza Interactivă a Energiei”**.

Principalele elemente ale interfeței:

* **Bară laterală (`st.sidebar`)** cu:

  * **Selecție interval de date** (`st.sidebar.date_input`):

    * implicit: de la 1 ianuarie anul trecut până la data curentă;

    * utilizatorul poate schimba capetele intervalului.

  * **Selecția tipurilor de energie** (`st.sidebar.multiselect`):

    * listă cu: `carbune`, `hidro`, `hidrocarburi`, `nuclear`, `eolian`, `fotovolt`, `biomasa`;

    * toate sunt selectate implicit, dar utilizatorul poate filtra doar anumite surse.

Pe baza alegerilor, aplicația construiește dinamically URL-ul de descărcare:

```text
BASE_URL + "YYYY/MM/DD/HH/MM/YYYY/MM/DD/HH/MM"
```

și încarcă datele direct de pe [sistemulenergetic.ro](http://sistemulenergetic.ro).

### 4.2. Preprocesare și afișare de date

După descărcare:

* coloana `date` este convertită la `datetime`;

* se extrag `an`, `luna`, `zi`, `ora`, `minute`, `ziSapt` (la fel ca în notebook);

* se construiește lista de coloane afișate `filterd_colums`, astfel încât, dintre tipurile de energie, să fie incluse doar cele selectate de utilizator.

Aplicația afișează:

* **Tabelul de bază** pentru perioada selectată („Datele pentru perioada selectată”);

* **Date agregate** pentru tipurile de energie selectate:

  * `min`, `max`, `sum`, `mean`, `median`, `std`.

### 4.3. Vizualizări interactive

Aplicația reproduce și adaptează principalele vizualizări din notebook, dar ținând cont doar de sursele selectate:

1. **Heatmap orar** – „Profil orar mediu pe tipuri de energie”

* agregare `groupby("ora").mean()` pentru coloanele selectate;

* valorile negative sunt tăiate la 0;

* heatmap Seaborn integrat în Streamlit cu `st.pyplot`.

1. **Heatmap lunar** – „Profil lunar mediu pe tipuri de energie”

* agregare `groupby("luna").mean()` pentru tipurile selectate;

* reprezentare tot cu Seaborn și `st.pyplot`.

1. **Producția lunară pe tipuri**

* agregare `groupby(['an', 'luna']).sum()` pentru tipurile selectate;

* crearea coloanei `year_month` (format „YYYY-MM”);

* transformare `melt` și grafic interactiv Plotly (`px.line`) integrat cu `st.plotly_chart`.

Astfel, utilizatorul poate analiza:

* cum se distribuie, în medie, producția pe ore și luni;

* cum evoluează în timp producția lunară pentru fiecare tip de energie, în funcție de intervalul de timp și tipurile selectate.

### 4.4. Generarea raportului PDF

Aplicația include un buton în sidebar: **„Generează raport PDF”**.

La apăsarea lui:

1. se generează un **profil automat al datelor** folosind `ydata_profiling.ProfileReport`, cu:

* titlu „Profil date energie”;

* opțiuni `explorative=True, minimal=True` (pentru un raport compact);

1. raportul este salvat temporar ca HTML;

2. HTML-ul este convertit în **PDF** cu `pdfkit.from_file`;

3. PDF-ul este pus la dispoziție printr-un `download_button` în sidebar, cu un nume de fișier de forma:

`raport_energie_YYYYMMDD_HHMM.pdf`

Prin această funcționalitate, utilizatorul poate descărca rapid un raport descriptiv complet pentru datele curente (inclusiv statistici, distribuții, corelații etc.).

## 5\. Rezultate și concluzii

Pe baza analizelor și vizualizărilor realizate, se pot formula următoarele concluzii principale:

* Mixul energetic este dominat de sursele **hidro** și **nuclear**, care au cele mai mari volume totale de producție și joacă un rol de bază în acoperirea consumului.

* Producția **fotovoltaică** este puternic dependentă de oră și de lună: valorile sunt aproape nule noaptea și ating maxime în intervalul diurn, cu producție sporită în lunile de primăvară-vară.

* Producția **eoliană** este mult mai volatilă decât sursele convenționale, cu variații mari atât între ore, cât și între luni.

* Relația dintre `consum` și `productie` este puternic corelată pozitiv, însă raportul producție/consum variază în jurul valorii 1, ceea ce indică alternanța perioadelor de **ușor surplus** cu cele de **ușor deficit**.

* Analiza `sold` (diferența producție–consum) și a benzilor de confidență arată existența unor episoade în care soldul se îndepărtează semnificativ de medie, ceea ce poate fi interpretat ca perioade de stres pentru sistem sau de export/import pronunțat.

Aplicația Streamlit realizată permite explorarea interactivă a acestor fenomene, prin filtrare pe interval de timp și tipuri de energie, vizualizare de heatmap-uri orare/lunare și grafice liniare pe tipuri de producție, precum și generarea automată de rapoarte PDF.

## 6\. Limitări și direcții de dezvoltare

### 6.1. Limitări

* Analiza se bazează pe datele disponibile în intervalul considerat; nu se ține cont de factori externi precum vremea, sezonalitatea detaliată sau prețurile energiei.

* Nu s-au analizat diferențele între sectoarele de consum (industrial, rezidențial etc.), ci doar agregatele la nivel de sistem.

* Modelarea avansată (de exemplu, previziuni de consum/producție) nu a fost obiectivul principal al acestei lucrări.

### 6.2. Posibile extinderi

* Integrarea de date meteo (temperatură, radiație solară, vânt) pentru a explica mai bine variațiile pentru fotovoltaic și eolian.

* Construirea unor modele de **forecast** (de ex. serii temporale cu ARIMA/Prophet sau modele de machine learning) pentru consum și producție.

* Extinderea aplicației Streamlit cu:

  * mai multe tipuri de grafice interactive (de exemplu, comparații între ani pe același plot);

  * opțiuni de salvare a configurațiilor de filtre;

  * generarea unui raport PDF personalizat, care să includă exact graficele filtrate de utilizator.
