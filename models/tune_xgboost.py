"""
tune_xgboost.py
"""

from xgboost import XGBClassifier

from utils.data_loader import load_dataset
from utils.preprocessing import preprocess_dataset
from utils.tuning import tune_model
from utils.config import (
    XGBOOST_PARAM_GRID,
    RANDOM_STATE,
    OBJECTIVE,
    EVAL_METRIC 
)

def build_model(params):

    return XGBClassifier(

        random_state=RANDOM_STATE,

        objective=OBJECTIVE,

        eval_metric=EVAL_METRIC,

        **params

    )


df = load_dataset()

df = preprocess_dataset(df)

years = sorted(df["Year"].unique())

print("=" * 80)
print("XGBOOST TUNING")
print("=" * 80)

results = tune_model(

    df,

    years,

    build_model,

    XGBOOST_PARAM_GRID

)

print(results.head(20).to_string(index=False))