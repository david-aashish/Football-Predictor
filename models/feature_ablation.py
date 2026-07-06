"""
feature_ablation.py

Tests the importance of feature groups using
Leave-One-World-Cup-Out evaluation.
"""

from utils.data_loader import load_dataset
from utils.feature_ablation import run_feature_ablation
from utils.config import MODEL_NAME

print("=" * 80)
print("FEATURE ABLATION")
print("=" * 80)

df = load_dataset()

results = run_feature_ablation(
    df,
    MODEL_NAME
)

print(results.to_string(index=False))