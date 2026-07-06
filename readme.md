# FIFA World Cup Winner Prediction using Machine Learning

## Overview

This project predicts the winner of the FIFA World Cup using Machine Learning techniques. Historical data from the FIFA World Cups (2006–2022) was collected, cleaned, engineered into meaningful features, and used to train multiple classification models. The trained models were then used to predict the winner of the 2026 FIFA World Cup.

The project follows a complete Machine Learning pipeline including data collection, preprocessing, feature engineering, model training, evaluation, feature selection, hyperparameter tuning, and final prediction.

---

## Objectives

* Build a historical FIFA World Cup dataset.
* Engineer meaningful features representing team strength.
* Compare multiple Machine Learning algorithms.
* Perform feature ablation experiments.
* Tuning Hyperparameters
* Evaluate models using Leave-One-World-Cup-Out Cross Validation.
* Predict the 2026 FIFA World Cup champion.

---

## Dataset

The dataset was created by combining information from multiple publicly available football datasets.

### Data Sources

* World Cup Results
* International Match Results
* Elo Ratings
* FIFA Rankings
* Qualification Matches

Historical tournaments included:

* FIFA World Cup 2006
* FIFA World Cup 2010
* FIFA World Cup 2014
* FIFA World Cup 2018
* FIFA World Cup 2022

The prediction dataset contains all qualified teams for the FIFA World Cup 2026.

---

## Feature Engineering

The following features were generated for every team:

* Elo Rating
* FIFA Ranking
* Qualification Matches
* Win Rate
* Draw Rate
* Loss Rate
* Goals For Per Game
* Goals Against Per Game
* Goal Difference Per Game
* Points Per Game
* Host Nation
* Confederation
* Previous World Cup Progress

---

## Feature Selection

A feature ablation study was performed to identify redundant features.

The final feature set removed:

* FIFA Rank
* Confederation
* Host
* Goal Difference Per Game
* Draw Rate
* Loss Rate
* Matches

These removals resulted in a simpler model with little to no loss in predictive performance.

---

## Machine Learning Models

Three supervised classification models were implemented.

### Logistic Regression

Used as the baseline linear classifier.

### Random Forest

Ensemble learning model using bootstrap aggregation.

### XGBoost

Gradient Boosted Decision Trees for high-performance classification.

---

## Hyperparameter Tuning

GridSearchCV was performed for:

* Random Forest
* XGBoost

Hyperparameter tuning produced only marginal improvements, so the final project uses a simplified tuned configuration for reproducibility.

---

## Evaluation Strategy

Instead of a random train-test split, the project uses:

**Leave-One-World-Cup-Out Cross Validation**

For every tournament:

* Train on all previous World Cups
* Test on one unseen World Cup

This better simulates predicting future tournaments.

Evaluation metrics:

* Accuracy
* Precision
* Recall
* F1 Score
* Confusion Matrix
* Champion Prediction Accuracy
* Champion Ranking

---

## Project Structure

```text
FIFA Predictor/

├── data/
│   ├── raw/
│   └── processed/
│
├── models/
│   ├── compare_models.py
│   ├── evaluate.py
│   ├── predict.py
│
├── scripts/
│   ├── build_dataset.py
│   ├── elo.py
│   ├── fifa_rank.py
│   ├── qualification_stats.py
│   ├── previous_wc_progress.py
│   └── ...
│
├── utils/
│   ├── config.py
│   ├── preprocessing.py
│   ├── evaluation.py
│   ├── trainer.py
│   ├── models.py
│   ├── splitting.py
│   └── ...
│
├── saved_models/
│
├── predictions/
│
├── README.md
└── requirements.txt
```

---

## Installation

Clone the repository.

```bash
git clone <repository-url>
```

Move into the project directory.

```bash
cd FIFA-Predictor
```

Install dependencies.

```bash
pip install -r requirements.txt
```

---

## Running the Project

### Evaluate a Single Model

```bash
python -m models.evaluate
```

---

### Compare All Models

```bash
python -m models.compare_models
```

---

### Predict the 2026 FIFA World Cup

```bash
python -m models.predict
```

Prediction files will be generated inside:

```text
predictions/
```

---

## Prediction Output

Each model generates a ranked list of qualified teams with their predicted championship probability.

Generated files:

* logistic_regression_predictions.csv
* random_forest_predictions.csv
* xgboost_predictions.csv

The project also reports a consensus prediction based on all models.

---

## Technologies Used

* Python
* Pandas
* NumPy
* Scikit-learn
* XGBoost

---

## Future Improvements

* Include player-level statistics.
* Incorporate betting odds and market probabilities.
* Add injury and squad availability information.
* Explore deep learning approaches.
* Update the dataset after every international window.

---

## Author

David Aashish