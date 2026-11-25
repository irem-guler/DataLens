from pathlib import Path

import pandas as pd
from PyQt6.QtCore import QObject, pyqtSignal

FILE_FILTER = "Data files (*.csv *.xlsx *.xls *.json);;All files (*)"


def load_dataframe(path: str) -> pd.DataFrame:
    suffix = Path(path).suffix.lower()
    if suffix in (".xlsx", ".xls"):
        return pd.read_excel(path)
    if suffix == ".json":
        return pd.read_json(path)
    try:
        return pd.read_csv(path)
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="latin-1")


class DataStore(QObject):
    """Shared application data. Emits `changed` when df changes."""

    changed = pyqtSignal()

    MAX_HISTORY = 20

    def __init__(self):
        super().__init__()
        self.df = None
        self.path = None
        self._history = []

    @property
    def has_data(self) -> bool:
        return self.df is not None

    @property
    def can_undo(self) -> bool:
        return bool(self._history)

    def load(self, df: pd.DataFrame, path: str):
        """Loading a new file resets history."""
        self.df = df
        self.path = path
        self._history.clear()
        self.changed.emit()

    def apply(self, df: pd.DataFrame):
        """Stores a transformation result; the previous df can be restored (reference, not a copy)."""
        self._history.append(self.df)
        del self._history[:-self.MAX_HISTORY]
        self.df = df
        self.changed.emit()

    def undo(self):
        if self._history:
            self.df = self._history.pop()
            self.changed.emit()
