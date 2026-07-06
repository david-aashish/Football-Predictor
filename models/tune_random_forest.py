"""
tune_random_forest.py
"""

from sklearn.ensemble import RandomForestClassifier

from utils.data_loader import load_dataset
from utils.preprocessing import preprocess_dataset
from utils.tuning import tune_model
from utils.config import (
    RANDOM_FOREST_PARAM_GRID,
    RANDOM_STATE,
    N_JOBS,
    CLASS_WEIGHT
)

def build_model(params):

    return RandomForestClassifier(

        random_state=RANDOM_STATE,

        class_weight=CLASS_WEIGHT,

        n_jobs=N_JOBS,

        **params

    )


df = load_dataset()

df = preprocess_dataset(df)

years = sorted(df["Year"].unique())

print("=" * 80)
print("RANDOM FOREST TUNING")
print("=" * 80)

results = tune_model(

    df,

    years,

    build_model,

    RANDOM_FOREST_PARAM_GRID

)

print(results.head(20).to_string(index=False))