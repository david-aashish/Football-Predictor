"""
predict.py

Train all models on the full historical dataset
and predict champion probabilities for any input feature dataset.

Default:
    data/processed/world_cup_dataset_2026.csv

Output:
    predictions/
        logistic_regression_predictions.csv
        random_forest_predictions.csv
        xgboost_predictions.csv
"""

import argparse
from pathlib import Path

import pandas as pd

from live.prediction import apply_live_probability_rules
from models.predictor import predict_dataset

from utils.config import MODEL_NAMES

TRAIN_FILE = Path("data/processed/world_cup_dataset.csv")
DEFAULT_PREDICT_FILE = Path("data/processed/world_cup_dataset_2026.csv")
OUTPUT_DIR = Path("predictions")

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--file",
        type=str,
        default=str(DEFAULT_PREDICT_FILE),
        help="Feature CSV file to generate predictions for"
    )

    parser.add_argument(
        "--edition",
        default="wc2026",
        help="Tournament edition"
    )

    args = parser.parse_args()

    tournament_state = Path(
        f"data/live/{args.edition}/tournament_state.json"
    )

    dataset_path = Path(args.file)

    OUTPUT_DIR.mkdir(exist_ok=True)

    all_predictions = {}

    live_predictions = {}

    for model_name in MODEL_NAMES:
        all_predictions[model_name] = predict_dataset(
            dataset_path,
            model_name
        )
        live_predictions[model_name] = apply_live_probability_rules(
            all_predictions[model_name],
            tournament_state
        )

    champions = []

    print("=" * 80)
    print("FIFA WORLD CUP PREDICTIONS")
    print("=" * 80)

    for name, predictions in live_predictions.items():
        print()
        print("#" * 80)
        print(name.upper())
        print("#" * 80)

        print(predictions.head(10).to_string(index=False))

        champion = predictions.iloc[0]["Team"]
        champions.append(champion)

        print()
        print(f"Predicted Champion : {champion}")

        predictions.to_csv(
            OUTPUT_DIR / f"{name}_predictions.csv",
            index_label="Rank"
        )

    print()
    print("=" * 80)
    print("CONSENSUS PREDICTION")
    print("=" * 80)

    votes = pd.Series(champions).value_counts()

    print(votes)

    print()
    print(f"Consensus Champion : {votes.index[0]}")


if __name__ == "__main__":
    main()