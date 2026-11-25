"""3) Data Visualization functions.

Contract:
- Each function must draw and return matplotlib `Figure`.
  Use `fig, ax = plt.subplots()`; for figure-level functions like `sns.displot` return `g.figure`.
- If `hue` not selected, None is passed.
- Functions not yet implemented raise `NotImplementedError`; interface shows this as "not implemented yet" warning.
"""
from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure


def scatter_plot(df: pd.DataFrame, x, y, hue: Optional[str]) -> Figure:
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.scatterplot(data=df, x=x, y=y, hue=hue, ax=ax)
    ax.set_title(f"{x} vs {y}")
    plt.tight_layout()
    return fig


def line_plot(df: pd.DataFrame, x, y, hue: Optional[str]) -> Figure:
    fig, ax = plt.subplots(figsize=(8,6))
    sns.lineplot(data=df, x=x, y=y, hue=hue, ax=ax)
    ax.set_title(f"{x} vs {y}")
    plt.tight_layout()
    return fig


def dist_plot(df: pd.DataFrame, column, hue: Optional[str], kde: bool) -> Figure:
    g = sns.displot(data=df, x=column, hue=hue, kde=kde)
    g.set(title=f"{column} Distplot")
    return g.figure


def bar_plot(df: pd.DataFrame, x, y, hue: Optional[str]) -> Figure:
    fig,ax = plt.subplots(figsize=(8,6))
    sns.barplot(data=df, x=x, y=y, hue=hue, ax=ax, saturation=1)
    ax.set_title(f"{x} vs {y}")
    plt.tight_layout()
    return fig


def heatmap_plot(df: pd.DataFrame, columns: list) -> Figure:
    """Heatmap for selected numeric columns (typically a correlation matrix)."""
    try:
        fig,ax = plt.subplots(figsize=(8,6))
        corr = df[columns].corr()
        sns.heatmap(corr, ax = ax, annot=True, fmt=".2f")
        ax.set_title("Correlation Matrix")
        plt.tight_layout()
        return fig
    except (TypeError, KeyError, ValueError):
        raise ValueError("Select numeric columns only")
