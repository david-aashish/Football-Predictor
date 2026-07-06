"""
feature_analysis.py

Analyzes the features in the FIFA World Cup dataset.

Outputs:
    - Feature statistics
    - Correlation with Winner
    - Feature correlation matrix
    - Highly correlated feature pairs
"""

from utils.data_loader import load_dataset
from utils.preprocessing import preprocess_dataset

# ==========================================================
# Load Dataset
# ==========================================================

df = load_dataset()

df = preprocess_dataset(df)

print("=" * 80)
print("FEATURE ANALYSIS")
print("=" * 80)

# ==========================================================
# Basic Information
# ==========================================================

print()
print("=" * 80)
print("DATASET")
print("=" * 80)

print(f"Rows    : {len(df)}")
print(f"Columns : {len(df.columns)}")

print()

print(df.dtypes)

# ==========================================================
# Missing Values
# ==========================================================

print()
print("=" * 80)
print("MISSING VALUES")
print("=" * 80)

print(df.isnull().sum())

# ==========================================================
# Feature Statistics
# ==========================================================

print()
print("=" * 80)
print("FEATURE STATISTICS")
print("=" * 80)

numeric = df.drop(
    columns=["Winner", "Year", "Team"]
)

print(numeric.describe().T)

# ==========================================================
# Correlation with Winner
# ==========================================================

print()
print("=" * 80)
print("CORRELATION WITH WINNER")
print("=" * 80)

corr = df.corr(numeric_only=True)

winner_corr = (

    corr["Winner"]

    .drop("Winner")

    .sort_values(
        ascending=False
    )

)

print(winner_corr)

# ==========================================================
# Feature Correlation Matrix
# ==========================================================

print()
print("=" * 80)
print("FEATURE CORRELATION MATRIX")
print("=" * 80)

feature_corr = numeric.corr()

print(feature_corr.round(2))

# ==========================================================
# Highly Correlated Features
# ==========================================================

print()
print("=" * 80)
print("HIGHLY CORRELATED FEATURE PAIRS (|r| >= 0.80)")
print("=" * 80)

printed = set()

for col1 in feature_corr.columns:

    for col2 in feature_corr.columns:

        if col1 == col2:

            continue

        pair = tuple(sorted((col1, col2)))

        if pair in printed:

            continue

        value = feature_corr.loc[col1, col2]

        if abs(value) >= 0.80:

            printed.add(pair)

            print(

                f"{col1:<25}"

                f"{col2:<25}"

                f"{value:.3f}"

            )

# ==========================================================
# Feature Variance
# ==========================================================

print()
print("=" * 80)
print("LOW VARIANCE FEATURES")
print("=" * 80)

variance = numeric.var().sort_values()

print(variance)

print()
print("=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)