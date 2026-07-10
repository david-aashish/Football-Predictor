"""
predictor.py

Reusable prediction pipeline.

No printing.
No saving.
Only returns prediction DataFrames.
"""

import pandas as pd

from utils.preprocessing import scale_features
from utils.models import get_model
from utils.data import prepare_prediction_data

def predict_dataset(dataset_path, model_name):
    X_train, y_train, X_predict, teams = prepare_prediction_data(dataset_path)

    model = get_model(model_name)

    if model_name == "logistic_regression":
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

    predictions.insert(0, "Rank", predictions.index + 1)

    return predictions