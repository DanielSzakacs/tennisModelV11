# Agents.md — TennisModelV11

## Cél

A projekt célja, hogy a teniszezők múltbeli meccsadatai alapján **megbecsüljük, ki nyeri a következő mérkőzést**, és ezt egy újrafuttatható, adatvezérelt csővezetéssel és egy egyszerű felhasználói felületen tegyük elérhetővé.

---

## Forrásadatok (datasource)

- Időtáv: **1963–2024**.
- Szerkezet: egy sor egy lejátszott mérkőzés, mezők csoportosítva \*_winner / winner\__ \*\* és \*_loser / loser\__ \*\* prefixel.
- Fontos: sok jellemzőt **időben eltolva (lag)** kell képezni, hogy ne legyen **data leakage**.

### Leakage elkerülése

- Minden „múltbeli teljesítmény” jellegű feature-t **mérkőzés-időpont előtti adatokból** kell számolni (rolling/exp. rolling ablakok).
- „Head‑to‑head” és „recent form” mutatók a meccs napjáig bezárólag számolandók.
- Idő alapú tanítás/validálás/test felosztás, **nincs véletlen keverés a teljes idősoron**.

---

## Közös elvárások és technikai keretek

- **Tech stack (requirements.txt)**: `pandas`, `numpy`, `scikit-learn`, `matplotlib`, `seaborn`, `streamlit`, `joblib`.
- **Kódstílus**: minden függvénynek legyen **docstring**‑je (röviden leírva, mit csinál; bemenet/kimenet; feltételezések).
- **Reprodukálhatóság**: rögzített random seed(ek); determinisztikus futás ahol lehetséges.
- **Fájlkezelés**: minden script **idempotens** legyen (többszöri futtatás nem rontja az állapotot).
- **Naplózás**: írjunk naplókat a `/logs` mappába (pl. `training.log`, `prep.log`).
- **Kimenő artefaktok**: modellek a `/models`, metrikák a `/reports`, előkészített adat a `/data/prep`.

### Projekt mappaszerkezet (javaslat)

```
.
├─ data/
│  ├─ raw/               # forrás (pl. atp_df.csv)
│  ├─ interim/           # átmeneti fájlok (ellenőrzés, QC)
│  └─ prep/              # véglegesített tanító-/predikciós dataset(ek)
├─ models/               # .joblib modellek és preprocesszorok
├─ notebooks/            # EDA, jegyzetek (opcionális)
├─ reports/
│  ├─ figures/           # ábrák (CM, ROC stb.)
│  └─ metrics/           # JSON/CSV metrikák
├─ scripts/
│  ├─ make_dataset.py    # adat-előkészítő pipeline (Data Engineer)
│  └─ train_models.py    # modellek tanítása (ML Engineer)
├─ app.py                # Streamlit frontend (Frontend Agent)
├─ requirements.txt
└─ README.md
```

---

## Szerepkörök, feladatok, átadások

### 1) Data Analyst Agent

**Fő feladat**: Forrásadatok feltérképezése, tisztítás, hiányok/outlierek kezelése, új jellemzők tervezése.

**Tevékenységek**

- **Adatminőség**: hiányzó értékek azonosítása; pótlás **mediánnal** (player‑szintű medián, ha elérhető, különben globális), vagy a megjelölt szabályok szerint sorok/mezők eldobása.
- **Outlierek**: robusztus szabályok (pl. IQR/med. abs. dev.) szerinti jelölés; szélsőségek csonkolása (winsorization) vagy eltávolítása indoklással.
- **EDA**: alap statisztikák; időbeli trendek; felszín (surface), torna, kör (round) szerinti bontások; győztes/vesztes eloszlások.
- **Head‑to‑head**: játékospárok egymás elleni története (győzelem/vereség számláló, utolsó találkozók).
- **Feature‑tervezés (példák)**:

  - **ELO / rating** és **rating‑különbség**.
  - **Recent form** (utolsó N mérkőzés win%); **rolling serve/return** mutatók.
  - **Age diff, rank diff**, utazási/borítás preferencia (surface win%).
  - **Head‑to‑head diff** és „clutch” mutatók (TB/deciding set statisztikák, ha elérhető).

- **Időkezelés**: minden aggregációt **a mérkőzés dátuma előtti adatokból** számít (lag, rolling).

**Átadandók**

- Rövid **analitikai jegyzet** (Markdown) az észlelt adatminőségi kérdésekről és döntésekről.
- **Feature‑specifikáció** tételesen (név, definíció, ablak, szint: player/pair/match, leakage‑védelmi megjegyzés).

