from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from utils.config import (
    RANDOM_STATE,
    N_JOBS,
    CLASS_WEIGHT,
    MAX_ITER,
    RF_MAX_DEPTH,
    RF_N_ESTIMATORS,
    RF_MIN_SAMPLES_SPLIT,
    RF_MIN_SAMPLES_LEAF,
    XGB_MAX_DEPTH,
    XGB_N_ESTIMATORS,
    XGB_LEARNING_RATE,
    XGB_SUBSAMPLE,
    XGB_COLSAMPLE_BYTREE,
    OBJECTIVE,
    EVAL_METRIC
)

def get_logistic_regression():

    return LogisticRegression(
        max_iter=MAX_ITER,
        random_state=RANDOM_STATE,
        class_weight=CLASS_WEIGHT,
    )


def get_random_forest():

    return RandomForestClassifier(
        n_estimators=RF_N_ESTIMATORS,
        max_depth=RF_MAX_DEPTH,
        min_samples_split=RF_MIN_SAMPLES_SPLIT,
        min_samples_leaf=RF_MIN_SAMPLES_LEAF,
        random_state=RANDOM_STATE,
        class_weight=CLASS_WEIGHT,
        n_jobs=N_JOBS
    )


def get_xgboost():

    return XGBClassifier(
        n_estimators=XGB_N_ESTIMATORS,
        learning_rate=XGB_LEARNING_RATE,
        max_depth=XGB_MAX_DEPTH,
        subsample=XGB_SUBSAMPLE,
        colsample_bytree=XGB_COLSAMPLE_BYTREE,
        objective=OBJECTIVE,
        random_state=RANDOM_STATE,
        eval_metric=EVAL_METRIC
    )

MODELS = {
    "logistic_regression": get_logistic_regression,
    "random_forest": get_random_forest,
    "xgboost": get_xgboost
}

def get_model(model_name):

    return MODELS[model_name]()