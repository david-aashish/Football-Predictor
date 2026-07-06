import pandas as pd

results = pd.read_csv("data/raw/results.csv")

qualification = results[
    results["tournament"] == "FIFA World Cup qualification"
]

qualification = qualification[
    (qualification["date"] >= "2003-09-06") &
    (qualification["date"] <= "2005-11-16")
]

print(
    qualification[
        (qualification["home_team"].str.contains("Serbia", case=False, na=False)) |
        (qualification["away_team"].str.contains("Serbia", case=False, na=False))
    ][["date","home_team","away_team"]]
)