**Elfogadási feltételek (DoD)**

- Hiánykezelési és outlier‑szabályok dokumentálva és szkriptbe ültetve.
- Feature‑lista jóváhagyva, időbeli korrektség igazolva mintapéldákkal.

---

### 2) Data Engineer Agent

**Fő feladat**: Újrafuttatható, idempotens **adat‑pipeline** megírása.

**Parancs és elvárt működés**

```bash
python scripts/make_dataset.py
```

- Bemenet: `/data/raw/atp_df.csv`.

- Lépések (magas szinten):

  1. Beolvasás, típusok és dátumok normalizálása.
  2. Tisztítás (hiányok/outlierek) a Data Analyst által lefektetett szabályok szerint.
  3. **Player‑idővonal** felépítése: időrend, lag/rolling mutatók képzése.
  4. **Párosítás standardizálása**: minden meccs **(A,B)** nézőpontú, bináris címkével (`label=1`, ha A nyer). (A és B determinisztikusan rendezve: pl. ABC sorrend, hogy ne legyen duplikáció.)
  5. **Feature engineering** implementálása (spec szerint).
  6. QC/validáció (sor- és oszlopszámok, hiányok aránya, alap eloszlások), naplózás.
  7. Kimenet mentése CSV‑be: `/data/prep/features.csv`.

- Kimenetek:

  - `/data/prep/features.csv` (tanításra és predikcióra alkalmas táblázat)
  - QC riport: `/reports/metrics/prep_summary.json`
  - Napló: `/logs/prep.log`

**Elfogadási feltételek (DoD)**

- Script többször futtatva is determinisztikus kimenetet ad.
- Oszlopnév‑szerződés dokumentálva (lásd „Feature‑szerződés”).
- Időalapú szivárgás kizárva (unit teszttel/ellenőrzéssel).

---

### 3) ML Engineer Agent

**Fő feladat**: Egy vagy több olyan modell(ek) fejlesztése, amely(ek) a mérkőzés győztesét **>= 80% pontossággal** jelzi(k) előre.

**Parancs és elvárt működés**

```bash
python scripts/train_models.py
```

- Bemenet: `/data/prep/features.csv`.
- Tanítási protokoll:

  - Időalapú felosztás (javaslat):

    - **Train**: 1963–2022.12.31
    - **Validáció**: 2023
    - **Teszt**: 2024

  - **TimeSeriesSplit** vagy „expanding window” CV.
  - Cél: bináris `label` (A nyer?) és **valószínűség** becslés.

- Modellek (példák, tetszőleges kombináció):

  - `LogisticRegression`, `RandomForestClassifier`, `GradientBoostingClassifier`/`XGBoost` helyett GB baseline scikit‑learnben (ha XGBoost nincs a requirements‑ben, maradjunk sklearn‑nél), `SVC(probability=True)`.
  - **Ensemble**: soft‑voting a legjobb 2–3 modellre.

- **Hyperparaméter‑kutatás**: `GridSearchCV` / `RandomizedSearchCV` a CV‑sémán.
- **Metrikák**: `accuracy`, `roc_auc`, `log_loss`, `precision/recall`, kalibrációs görbe. Követelmény: **accuracy ≥ 0.80** a teszten.
- **Kimenetek**:

  - Legjobb modell(ek) és preprocesszor(ok): `/models/model.joblib` (vagy `model_*.joblib`).
  - Metrikák: `/reports/metrics/train_results.json` + osztási dátumok.
  - Ábrák: `/reports/figures/{confusion_matrix, roc_curve, calibration}.png`.
  - Napló: `/logs/training.log`.

**Elfogadási feltételek (DoD)**

- Script hiba nélkül fut, elmenti az artefaktokat, naplóz.
- Tesztkészlet‑eredmények dokumentálva; **≥80% pontosság** teljesül vagy indokolt iterációs terv a javításhoz.
- Modellek `joblib`‑bal tölthetők és `predict_proba`‑t adnak.

---

### 4) Frontend Agent

**Fő feladat**: Streamlit alapú felület, ahol a felhasználó két játékost kiválaszt, és megkapja a **győzelmi valószínűséget**.

**Követelmények**

- Az alkalmazás: `app.py` (Streamlit).
- UI elemek:

  - Két **dropdown** a játékosok nevére (A és B).
  - Gomb: **„Predict”**.
  - Kimenet: valószínűség (A nyer), és opcionális vizualizációk **seaborn**‑nal (eloszlások, head‑to‑head mini‑összegzés).

