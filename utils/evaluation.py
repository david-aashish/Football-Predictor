import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
from sklearn.metrics import confusion_matrix


def evaluate(model, X_test, y_test, teams):

    predictions = model.predict(X_test)

    probabilities = model.predict_proba(X_test)[:, 1]
    probabilities = probabilities / probabilities.sum()

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    precision = precision_score(
        y_test,
        predictions,
        zero_division=0
    )

    recall = recall_score(
        y_test,
        predictions,
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        predictions,
        zero_division=0
    )

    cm = confusion_matrix(
        y_test,
        predictions
    )

    results = pd.DataFrame({

        "Team": teams.values,
        "Champion_Probability": probabilities

    })

    results = results.sort_values(
        "Champion_Probability",
        ascending=False
    ).reset_index(drop=True)

    winner = results.iloc[0]["Team"]

    return (

        accuracy,
        precision,
        recall,
        f1,
        cm,
        winner,
        results

    )

def get_feature_importance(model, feature_names):

    if not hasattr(model, "feature_importances_"):
        return None

    importance = pd.DataFrame({

        "Feature": feature_names,

        "Importance": model.feature_importances_.round(4)

    })

    return importance.sort_values(
        "Importance",
        ascending=False
    )