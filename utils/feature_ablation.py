"""
feature_ablation.py

Utilities for performing feature ablation experiments.
"""

from utils.config import FEATURE_SETS


def drop_features(df, features):

    df = df.copy()

    cols_to_drop = []

    for feature in features:

        if feature == "Confederation":

            cols_to_drop.extend(
                [
                    c for c in df.columns
                    if c.startswith("Confederation_")
                ]
            )

        else:

            cols_to_drop.append(feature)

    df = df.drop(
        columns=cols_to_drop,
        errors="ignore"
    )

    return df


def run_feature_ablation(df, model_name):

    from utils.preprocessing import (
        preprocess_dataset,
        scale_features
    )

    from utils.splitting import split_dataset

    from utils.models import get_model

    from utils.trainer import train_model

    from utils.evaluation import evaluate

    import pandas as pd

    years = sorted(df["Year"].unique())

    summary = []

    for experiment, removed_features in FEATURE_SETS.items():

        experiment_df = preprocess_dataset(df)

        experiment_df = drop_features(
            experiment_df,
            removed_features
        )

        correct = 0

        top3 = 0

        ranks = []

        accuracies = []

        precisions = []

        recalls = []

        f1_scores = []

        for year in years:

            X_train, X_test, y_train, y_test, teams = split_dataset(
                experiment_df,
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

            accuracy, precision, recall, f1, _, winner, results = evaluate(
                model,
                X_test,
                y_test,
                teams
            )

            actual = experiment_df[
                (experiment_df["Year"] == year) &
                (experiment_df["Winner"] == 1)
            ]["Team"].values[0]

            rank = (
                results[
                    results["Team"] == actual
                ].index[0]
                + 1
            )

            if winner == actual:
                correct += 1

            if rank <= 3:
                top3 += 1

            ranks.append(rank)

            accuracies.append(accuracy)

            precisions.append(precision)

            recalls.append(recall)

            f1_scores.append(f1)

        summary.append({

            "Experiment": experiment,

            "Removed Features":
                ", ".join(removed_features)
                if removed_features
                else "None",

            "Correct":
                correct,

            "Top3":
                top3,

            "Average Rank":
                round(sum(ranks)/len(ranks), 2),

            "Accuracy":
                round(sum(accuracies)/len(accuracies), 3),

            "Precision":
                round(sum(precisions)/len(precisions), 3),

            "Recall":
                round(sum(recalls)/len(recalls), 3),

            "F1":
                round(sum(f1_scores)/len(f1_scores), 3)

        })

    return pd.DataFrame(summary)