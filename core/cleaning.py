"""1) Data Transforming functions."""
from typing import Optional

import pandas as pd


# 1a - Duplicate ---------------------------------------------------------------
def find_duplicates(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    return (df[df.duplicated(subset = columns, keep = "first")])


def remove_duplicates(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    return df.drop_duplicates(subset = columns)


# 1b - Null --------------------------------------------------------------------
def find_null_values(df: pd.DataFrame) -> pd.Series:
    return df.isna().sum()


def fill_null_values(df: pd.DataFrame, column, use_mean: bool, value: Optional[str]) -> pd.DataFrame:
    if use_mean:
        if pd.api.types.is_numeric_dtype(df[column]):
            fill = df[column].mean()
        else: 
            raise ValueError("Mean cannot be used for string columns")
    else:
        if value is None or value == "":
            raise ValueError("Fill value cannot be empty")
        if pd.api.types.is_numeric_dtype(df[column]):
            try:
                fill = float(value)
            except ValueError:
                raise ValueError(f"'{value}' is not a numeric value")
        else:
            fill = value
    df[column] = df[column].fillna(fill)
    return df


# 1c - New column (arithmetic) ---------------------------------------------------
def create_math_column(df: pd.DataFrame, col_a, operation: str, col_b, new_column: str) -> pd.DataFrame:
    if pd.api.types.is_numeric_dtype(df[col_a]) and pd.api.types.is_numeric_dtype(df[col_b]):
        if operation == "+":
            df[new_column] = df[col_a] + df[col_b]
            return df
        elif operation == "-":
            df[new_column] = df[col_a] - df[col_b]
            return df
        elif operation == "*":
            df[new_column] = df[col_a] * df[col_b]
            return df
        elif operation == "/":
            if (df[col_b] == 0).any():
                raise ValueError("Cannot divide by zero")
            else:
                df[new_column] = df[col_a] / df[col_b]
                return df
        else:
            raise ValueError("Unknown operator")
    else:
        raise ValueError("Operation requires numeric columns")
        


# 1d - Outlier -----------------------------------------------------------------
def replace_outliers(df: pd.DataFrame, column, lower: Optional[float], upper: Optional[float],
                     new_value: float) -> pd.DataFrame:
    if not pd.api.types.is_numeric_dtype(df[column]):
        raise ValueError("Operation requires numeric columns")
    else:
        if lower is not None:
            df.loc[df[column] < lower, column] = new_value
        if upper is not None:
            df.loc[df[column] > upper, column] = new_value
    return df
        


def drop_outliers(df: pd.DataFrame, column, lower: Optional[float], upper: Optional[float]) -> pd.DataFrame:
    if not pd.api.types.is_numeric_dtype(df[column]):
            raise ValueError("Operation requires numeric columns")
    else:
        if lower is None and upper is None:
            raise ValueError("At least one bound is required")
        if lower is not None:
            df = df[df[column] >= lower]
        if upper is not None: 
            df = df[df[column] <= upper]
        return df

        
    


# 1e - Capitalize words (without lower/upper) ---------------------------------
def capitalize_column_values(df: pd.DataFrame, column) -> pd.DataFrame:
    if not pd.api.types.is_string_dtype(df[column]):
        raise ValueError("Only string columns are supported")
    df[column] = df[column].str.title()
    return df


# 1f - Column name ---------------------------------------------------------------
def rename_column(df: pd.DataFrame, old_name, new_name: str) -> pd.DataFrame:
    df = df.rename(columns={old_name:new_name})
    return df


# 1g - Data type ---------------------------------------------------------------
def change_dtype(df: pd.DataFrame, column, new_dtype: str) -> pd.DataFrame:
    try:
        df[column] = df[column].astype(new_dtype)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"'{column}' column could not be converted to '{new_dtype}': {exc}")
    return df


# 1h - to_datetime -------------------------------------------------------------
def create_datetime_column(df: pd.DataFrame, column, new_column: str,
                           date_format: Optional[str]) -> pd.DataFrame:
    try:
        df[new_column] = pd.to_datetime(df[column], format= date_format)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"Date conversion failed: {exc}")
    return df
    


# 1i - Combine data -------------------------------------------------------------
def concat_dataframes(df: pd.DataFrame, other_df: pd.DataFrame, axis: int) -> pd.DataFrame:
    return pd.concat([df, other_df], axis=axis)


def merge_dataframes(df: pd.DataFrame, other_df: pd.DataFrame, on: list, how: str) -> pd.DataFrame:
    return df.merge(other_df, on=on, how=how)


# 1j - Replace value ----------------------------------------------------------
def replace_column_value(df: pd.DataFrame, column, old_value: str, new_value: str) -> pd.DataFrame:

    df[column] = df[column].replace(old_value,new_value)
    return df
