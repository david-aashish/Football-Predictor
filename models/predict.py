"""
predict.py

Train all models on the full historical dataset
and predict the 2026 FIFA World Cup.

Output:
    predictions/
        logistic_regression_predictions.csv
        random_forest_predictions.csv
        xgboost_predictions.csv
"""

import pandas as pd
from pathlib import Path

from utils.preprocessing import preprocess_dataset, scale_features
from utils.models import (
    get_logistic_regression,
    get_random_forest,
    get_xgboost,
)

TRAIN_FILE = Path("data/processed/world_cup_dataset.csv")

PREDICT_FILE = Path("data/processed/world_cup_dataset_2026.csv")

OUTPUT_DIR = Path("predictions")

# ==========================================================
# Load
# ==========================================================

train_df = pd.read_csv(TRAIN_FILE)
predict_df = pd.read_csv(PREDICT_FILE)

# Save team names

teams = predict_df["Team"].copy()

# ==========================================================
# Preprocess
# ==========================================================

train_df = preprocess_dataset(train_df)
predict_df = preprocess_dataset(predict_df)

X_train = train_df.drop(columns=["Winner", "Year", "Team"])
y_train = train_df["Winner"]

X_predict = predict_df.drop(columns=["Year", "Team"])

# ==========================================================
# Models
# ==========================================================

models = {

    "logistic_regression": get_logistic_regression(),

    "random_forest": get_random_forest(),

    "xgboost": get_xgboost()

}

OUTPUT_DIR.mkdir(exist_ok=True)

champions = []

print("=" * 80)
print("FIFA WORLD CUP 2026 PREDICTIONS")
print("=" * 80)

for name, model in models.items():

    print()
    print("#" * 80)
    print(name.upper())
    print("#" * 80)

    X_predict = X_predict.reindex(columns=X_train.columns, fill_value=0)
    
    # Logistic needs scaling

    if name == "logistic_regression":

        X_train_scaled, X_predict_scaled = scale_features(
            X_train,
            X_predict
        )

        model.fit(X_train_scaled, y_train)

        probabilities = model.predict_proba(
            X_predict_scaled
        )[:, 1]

    else:

        model.fit(X_train, y_train)

        probabilities = model.predict_proba(
            X_predict
        )[:, 1]

    predictions = pd.DataFrame({

        "Team": teams,

        "Probability": probabilities

    })

    predictions = predictions.sort_values(
        "Probability",
        ascending=False
    ).reset_index(drop=True)

    predictions.index += 1

    print(predictions.head(10))

    champion = predictions.iloc[0]["Team"]

    champions.append(champion)

    print()
    print(f"Predicted Champion : {champion}")

    predictions.to_csv(

        OUTPUT_DIR / f"{name}_predictions.csv",

        index_label="Rank"

    )

# ==========================================================
# Consensus
# ==========================================================

print()
print("=" * 80)
print("CONSENSUS PREDICTION")
print("=" * 80)

votes = pd.Series(champions).value_counts()

print(votes)

print()
print(f"Consensus Champion : {votes.index[0]}")