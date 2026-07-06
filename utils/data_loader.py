import pandas as pd
from utils.config import DATA_FILE

def load_dataset():

    df = pd.read_csv(DATA_FILE)

    return df