import pandas as pd
from pathlib import Path

DATA_FILE = Path("data/processed/world_cup_dataset.csv")

def load_dataset():

    df = pd.read_csv(DATA_FILE)

    return df