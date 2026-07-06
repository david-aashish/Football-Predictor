import pandas as pd
from sklearn.preprocessing import StandardScaler
from utils.config import DROP_COLUMNS

def preprocess_dataset(df):

    df = pd.get_dummies(
        df,
        columns=["Confederation"],
        dtype=int
    )
    
    df = df.drop(columns=DROP_COLUMNS)

    return df

def scale_features(X_train, X_test=None, return_scaler=False):

    scaler = StandardScaler()

    X_train = scaler.fit_transform(X_train)

    if X_test is not None:
        X_test = scaler.transform(X_test)

    if return_scaler:
        return X_train, X_test, scaler

    return X_train, X_test