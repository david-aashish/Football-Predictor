def split_dataset(df, test_year):

    train = df[df["Year"] != test_year]

    test = df[df["Year"] == test_year]

    X_train = train.drop(
        columns=["Winner", "Year", "Team"]
    )

    y_train = train["Winner"]

    X_test = test.drop(
        columns=["Winner", "Year", "Team"]
    )

    y_test = test["Winner"]

    teams = test["Team"]

    return X_train, X_test, y_train, y_test, teams