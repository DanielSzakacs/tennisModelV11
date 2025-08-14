# ===== Agents.md =====

## Projekt rövid leírása

Greenfield ML-projekt: férfi profi teniszmeccsek győztesének előrejelzése 1963–2024 közötti adatok alapján. Forrás CSV: `data/raw/atp_df.csv`. **Minden sor egy már lejátszott meccs post-match statisztikáit** tartalmazza (winner/loser oldali mutatókkal). A végcél egy frontend, ahol a felhasználó két játékos nevét kiválasztja, és a rendszer(ek) kalibrált győzelmi valószínűséget adnak (≥80% accuracy időben visszatartott teszten).

## Célmetrika és elvárások

- **Elsődleges metrika:** Accuracy és Brier-score **időalapú out-of-time** teszten (pl. train ≤2019, valid 2020–2022, test 2023–2024).
- **Küszöb:** ≥80% accuracy a 2023–2024 teszten (best-of-3 és best-of-5 külön).
- **Kimenet:** kalibrált győzelmi valószínűség (0–1), magyarázhatóság (SHAP top-10).

## Kritikus anti-leakage elvek (mert a sorok post-match statok)

1. **Tárgy-meccs oszlopok (pl. `w_*`, `l_*`, set/game/bp/ace/df)** közvetlen használata **TILTOTT**. Ezek csak historikus aggregációk alapanyagaként szolgálnak **korábbi** meccsekből.
2. **Csak meccs ELŐTT elérhető információ** használható (rolling/expanding `closed='left'`).
3. **H2H, Elo** kizárólag korábbi mérkőzésekből; az aktuális sor sosem kerülhet bele.
4. **Időalapú split** (train→val→test), semmilyen jövőbeli információ nem szivároghat vissza.

## Repo-higiénia és környezet

- **.gitignore kötelező**, bináris és nagy fájlok kizárásával (pl. `*.png`, `*.jpg`, `*.gif`, `*.mp4`, `*.mov`, `*.mkv`, `*.zip`, `*.tar.gz`, `*.7z`, `*.onnx`, `*.pkl`, `models/*`, `mlruns/*`, `__pycache__/`, `.venv/`, `node_modules/`).  
  _Megjegyzés:_ a `*.csv` NINCS globálisan ignorálva; a `data/raw/atp_df.csv` a projekt része maradhat.
- **Python környezet:** pip + venv + `requirements.txt` (verziókkal). Telepítés: `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`.
- **Node környezet a frontendhez:** Node 20 LTS (npm vagy pnpm), `.env.example` a backend URL-hez.

## Adat- és entitáskezelés

- Entitás feloldás: játékosnév → kanonikus `player_id` (aliasok, diakritika, fuzzy).
- Szűrés: ATP Tour/Grand Slam főtáblás meccsek (később bővíthető).
- Célváltozó: `winner` ∈ {0,1}; A/B szerep determinisztikus (pl. névsorrend), független a CSV w/l oldalától.

## Feature engineering (historikusból, A és B külön, majd A−B)

- Szervaráták: `DoubleFault%`, `Ace%`, `1stIn%`, `1stWon%`, `2ndWon%`, `BPSaved%` (0-div guard).
- **DominanceRatio** historikusból: `(spw/svpt)/(opp_spw/opp_svpt)`.
- Forma: W-L, szett/game diff, pihenőnapok, meccsterhelés (30/90/180 nap).
- H2H (összes + surface), „days since last meeting”.
- Elo és Surface-Elo inkrementális frissítéssel.

## Modellstratégia (champion–challenger)

- Alapvonal: logisztikus regresszió A−B különbségeken.
- GBM: LightGBM/XGBoost/CatBoost + korai megállítás.
- Kalibráció: Platt/Isotonic.
- Ensemble: súlyozott átlag / stacking (LR meta).

## Kísérleti protokoll és validáció

- Train ≤2019, Val 2020–2022, Test 2023–2024.
- Leakage-tesztek (unit + e2e).
- Csoportbontások: surface, best-of, tournament level, H2H>0 vs H2H=0.

## Metrikák és riportok

- Accuracy, LogLoss, Brier, AUC, kalibrációs görbe, konfúziós mátrix.
- SHAP top-10, csoportbontások.

## Munkafolyamat és handoffok

- **Tennis Szakértő Agent:** oszlopok áttekintése, tiltólista; `docs/columns_decision.md`, `docs/leakage_watchlist.md`.
- **Data Analyst Agent:** EDA, hiánykezelés, outlierek; `notebooks/01_eda.ipynb`, `data/processed/base.parquet`.
- **Data Engineer Agent:** leak-safe feature pipeline; `src/features/`, `tests/`, `data/processed/features_*.parquet`.
- **ML Engineer Agent:** modellek, kalibráció, ensemble, MLflow; `src/train.py`, `src/infer.py`.
- **MLOps Agent:** CI, Docker, MLflow, **.gitignore**, release-ek, leakage-gate.
- **Frontend Engineer Agent:** React UI, CORS, `.env` kezelés, build és dev szerver.

## Mappa-struktúra (kiegészítve)

├─ data/
│ ├─ raw/atp_df.csv
│ └─ processed/
├─ src/
│ ├─ data/ # load/clean/split/entities
│ ├─ features/ # leak-safe featurization
│ ├─ models/ # train/tune/evaluate/ensemble
│ └─ api/ # FastAPI service
├─ app/ # React frontend (Vite + Tailwind)
├─ models/ # mentett modellek, best_params/\*.json (GITIGNORE)
├─ reports/ # teszt riportok, ábrák (PNG GITIGNORE, md maradhat)
├─ notebooks/
├─ tests/
├─ .gitignore
├─ requirements.txt
├─ Makefile
└─ docs/

## Elfogadási kritériumok (kiegészítve)

- Teszt (2023–2024) **≥80% accuracy** és jó kalibráció.
- **Leakage-tesztek zöldek**.
- **Futtatható frontend**: `npm run dev` (lokál) és `npm run build`.
- **Lokális modellgenerálás legjobb paraméterekkel**:  
  `make venv && make deps && make features && make tune && make train_best && make evaluate`  
  (a `tune` menti a best paramokat JSON-ba, `train_best` azzal tanít).
- **pip + venv + requirements.txt** használata dokumentált a README-ben.

---
