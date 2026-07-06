import joblib

def save_model(
    model,
    model_file,
    feature_names,
    scaler=None,
    scaler_file=None
):
    model_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    joblib.dump(
        {
            "model": model,
            "features": feature_names
        },
        model_file
    )

    if scaler is not None and scaler_file is not None:

        joblib.dump(
            scaler,
            scaler_file
        )

    print()
    print("=" * 50)
    print("Model Saved")
    print("=" * 50)

    print(f"Model : {model_file}")

    if scaler is not None:
        print(f"Scaler: {scaler_file}")