"""
tuning.py

Generic hyperparameter tuning utilities.
"""

from itertools import product
import pandas as pd

from utils.splitting import split_dataset
from utils.evaluation import evaluate


def tune_model(
    df,
    years,
    model_builder,
    param_grid,
):

    results = []

    parameter_names = list(param_grid.keys())

    parameter_values = list(param_grid.values())

    for values in product(*parameter_values):

        params = dict(zip(parameter_names, values))

        correct = 0

        top3 = 0

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

            model = model_builder(params)

            model.fit(
                X_train,
                y_train
            )

            accuracy, precision, recall, f1, cm, winner, prediction = evaluate(
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
                prediction[
                    prediction["Team"] == actual
                ].index[0]
                + 1
            )

            if winner == actual:
                correct += 1

            if rank <= 3:
                top3 += 1

            champion_ranks.append(rank)
            accuracies.append(accuracy)
            precisions.append(precision)
            recalls.append(recall)
            f1_scores.append(f1)

        row = params.copy()

        row["Correct"] = correct
        row["Top3"] = top3
        row["Average Rank"] = round(sum(champion_ranks) / len(champion_ranks), 2)
        row["Accuracy"] = round(sum(accuracies) / len(accuracies), 3)
        row["Precision"] = round(sum(precisions) / len(precisions), 3)
        row["Recall"] = round(sum(recalls) / len(recalls), 3)
        row["F1"] = round(sum(f1_scores) / len(f1_scores), 3)

        results.append(row)

    results = pd.DataFrame(results)

    results = results.sort_values(

        by=[
            "Correct",
            "Top3",
            "Average Rank"
        ],

        ascending=[
            False,
            False,
            True
        ]
    )

    return results