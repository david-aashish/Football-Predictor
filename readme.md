# FIFA World Cup Prediction using Machine Learning & AI

## Overview

This project predicts the FIFA World Cup champion using Machine Learning and Artificial Intelligence.

The project is being developed in multiple stages.

The first stage predicts the tournament winner **before the World Cup begins** using historical data.

Later stages introduce a live tournament engine, dynamic prediction updates after every match, tournament simulation, and an AI explanation system.

The long-term goal is to build a complete intelligent World Cup prediction platform.

---

# Project Roadmap

## ✅ Stage 1 — Static World Cup Prediction

Completed

Predict the FIFA World Cup winner before the tournament begins using historical data.

Implemented:

- Historical dataset construction
- Feature engineering
- Feature selection
- Hyperparameter tuning
- Model comparison
- Leave-One-World-Cup-Out Cross Validation
- 2026 World Cup prediction

---

## ✅ Stage 2A — Generic Live Tournament Engine

Completed

Built a generic live tournament update system capable of updating team information after every completed World Cup match.

Implemented:

- Generic tournament configuration using YAML
- Tournament state management
- Dynamic Elo updates
- Tournament statistics tracking
- Live form tracking
- Knockout elimination handling
- Feature regeneration after every match
- CLI interface
- Batch match replay
- Unit and integration testing

The architecture is tournament-independent and can be reused for future World Cups with only configuration changes.

---

## ✅ Stage 2B — Dynamic Re-Prediction

Completed

Built a live championship prediction engine that recalculates World Cup winner probabilities after every completed match using the Stage 1 Machine Learning models.

Implemented:

- Reusable prediction pipeline
- Dynamic prediction using updated tournament features
- Live probability adjustment for eliminated teams
- Probability normalization
- Automatic prediction snapshots
- Probability timeline generation
- CLI integration
- Batch replay integration
- Unit and integration testing

---

## ✅ Stage 2C — Visualization

Completed

Implemented:

- Champion probability timeline generation
- Automatic probability timeline chart
- Top-10 favorites after every prediction snapshot
- Automatic visualization refresh after every live match
- CLI visualization interface
- Edition-aware visualization outputs
- Unit and integration testing

---

## ⏳ Stage 3 — Match Prediction

Planned

Predict individual match outcomes using Machine Learning.

---

## ⏳ Stage 4 — Tournament Simulation

Planned

Monte Carlo simulation of the complete FIFA World Cup.

Includes:

- Group simulation
- Knockout simulation
- Bracket generation
- Champion probabilities

---

## ⏳ Stage 5 — AI Explanation Layer

Planned

Use Large Language Models (LLMs) to explain model predictions in natural language.

Example:

> "Why is France currently the favourite?"

---

## ⏳ Stage 6 — Deployment

Planned

Interactive web application with:

- Live probabilities
- Match predictions
- Tournament simulation
- AI explanations

---

# Dataset

Historical tournaments included:

- FIFA World Cup 2006
- FIFA World Cup 2010
- FIFA World Cup 2014
- FIFA World Cup 2018
- FIFA World Cup 2022

Prediction dataset:

- FIFA World Cup 2026 Qualified Teams

---

# Data Sources

The project combines multiple public football datasets.

- FIFA World Cup Results
- International Match Results
- Elo Ratings
- FIFA Rankings
- World Cup Qualification Results

---

# Features

The initial Machine Learning model uses only information available **before** the tournament begins.

Features include:

- Elo Rating
- Qualification Performance
- Previous World Cup Progress
- Host Nation
- Confederation

Live tournament features generated during Stage 2 are used to dynamically re-run the trained models after every completed match. The models are not retrained during the tournament; instead, updated features are passed through the existing Stage 1 models. Stage 2 visualizes these evolving championship probabilities through automatically generated timelines and summary tables.

---

# Machine Learning Models

Three supervised learning algorithms are implemented.

- Logistic Regression
- Random Forest
- XGBoost

---

# Evaluation Strategy

Instead of using a random train/test split, the project uses

**Leave-One-World-Cup-Out Cross Validation**

