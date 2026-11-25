"""2) Data Analysis functions."""
import pandas as pd
import io


# 2a - Correlation --------------------------------------------------------------
def get_correlation(df: pd.DataFrame, col_a, col_b) -> float:
    if pd.api.types.is_numeric_dtype(df[col_a]) and pd.api.types.is_numeric_dtype(df[col_b]):
        return df[col_a].corr(df[col_b])
    else:
        raise ValueError("Columns must be numeric")


# 2b - describe / info ---------------------------------------------------------
def get_describe(df: pd.DataFrame) -> pd.DataFrame:
    return df.describe()


def get_info(df: pd.DataFrame) -> str:
    buffer = io.StringIO()
    df.info(buf=buffer)
    return buffer.getvalue()


# 2c - dtype -------------------------------------------------------------------
def get_column_dtype(df: pd.DataFrame, column):
    return df[column].dtype


# 2d - groupby -----------------------------------------------------------------
def group_by_data(df: pd.DataFrame, group_columns: list, target_column, agg_func: str) -> pd.DataFrame:
    result = df.groupby(group_columns)[target_column].agg(agg_func)
    return result.to_frame()


# 2e - shape -------------------------------------------------------------------
def get_shape(df: pd.DataFrame) -> tuple:
    return df.shape


# 2f - head / tail -------------------------------------------------------------
def get_head(df: pd.DataFrame, n: int) -> pd.DataFrame:
    return df.head(n)


def get_tail(df: pd.DataFrame, n: int) -> pd.DataFrame:
    return df.tail(n)


# 2g - Rows matching a value --------------------------------------------------------
def filter_rows_by_value(df: pd.DataFrame, column, value: str) -> pd.DataFrame:
    if pd.api.types.is_string_dtype(df[column]):
        value = value.strip()
        return df[df[column].str.strip() == value]
    else:
        try:
            value = df[column].dtype.type(value)
        except (ValueError, TypeError):
            raise ValueError(f"Could not convert '{value}' to '{df[column].dtype}'")
        return df[df[column] == value]
    


# 2h - mean / mod --------------------------------------------------------------
def get_column_mean(df: pd.DataFrame, column) -> float:
    return df[column].mean()


def get_column_mode(df: pd.DataFrame, column) -> pd.Series:
    return df[column].mode()
