import pandas as pd

def count_by_status(df: pd.DataFrame):
    return df["وضعیت نهایی"].value_counts().to_dict()