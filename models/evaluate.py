"""
evaluate.py

Evaluates Logistic Regression using
Leave-One-World-Cup-Out Cross Validation.

Input:
    data/processed/world_cup_dataset.csv

Output:
    Prints evaluation metrics
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
from utils.config import MODEL_NAME
from utils.evaluation import (
    evaluate,
    get_feature_importance
)

# ==========================================================
# Main
# ==========================================================

if __name__ == "__main__":

    df = load_dataset()

    df = preprocess_dataset(df)

    years = sorted(df["Year"].unique())

    summary = []

    print("=" * 70)
    print("Leave-One-World-Cup-Out Evaluation")
    print("=" * 70)

    for year in years:

        X_train, X_test, y_train, y_test, teams = split_dataset(
            df,
            year
        )

        if MODEL_NAME == "logistic_regression":

            X_train, X_test = scale_features(
                X_train,
                X_test
            )
        
        model = get_model(MODEL_NAME)

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

        actual_champion = df[
            (df["Year"] == year) &
            (df["Winner"] == 1)
        ]["Team"].values[0]

        actual_rank = (
            results[
                results["Team"] == actual_champion
            ].index[0]
            + 1
        )

        actual_rank_str = f"{actual_rank}/{len(results)}"

        print()

        print("=" * 50)
        print(f" WORLD CUP {year}")
        print("=" * 50)

        print(f"Predicted Champion: {winner}")
        print(f"Actual Champion   : {actual_champion}")

        print()

        print("Champion Probabilities:")
        print('-' * 50)
        for i, row in results.head(10).iterrows():

            print(
                f"{i+1:2d}. "
                f"{row['Team']:<20}"
                f"{row['Champion_Probability']:.4f}"
            )

        print(f"Actual Champion Rank: {actual_rank_str}")

        print()

        print(f"Accuracy : {accuracy:.3f}")
        print(f"Precision: {precision:.3f}")
        print(f"Recall   : {recall:.3f}")
        print(f"F1 Score : {f1:.3f}")

        print()

        print("Confusion Matrix:")
        print(cm)

        summary.append({

            "Year": year,

            "Predicted": winner,

            "Actual": actual_champion,

            "Rank": actual_rank,

            "Accuracy": accuracy,

            "Precision": precision,

            "Recall": recall,

            "F1": f1

        })

    summary = pd.DataFrame(summary)

    print()
    print("=" * 80)
    print("Evaluation Summary")
    print("=" * 80)

    print(summary.to_string(index=False))

    print()
    print("=" * 80)
    print("Overall Performance")
    print("=" * 80)

    correct = (summary["Predicted"] == summary["Actual"]).sum()

    print("Correct Champion Predictions: ", correct, "/", len(summary))
    print(f"Average Accuracy       : {summary['Accuracy'].mean():.3f}")
    print(f"Average F1 Score       : {summary['F1'].mean():.3f}")
    print(f"Average Champion Rank  : {summary['Rank'].mean():.2f}")

    X = df.drop(columns=["Winner", "Year", "Team"])

    feature_names = X.columns.tolist()

    y = df["Winner"]

    if MODEL_NAME == "logistic_regression":
        X, _ = scale_features(X, X)

    model = get_model(MODEL_NAME)

    model = train_model(
        model,
        X,
        y
    )

    if MODEL_NAME != "logistic_regression":
        print()
        print("=" * 80)
        print("Feature Importance")
        print("=" * 80)

        print(
            get_feature_importance(
                model,
                feature_names
            ).to_string(index=False)
    )