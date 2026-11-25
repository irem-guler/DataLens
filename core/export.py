"""Export the active dataset without modifying it."""
import pandas as pd


def export_csv(df: pd.DataFrame, path: str) -> None:
    """Save every row and column as UTF-8 CSV, without the pandas index."""
    df.to_csv(path, index=False, encoding="utf-8-sig")
