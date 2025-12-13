# Plan pentru Laborator 3: Analiza și Vizualizarea Datelor Atmosferice folosind CAMS

## Obiectiv
Realizarea unei analize și vizualizări a datelor atmosferice din Serviciul de Monitorizare a Atmosferei Copernicus (CAMS) pentru a studia indicatorii de calitate a aerului, tendințele și variațiile geografice.

## Pași ai planului

1. **Înregistrează-te pe Atmosphere Data Store (ADS) și obține API key-ul personal.**
   - Accesează https://ads.atmosphere.copernicus.eu/
   - Creează cont și obține API key-ul.

2. **Instalează pachetul `cdsapi` și configurează API-ul.**
   - Rulează `pip install cdsapi`.
   - Creează fișierul `~/.cdsapirc` cu URL și key.

3. **Selectează dataset și acordă termenii.**
   - Alege dataset relevant (ex. CAMS European air quality forecasts pentru PM2.5, NO2).
   - Acordă termenii de utilizare pe pagina datasetului.

4. **Generează codul API pentru descărcare.**
   - Folosește formularul de download din portal pentru a genera codul Python pentru regiune și perioadă aleasă (ex. Europa, ultimul an).

5. **Creează notebook Jupyter.**
   - Creează un fișier `main.ipynb` în directorul lab_3.

6. **Importă librăriile necesare.**
   - pandas, matplotlib, seaborn, geopandas, folium, cdsapi.

7. **Descarcă datele folosind API-ul.**
   - Folosește `cdsapi.Client().retrieve()` în notebook pentru a descărca datele.

8. **Preprocesează datele.**
   - Gestionează valori lipsă sau inconsistente.
   - Convertește datele temporale într-un format unificat.
   - Extrage caracteristicile relevante (niveluri poluanți, coordonate geografice).

9. **Analizează datele.**
   - Calculează statistici descriptive (medie, mediană, deviație standard) pentru nivelurile poluanților.
   - Identifică tendințe în timp pentru un poluant selectat folosind analiza seriilor temporale.
   - Comparați nivelurile poluanților în diferite regiuni.

10. **Creează vizualizări.**
    - Grafice de serii temporale pentru tendințe în timp.
    - Hărți termice pentru concentrațiile poluanților pe hartă geografică.
    - Diagrame de bare sau histograme pentru comparații între regiuni.
    - Salvează toate figurile în folderul `./figures/` (ex. ca PDF/PNG).

11. **Interpretează rezultatele.**
    - Scrie un scurt rezumat al concluziilor, evidențiind tendințe, anomalii sau modele semnificative.
    - Oferi perspective despre utilizarea informațiilor în politici de mediu sau conștientizarea publicului.

12. **Finalizează livrabilele.**
    - Exportă notebook-ul ca PDF.
    - Creează un raport de 1-2 pagini incluzând vizualizările și interpretările.

## Criterii de evaluare
- Gestionarea Datelor (25%): Calitatea preprocesării și gestionării datelor lipsă.
- Analiză (25%): Profunzimea și acuratețea analizei.
- Vizualizări (30%): Claritatea, corectitudinea și relevanța vizualizărilor.
- Interpretare (20%): Calitatea concluziilor și prezentării în raport.

## Note suplimentare
- Asigură-te că toate figurile sunt salvate în `./figures/`.
- Explorează mai multe surse de date CAMS pentru a îmbogăți analiza.