This better represents predicting future World Cups.

Evaluation includes:

- Accuracy
- Precision
- Recall
- F1 Score
- Champion Prediction Accuracy
- Champion Ranking

---

# Live Tournament Engine

Current capabilities:

- Initialize tournament state
- Update Elo ratings
- Track tournament statistics
- Track recent form
- Mark eliminated teams
- Generate updated feature datasets
- Dynamically recalculate championship probabilities
- Apply elimination-aware probability normalization
- Save prediction snapshots
- Generate probability timelines
- Generate probability timeline charts
- Generate top-10 favorites tables
- Automatically refresh visualizations after every live update
- Support future tournaments via configuration

---

# Project Structure

```text
FIFA Predictor/
├── data/
│   ├── raw/
│   ├── processed/
│   └── live/
│
├── live/
│   ├── adapters/
│   │   ├── cli.py
│   │   ├── batch_csv.py
│   │   └── visualize.py
│   │
│   ├── pipeline.py
│   ├── prediction.py
│   ├── snapshot.py
│   ├── timeline.py
│   ├── visualization.py
│   ├── state.py
│   ├── elo.py
│   ├── form.py
│   ├── advancement.py
│   ├── build_features.py
│   ├── initialize.py
│   └── ...
│
├── models/
│   ├── predictor.py
│   ├── predict.py
│   └── ...
│
├── predictions/
│   ├── snapshots/
│   │   └── {edition}/
│   ├── timelines/
│   └── visualizations/
│       └── {edition}/
│
├── tournaments/
│   └── wc2026.yaml
│
├── tests/
│   ├── integration_tests/
│   └── unit_tests/
│
├── utils/
├── scripts/
├── saved_models/
│
├── data_sources.md
├── pyproject.toml
├── README.md
├── requirements.txt
└── solution_architecture.doc
```

---

# Running Stage 1

Evaluate models

```bash
python -m models.evaluate
```

Compare models

```bash
python -m models.compare_models
```

Generate championship predictions

```bash
python -m models.predict
```

---

# Running Stage 2

Initialize tournament

```bash
python -m live.adapters.cli --edition wc2026 --init
```

View tournament status

```bash
python -m live.adapters.cli --edition wc2026 --status
```

Process one match

```bash
python -m live.adapters.cli \
--edition wc2026 \
--result \
--home Brazil \
--away Norway \
--home-goals 2 \
--away-goals 1 \
--round r16
```

The command automatically:

- Updates the tournament state
- Regenerates live tournament features
- Recalculates championship probabilities
- Saves a prediction snapshot
- Updates the team probability timeline

Replay multiple matches

```bash
python -m live.adapters.batch_csv \
--edition wc2026 \
--file data/raw/batch_matches.csv
```

Generate visualizations:

Visualization outputs are refreshed automatically after every live match update.

The visualization CLI can also be used to regenerate charts and tables manually whenever required.

```bash
python -m live.adapters.visualize \
--edition wc2026 \
--all
```

Stage 2 automatically generates:

```text
predictions/

├── snapshots/
│   └── wc2026/
│       ├── wc2026_snapshot_001_pre_tournament.csv
│       ├── wc2026_snapshot_002_match_001.csv
│       └── ...

├── timelines/
│   └── wc2026_probability_timeline.csv

└── visualizations/
    └── wc2026/
        ├── wc2026_probability_timeline.png
        └── wc2026_top10_by_snapshot.csv
```

---

# Testing

Stages 2A, 2B and 2C include comprehensive unit and integration tests covering:

- Live tournament engine
- Dynamic prediction pipeline
- Snapshot generation
- Probability timeline creation
- Visualization generation

Run all tests:

```bash
python -m pytest
```

---

# Technologies

- Python
- Pandas
- NumPy
- Scikit-Learn
- XGBoost
- PyYAML
- PyTest

---

# Future Work

The project will continue toward a complete AI-powered World Cup prediction platform including:

- Probability visualization dashboard
- Match prediction
- Monte Carlo tournament simulation
- AI explanations
- Interactive web dashboard

---

# Author

David Aashish