- Adatkiválasztás:

  - A frontend **alapértelmezésben** a kiválasztott játékosok **legfrissebb** (a /data/prep‑ben elérhető utolsó dátumig számított) feature‑vektorait adja át a modellnek.
  - Ha nincs friss rekord, jelezze a UI és kérjen alternatívát (pl. korábbi év vagy alap baseline).

- Modellbetöltés: `/models/model.joblib`.
- Megjelenítés: százalékos esély, H2H összefoglaló (ha elérhető), releváns utolsó forma.

**Elfogadási feltételek (DoD)**

- `streamlit run app.py` alatt indul, hiba nélkül.
- Modell betöltése és predikció működik.
- Input‑védelem (A ≠ B), hiányzó modell/adat esetén barátságos üzenet.

---

## Feature‑szerződés (részlet minta)

A `/data/prep/features.csv` minimális oszlopai:

| Oszlop                                                        | Típus      | Leírás                                                           |
| ------------------------------------------------------------- | ---------- | ---------------------------------------------------------------- |
| `match_id`                                                    | string/int | Egyedi azonosító (forrásból vagy konstruált).                    |
| `date`                                                        | date       | Mérkőzés dátuma.                                                 |
| `player_a`, `player_b`                                        | string     | Játékosnevek/azonosítók.                                         |
| `label`                                                       | int {0,1}  | 1, ha `player_a` nyer; különben 0.                               |
| `elo_a`, `elo_b`, `elo_diff`                                  | float      | ELO és különbsége a dátum előtt számítva.                        |
| `h2h_a_over_b`, `h2h_b_over_a`, `h2h_diff`                    | int/float  | Egymás ellen eddigi mérleg a meccs napjáig.                      |
| `recent_winrate_a`, `recent_winrate_b`, `recent_winrate_diff` | float      | Utolsó N (pl. 10) meccs win%.                                    |
| `surface_winrate_*`                                           | float      | Borítás szerinti win% (a dátum előtt).                           |
| `rank_a`, `rank_b`, `rank_diff`                               | float/int  | Hivatalos ranglista ha elérhető; különbség.                      |
| `age_a`, `age_b`, `age_diff`                                  | float      | Életkor a meccs napján.                                          |
| `serve_*`, `return_*`                                         | float      | Rolling szerválási/visszafogadási mutatók (pl. pont%/BP mentés). |

> Megjegyzés: minden `*_diff = *_a - *_b`.

---

## Parancsok összefoglaló

```bash
# 1) Adat-előkészítés
python scripts/make_dataset.py

# 2) Modellek tanítása
python scripts/train_models.py

# 3) Frontend (lokális)
streamlit run app.py
```

---

## Minőségbiztosítás

- **Unit/integ tesztek** kulcs lépésekre (lag/rolling korrekt‑e; duplikációk nincsenek; label helyes).
- **Validációs ellenőrzőlista**: nincs jövőből származó adat; hiányok aránya elfogadható; metrikák rögzítve.
- **Naplók és riportok**: futásidő, sor-/oszlopszámok, hibák figyelmeztetések.

---

## Kódolási irányelvek (rövid)

- Docstring minden függvényhez (cél, bemenet/kimenet, kivételek).
- Tiszta függvények, ahol lehet (mellékhatás minimalizálása).
- Paraméterezhetőség: konstansokat tegyük a fájl elejére vagy parse‑oljuk CLI‑ből.
- Random seed(ek) központosítva (pl. `RANDOM_STATE=42`).

---

## Elfogadási kritériumok összesítve

- [ ] Adat‑pipeline újrafuttatható, idempotens, dokumentált.
- [ ] Feature‑k időben helyesek, leakage kizárva.
- [ ] Tesztkészlet **pontosság ≥ 80%**.
- [ ] Artefaktok és riportok mentve a megfelelő mappákba.
- [ ] Streamlit frontend működik, két játékos kiválasztható, esély megjelenik.

---

## Megjegyzések

- Ha a 80% pontosság tartósan nem érhető el, javasolt: további feature‑k (pl. turné‑intenzitás, utazási távolságok), kalibráció (`CalibratedClassifierCV`), és/vagy egyszerűbb **stacking** ensemble.
- A teljes folyamat legyen **önállóan dokumentálható** a `README.md`‑ben rövid indoklásokkal és futtatási példákkal.
