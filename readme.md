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

## 🔄 Stage 2B — Dynamic Re-Prediction

Planned

After every completed World Cup match:

- Update live features
- Re-run prediction models
- Generate new championship probabilities
- Save probability snapshots over time

---

## ⏳ Stage 2C — Visualization

Planned

Visualize how championship probabilities evolve throughout the tournament.

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

Live tournament features are added during Stage 2A but are not yet used for model training.

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

Stage 2A introduced a generic tournament engine.

Current capabilities:

- Initialize tournament state
- Update Elo ratings
- Track tournament statistics
- Track recent form
- Mark eliminated teams
- Generate updated feature datasets
- Replay completed matches
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
│   ├── tournament_config.py
│   ├── state.py
│   ├── pipeline.py
│   ├── elo.py
│   ├── form.py
│   ├── advancement.py
│   ├── build_features.py
│   └── initialize_tournament.py
│
├── tournaments/
│   └── wc2026.yaml
│
├── models/
│
├── scripts/
│
├── utils/
│
├── tests/
│
├── predictions/
│
├── saved_models/
│
├── README.md
└── requirements.txt
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

Predict the 2026 World Cup

```bash
python -m models.predict
```

---

# Running Stage 2A

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

Replay multiple matches

```bash
python -m live.adapters.batch_csv \
--edition wc2026 \
--file data/raw/batch_matches.csv
```

---

# Testing

Stage 2A includes comprehensive unit and integration tests.

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

The project will continue toward a fully dynamic AI-powered prediction system including:

- Dynamic prediction updates
- Match prediction
- Monte Carlo simulation
- AI explanations
- Interactive web dashboard

---

# Author

David Aashish