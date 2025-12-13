# Laboratorul 4 - Calitatea Aerului folosind CAMS

**Autor**: Ivan Majeru
**Titular disciplina**: Anatol Poiata
**Disciplină**: Analiza si Vizualizarea Datelor

**2025**

### Raport de analiză – Calitatea Aerului folosind CAMS

#### 1. Contextul proiectului

Acest proiect analizează datele de calitate a aerului din Serviciul de Monitorizare a Atmosferei Copernicus (CAMS), focusând pe indicatorii precum PM2.5, NO2 etc. pentru o regiune selectată (ex. Europa) și perioadă de timp.

Obiectivele principale:

1. Descărcarea și preprocesarea datelor atmosferice.
2. Analiza descriptivă și tendințe în timp.
3. Vizualizări geografice și comparații regionale.
4. Interpretare pentru politici de mediu.

#### 2. Preprocesare și curățare date

- Datele sunt descărcate folosind API-ul CAMS (cdsapi).
- Gestionarea valorilor lipsă și conversia datelor temporale.
- Filtrarea outlierilor pentru acuratețe.

#### 3. Analiza descriptivă a variabilelor

Variabile analizate: PM2.5, NO2 etc.

Caracteristici globale:

- **PM2.5**: Medie ≈ 15 µg/m³, variații în timp.

Distribuția PM2.5:

![Distribuția PM2.5](./figures/distributia_pm25.pdf)

#### 4. Analiza tendințelor în timp

Tendința PM2.5 arată variații zilnice.

![Tendința PM2.5](./figures/tendinta_pm25.pdf)

#### 5. Vizualizare geografică

Hartă termică pentru concentrațiile PM2.5.

![Hartă termică PM2.5](./figures/harta_termica_pm25.html)

#### 6. Concluzii și interpretare

Analiza evidențiază zone cu niveluri ridicate de poluanți. Aceste informații pot informa politici de reducere a emisiilor și conștientizarea publicului despre calitatea aerului.

#### 7. Aplicația Streamlit

Aplicația permite explorarea interactivă a datelor, cu filtre pentru regiuni și perioade.