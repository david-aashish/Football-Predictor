from pathlib import Path

DATA_FILE = Path("data/processed/world_cup_dataset.csv")

LOGISTIC_REGRESSION_MODEL_FILE = Path("saved_models/logistic_regression.pkl")
SCALER_FILE = Path("saved_models/scaler.pkl")
RANDOM_FOREST_MODEL_FILE = Path("saved_models/random_forest.pkl")
XGBOOST_MODEL_FILE = Path("saved_models/xgboost.pkl")

RANDOM_STATE = 42
N_JOBS = -1
MAX_ITER = 5000
CLASS_WEIGHT = "balanced"
RF_MAX_DEPTH = 6
RF_N_ESTIMATORS = 300
RF_MIN_SAMPLES_SPLIT = 2
RF_MIN_SAMPLES_LEAF = 1
XGB_MAX_DEPTH = 4
XGB_N_ESTIMATORS = 500
XGB_LEARNING_RATE = 0.05
XGB_SUBSAMPLE = 0.8
XGB_COLSAMPLE_BYTREE = 0.8
OBJECTIVE = "binary:logistic"
EVAL_METRIC = "logloss"

MODEL_NAME = "xgboost"  # Options: "logistic_regression", "random_forest", "xgboost"

MODELS = [
    "logistic_regression",
    "random_forest",
    "xgboost"
]

RANDOM_FOREST_PARAM_GRID = {
    "n_estimators": [100, 300, 500],
    "max_depth": [4, 6, 8, None],
    "min_samples_split": [2, 5],
    "min_samples_leaf": [1, 2],
    "max_features": ["sqrt", None]
}

XGBOOST_PARAM_GRID = {
    "n_estimators": [200, 500],
    "learning_rate": [0.01, 0.05, 0.1],
    "max_depth": [3, 4, 5],
    "subsample": [0.8, 1.0],
    "colsample_bytree": [0.8, 1.0]
}

FEATURE_SETS = {

    "Baseline": [],

    # Ranking
    "No Elo": [
        "Elo_Rating"
    ],

    "No FIFA Rank": [
        "FIFA_Rank"
    ],

    "No Rankings": [
        "Elo_Rating",
        "FIFA_Rank"
    ],

    # Match performance
    "No Points": [
        "Points"
    ],

    "No Goal Difference": [
        "Goal_Difference"
    ],

    "No Match Statistics": [
        "Matches",
        "Wins",
        "Draws",
        "Losses",
        "Goals_For",
        "Goals_Against",
        "Goal_Difference",
        "Points"
    ],

    # Tournament context
    "No Host": [
        "Host"
    ],

    "No Confederation": [
        "Confederation"
    ],

    "No Previous WC": [
        "Previous_WC_Progress"
    ]
}

DROP_COLUMNS = [

    "FIFA_Rank",
    "Confederation_AFC",
    "Confederation_CAF",
    "Confederation_CONCACAF",
    "Confederation_CONMEBOL",
    "Confederation_OFC",
    "Confederation_UEFA",
    "Host",
    "Goal_Difference_Per_Game",
    "Draw_Rate",
    "Loss_Rate",
    "Matches"

]