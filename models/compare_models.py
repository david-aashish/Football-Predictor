"""
compare_models.py

Compares Logistic Regression, Random Forest and XGBoost
using Leave-One-World-Cup-Out Cross Validation.
"""

import pandas as pd

from utils.data_loader import load_dataset
from utils.preprocessing import (
    preprocess_dataset,
    scale_features
)
from utils.splitting import split_dataset
from utils.models import get_model
from utils.trainer import train_model
from utils.evaluation import evaluate
from utils.config import MODELS

# ==========================================================
# Load Data
# ==========================================================

df = load_dataset()

df = preprocess_dataset(df)

years = sorted(df["Year"].unique())

summary = []

print("=" * 80)
print("MODEL COMPARISON")
print("=" * 80)

for model_name in MODELS:

    print()
    print("#" * 80)
    print(model_name.upper())
    print("#" * 80)

    correct_predictions = 0
    top3_predictions = 0

    champion_ranks = []

    accuracies = []

    precisions = []

    recalls = []

    f1_scores = []

    for year in years:

        X_train, X_test, y_train, y_test, teams = split_dataset(
            df,
            year
        )

        if model_name == "logistic_regression":

            X_train, X_test = scale_features(
                X_train,
                X_test
            )

        model = get_model(model_name)

        model = train_model(
            model,
            X_train,
            y_train
        )

        accuracy, precision, recall, f1, cm, winner, results = evaluate(

            model,

            X_test,

            y_test,

            teams

        )

        actual = df[
            (df["Year"] == year) &
            (df["Winner"] == 1)
        ]["Team"].values[0]

        rank = (

            results[
                results["Team"] == actual
            ].index[0]

            + 1

        )

        if rank <= 3:
            top3_predictions += 1

        if winner == actual:

            correct_predictions += 1

        champion_ranks.append(rank)

        accuracies.append(accuracy)

        precisions.append(precision)

        recalls.append(recall)

        f1_scores.append(f1)

        print(
            f"{year} | "
            f"Predicted: {winner:<15}"
            f"Actual: {actual:<15}"
            f"Rank: {rank}"
        )

    summary.append({

        "Model": model_name,

        "Correct Champions":
            correct_predictions,

        "Top 3":
            top3_predictions,

        "Average Rank":
            round(sum(champion_ranks)/len(champion_ranks),2),

        "Average Accuracy":
            round(sum(accuracies)/len(accuracies),3),

        "Average Precision":
            round(sum(precisions)/len(precisions),3),

        "Average Recall":
            round(sum(recalls)/len(recalls),3),

        "Average F1":
            round(sum(f1_scores)/len(f1_scores),3)

    })

summary = pd.DataFrame(summary)

print()
print("=" * 80)
print("FINAL COMPARISON")
print("=" * 80)

print(summary.to_string(index=False))

print()

max_champions = summary["Correct Champions"].max()

best_models = summary[
    summary["Correct Champions"] == max_champions
]

print("=" * 80)
print("BEST MODEL ANALYSIS")
print("=" * 80)

print()
print(f"Champion Predictions : {max_champions}/{len(years)}")

if len(best_models) == 1:

    print(
        "Best Champion Prediction Model:",
        best_models.iloc[0]["Model"]
    )

else:

    print("Champion Prediction Winner(s):")

    for model in best_models["Model"]:

        print(f" - {model}")

    print()

    print("Tie detected.")

    print("Using Average Rank as tie-breaker...")

    best_models = best_models.sort_values(
        by="Average Rank"
    )

    best_model = best_models.iloc[0]

    print()

    print(
        f"Overall Best Model: {best_model['Model']}"
    )

print()

print(
    "Lowest Average Rank :",
    summary.loc[
        summary["Average Rank"].idxmin()
    ]["Model"]
)

print(
    "Highest Average Accuracy :",
    summary.loc[
        summary["Average Accuracy"].idxmax()
    ]["Model"]
)

print(
    "Highest Average F1 :",
    summary.loc[
        summary["Average F1"].idxmax()
    ]["Model"]
)

print(
    "Highest Top-3 Accuracy :",
    summary.loc[
        summary["Top 3"].idxmax()
    ]["Model"]
)