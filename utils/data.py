from pathlib import Path

import pandas as pd

from utils.preprocessing import preprocess_dataset

TRAIN_FILE = Path("data/processed/world_cup_dataset.csv")


def prepare_prediction_data(dataset_path):
    train_df = pd.read_csv(TRAIN_FILE)
    predict_df = pd.read_csv(dataset_path)

    teams = predict_df["Team"].copy()

    train_df = preprocess_dataset(train_df)
    predict_df = preprocess_dataset(predict_df)

    X_train = train_df.drop(columns=["Winner", "Year", "Team"])
    y_train = train_df["Winner"]

    X_predict = predict_df.drop(columns=["Year", "Team"])
    X_predict = X_predict.reindex(columns=X_train.columns, fill_value=0)

    return X_train, y_train, X_predict, teams