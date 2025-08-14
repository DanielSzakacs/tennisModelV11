## Projekt rövid leírása

Greenfield ML-projekt: férfi profi teniszmeccsek győztesének előrejelzése 1963–2024 közötti adatok alapján. Forrás CSV: `data/raw/atp_df.csv` (nyers, tisztítatlan). A végcél egy front-end, ahol a felhasználó két játékos nevét kiválasztja, és a rendszer(ek) valószínűségi előrejelzést adnak a győztesre (≥80% pontosság valós, időben visszatartott teszten).

## Célmetrika és elvárások

- **Elsődleges metrika:** pontosság (accuracy) és Brier-score **időalapú, „out-of-time”** teszten (pl. train ≤2019, valid 2020–2022, test 2023–2024).
- **Küszöb:** ≥80% accuracy a 2023–2024 teszten (best-of-3 és best-of-5 külön riportálva).
- **Kimenet:** kalibrált győzelmi valószínűség (0–1), + magyarázhatóság (SHAP top-10 feature).

## Adat- és entitáskezelés

- **Forrás:** `data/raw/atp_df.csv`
- **Entitás feloldás:** játékosnév → kanonikus `player_id` (névváltozatok, ékezetek, duplikátumok kezelése).
- **Szűrés:** csak ATP Tour/Grand Slam főtáblás egyéni meccsek; qualify/challenger opciósan külön modellbe.
- **Célváltozó:** `winner` ∈ {0,1} (1 = elsőként megadott “Player A” vagy a CSV `winner_name`/`w_player_id`).
- **Szivárgás elkerülése:** csak **meccs előtti** információ használható; semmi a meccs kimeneteléből/utólagos aggregátumokból a feature napjáig.

## Javasolt oszlopok (nyers → felhasználható)

Szakértői első körös döntés szükséges az alábbi csoportok alapján:

- **Meccs meta:** dátum, torna, kategória (Grand Slam/ATP 1000/500/250), forduló, pálya típusa (Hard/Clay/Grass/Indoor), város/magasság, best-of (3/5).
- **Játékosok:** győztes/vesztes nevek és (ha van) egyedi azonosítók; életkor a meccsnapon; kézhasználat; edző (ha elérhető).
- **Szervamutatók (nyersek):** `w_ace, w_df, w_svpt, w_1stIn, w_1stWon, w_2ndWon, w_bpSaved, w_bpFaced` és ugyanez `l_*`.
- **Return/egyéb mutatók:** game- és set-eredmények, tie-break jelzők.
- **Környezeti tényezők:** fedett/nyitott pálya, időjárás proxy (ha elérhető).
- **Hiányzók/outlierek:** jelölés + kezelési stratégia (ld. Data Analyst feladat).

## Feature engineering (példák)

Kétirányú (A és B játékos) feature-k, majd **különbségként** is (A−B), mert ez erős jel:

- **Szervaráták (meccs-szint, ha a CSV tartalmazza):**
  - `DoubleFault% = (df/svpt) * 100`
  - `Ace% = (ace/svpt) * 100`
  - `1stIn% = (1stIn/svpt) * 100`
  - `1stWon% = (1stWon/1stIn) * 100`
  - `2ndWon% = (2ndWon/(svpt-1stIn)) * 100`
  - **DominanceRatio = (service points won / total svpt) / (opponent’s service points won / opp_svpt)**
    - Nyers képlet variáns (a felhasználó ötlete alapján loser/winner oldalon):  
      `DR = ((l_1stWon + l_2ndWon)/l_svpt) / ((w_1stWon + w_2ndWon)/w_svpt)`
  - `BPSaved% = (bpSaved/bpFaced) * 100` (0-val osztás védelme!)
- **Idősoros aggregátumok (csak meccs előtti adatokból!):**
  - gördülő 3/6/12 hónapos teljesítmény ugyanazon/váltott borításon (W/L arány, szett/game különbség, Ace%, DF%).
  - **Head-to-Head** A vs B történelem (összesen és borításon).
  - **Elo/Surface-Elo** és rajta form-trend (ΔElo 30/90 nap).
  - Tornaszint/forduló hatások (pl. GS R16+ tapasztalat).
  - Friss meccsterhelés (utolsó 14/30 nap meccsszáma, utazási távolság proxy).
- **Környezeti featurök:** indoor flag, magasság kategória, ország/kontinens hatások.

> Megjegyzés: a felhasználó által adott képletek loser-orientált példák. A rendszer szabályosan számolja ki játékos-szinten mindkét félre, majd képezi az A−B differenciákat és a szimmetrikus H2H mutatókat.

## Modellstratégia

Több modell-paradigma, „champion–challenger”:

