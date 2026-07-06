"""
train_random_forest.py

Trains a Random Forest model for FIFA World Cup prediction.

Input:
    data/processed/world_cup_dataset.csv

Output:
    saved_models/random_forest.pkl
"""

from utils.data_loader import load_dataset
from utils.preprocessing import preprocess_dataset
from utils.models import get_random_forest
from utils.trainer import train_model
from utils.save import save_model
from utils.config import RANDOM_FOREST_MODEL_FILE

if __name__ == "__main__":

    print("=" * 50)
    print("Loading Dataset")
    print("=" * 50)

    df = load_dataset()

    print(df.head())
    print()
    print(df.shape)

    df = preprocess_dataset(df)

    X = df.drop(
        columns=["Winner", "Year", "Team"]
    )

    feature_names = X.columns.tolist()

    y = df["Winner"]

    model = get_random_forest()

    print()
    print("=" * 50)
    print("Training Random Forest")
    print("=" * 50)

    model = train_model(
        model,
        X,
        y
    )

    save_model(
        model=model,
        model_file=RANDOM_FOREST_MODEL_FILE,
        feature_names=feature_names
    )