1. **Alapvonal:** logisztikus regresszió a kulcskülönbségekre (A−B) + regularizáció (C, penalty).
2. **Gradiens boosting:** XGBoost/LightGBM/CatBoost tabuláris jellemzőkre.
3. **Elo-család:** Surface-aware Elo, kiterjesztve H2H és korhoz igazított kimenettel; a „name-only” inferenciát az entitás-featurek biztosítják.
4. **Kalibráció:** Platt/Isotonic a validációs időszeleten.
5. **Ensemble:** súlyozott átlagolás vagy stacking (LR meta).

## Kísérleti protokoll

- **Időalapú split:** Train ≤2019, Val 2020–2022, Test 2023–2024 (fixált seed).
- **Csoport-szűrők riportja:** Surface, best-of, torna-szint, H2H megléte vs nincs.
- **Osztály-eloszlás:** winner/loser 50–50 körüli, de ellenőrzendő (up-/downsampling TILOS időszivárgás miatt).
- **Metadokumentáció:** minden feature definíciója, cut-off dátum.

## Metrikák és riportok

- Accuracy, LogLoss, Brier, AUC, **Reliability plot** (kalibráció), **Confusion**.
- Csoportonkénti bontás (surface, best-of-3/5, rangsor decilis).
- **Explainability:** globális és lokális SHAP top-10.
- **Model card** + leírás a korlátokról és adatelfogultságokról.

## Munkafolyamat és handoffok

### 1) Tennis Szakértő Agent

Feladatok:

- A nyers oszlopok áttekintése, hasznos/tiltólista (adat-szivárgás gyanús oszlopok listája).
- Minimum szükséges meta-oszlopok kijelölése (date, tournament, round, surface, best-of, player names/ids).
  Kimenetek:
- `docs/columns_decision.md`
- `docs/leakage_watchlist.md`

### 2) Data Analyst Agent

Feladatok:

- EDA: hiányzók, outlierek, eloszlások (winner/loser), felvételi szűrések.
- Dtype normalizálás, értékegység-egyeztetés, szótárak (surface, round, level).
- Hiánykezelés terv: median/most frequent, „unknown” kategória, időablakos imputálás.
  Kimenetek:
- `notebooks/01_eda.ipynb`
- `data/processed/base.parquet` (+ adat-dokumentáció)

### 3) Data Engineer Agent

Feladatok:

- Feature pipeline (python lib vagy DAG): idősoros aggregációk **leak-proof** ablakokkal.
- Entitás-normalizálás: név→player_id, alias-map, fuzzy matching.
- Reproducibilis csomag (`src/features/`, `src/data/`), unit tesztek.
  Kimenetek:
- `src/` könyvtár modulok, `tests/`, `Makefile`, `pyproject.toml`
- `data/processed/features_train.parquet`, `features_infer.parquet`

### 4) ML Engineer Agent

Feladatok:

- Alapmodell + GBM-k család, hiperparaméter-keresés (optuna/sklearn CV **időalapú**).
- Kalibráció, ensemble, mentés (onnx/pkl), pred API (FastAPI).
- SHAP/Permutation importance riportok.
  Kimenetek:
- `models/` (verziózott), `mlruns/` (MLflow), `src/train.py`, `src/infer.py`

### 5) MLOps Agent

Feladatok:

- MLflow tracking, adat- és modellverziózás (DVC/MLflow Artifacts).
- CI (pytest, ruff, mypy), konténer (Dockerfile), infra IaC minták (opcionális).
- Monitorozás: drift, teljesítmény 2025+ éles adatokon (ha lesz feed).
  Kimenetek:
- `.github/workflows/ci.yml`, `Dockerfile`, `docs/model_card.md`

### 6) Frontend Engineer Agent

Feladatok:

- Web UI: két játékos kiválasztása (typeahead/combobox), opcionális meta (surface, best-of).
- Válasz: győzelmi valószínűség(ek), confidence/kalibráció jelzés, kulcs-featurek top-5.
- Hibakezelés: ismeretlen játékos → javasolt kanonikus név.
  Kimenetek:
- `app/` (React + Tailwind), `src/api/client.ts`, demo deploy.

## Mappa-struktúra (javaslat)

├─ data/
│ ├─ raw/atp_df.csv
│ └─ processed/
├─ src/
│ ├─ data/ # load/clean
│ ├─ features/ # leak-safe featurization
│ ├─ models/ # train/infer
│ └─ api/ # FastAPI service
├─ notebooks/
├─ models/
├─ app/ # frontend
├─ tests/
└─ docs/

## Elfogadási kritériumok

- Időalapú teszten (2023–2024) **≥80% accuracy**, és javuló Brier-score az alapvonalhoz képest.
- Kalibrációs görbe ±5% sávban 0–1 tartományban.
- Frontend: 2 névválasztás → válasz ≤1s (lokál pred), vagy ≤2s (API).
- Reprodukálhatóság: `make train` → ugyanazok a metrikák ±0.2% ingadozással.

---
