"""Shared interface components."""
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PyQt6.QtGui import QFontDatabase, QFont
from PyQt6.QtWidgets import (
    QAbstractItemView, QComboBox, QDialog, QFormLayout, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QMessageBox, QPlainTextEdit, QPushButton, QSplitter, QStackedWidget,
    QTableView, QVBoxLayout, QWidget, QFrame, QScrollArea, QHeaderView,
)

FAILED = object()


def call_user_function(parent, func, *args, **kwargs):
    """Calls a user function and displays an error if it fails or is not implemented."""
    try:
        return func(*args, **kwargs)
    except NotImplementedError:
        QMessageBox.information(parent, "Not implemented", f"{func.__name__}() is not implemented yet.")
    except Exception as exc:
        QMessageBox.critical(parent, "Error", f"{func.__name__}() failed:\n\n{type(exc).__name__}: {exc}")
    return FAILED


# Table ----------------------------------------------------------------------------
class DataFrameModel(QAbstractTableModel):
    def __init__(self, df: pd.DataFrame):
        super().__init__()
        self._df = df

    def rowCount(self, parent=QModelIndex()):
        return len(self._df)

    def columnCount(self, parent=QModelIndex()):
        return self._df.shape[1]

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
            return None
        value = self._df.iat[index.row(), index.column()]
        if pd.api.types.is_scalar(value) and pd.isna(value):
            return "NaN"
        return str(value)

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return str(self._df.columns[section])
        return str(self._df.index[section])


class DataFrameView(QTableView):
    MAX_COLUMN_WIDTH = 300

    def __init__(self):
        super().__init__()
        self.setAlternatingRowColors(True)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setDefaultSectionSize(32)
        self.horizontalHeader().setMinimumSectionSize(80)
        self.setShowGrid(False)
        self._model = None

    def set_dataframe(self, df, max_rows=None):
        if df is None:
            df = pd.DataFrame()
        if max_rows is not None:
            df = df.head(max_rows)
        self._model = DataFrameModel(df)
        self.setModel(self._model)
        self.resizeColumnsToContents()
        for column in range(self._model.columnCount()):
            if self.columnWidth(column) > self.MAX_COLUMN_WIDTH:
                self.setColumnWidth(column, self.MAX_COLUMN_WIDTH)


class ResultView(QWidget):
    """Displays DataFrames and Series as tables, other results as text."""

    MAX_ROWS = 1000

    def __init__(self):
        super().__init__()
        self.note = QLabel()
        self.note.setObjectName("muted")
        self.note.setText("Run an operation to view its result.")
        self.table = DataFrameView()
        self.table.verticalHeader().setVisible(True)
        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)
        self.text.setPlaceholderText("Results will appear here.")
        self.text.setFont(QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont))
        self.stack = QStackedWidget()
        self.stack.addWidget(self.table)
        self.stack.addWidget(self.text)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)

        result_title = QLabel("Results")
        result_title.setObjectName("sectionTitle")
        layout.addWidget(result_title)
        layout.addWidget(self.note)
        layout.addWidget(self.stack)

    def show_result(self, result):
        if isinstance(result, pd.Series):
            result = result.to_frame()
        if isinstance(result, pd.DataFrame):
            note = f"{len(result)} rows, {result.shape[1]} columns"
            if len(result) > self.MAX_ROWS:
                note += f" (showing first {self.MAX_ROWS} rows)"
            self.note.setText(note)
            self.table.set_dataframe(result, self.MAX_ROWS)
            self.stack.setCurrentWidget(self.table)
        else:
            self.note.setText("")
            self.text.setPlainText(str(result))
            self.stack.setCurrentWidget(self.text)


class PlotCanvas(QWidget):
    """Displays the matplotlib Figure returned by a function."""

    def __init__(self):
        super().__init__()
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(6)
        self.placeholder = QLabel("Choose a chart and select columns to visualize your data.")
        self.placeholder.setObjectName("muted")
        self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder.setWordWrap(True)
        self._layout.addWidget(self.placeholder, 1)
        self._figure = None
        self._widgets = []

    def show_figure(self, figure):
        self.placeholder.hide()
        for widget in self._widgets:
            self._layout.removeWidget(widget)
            widget.deleteLater()
        if self._figure is not None:
            plt.close(self._figure)
        self._figure = figure
        canvas = FigureCanvasQTAgg(figure)
        toolbar = NavigationToolbar2QT(canvas, self)
        self._widgets = [toolbar, canvas]
        self._layout.addWidget(toolbar)
        self._layout.addWidget(canvas)


# Column selectors ---------------------------------------------------------------------
class ColumnComboBox(QComboBox):
    """Refreshes columns when data changes. column() returns the actual column name."""

    def __init__(self, store, numeric_only=False, optional=False):
        super().__init__()
        self.store = store
        self.numeric_only = numeric_only
        self.optional = optional
        store.changed.connect(self.refresh)
        self.refresh()

    def refresh(self):
        current = self.currentData()
        self.clear()
        if self.optional:
            self.addItem("(None)", None)
        df = self.store.df
        if df is not None:
            if self.numeric_only:
                df = df.select_dtypes(include="number")
            for column in df.columns:
                self.addItem(str(column), column)
        index = self.findData(current) if current is not None else -1
        if index >= 0:
            self.setCurrentIndex(index)

    def column(self):
        return self.currentData()


class ColumnListWidget(QListWidget):
    """Multiple column selection. columns() returns selected names."""

    def __init__(self, store):
        super().__init__()
        self.store = store
        self.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.setMaximumHeight(128)
        self.setToolTip("Click individual columns to select or deselect them.")
        store.changed.connect(self.refresh)
        self.refresh()

    def refresh(self, columns=None):
        selected = set(self.columns())
        self.clear()
        if columns is None:
            columns = [] if self.store.df is None else list(self.store.df.columns)
        for column in columns:
            item = QListWidgetItem(str(column))
            item.setData(Qt.ItemDataRole.UserRole, column)
            self.addItem(item)
            item.setSelected(column in selected)

    def columns(self):
        return [item.data(Qt.ItemDataRole.UserRole) for item in self.selectedItems()]


# Section window -----------------------------------------------------------------------
class OperationPanel(QFrame):
    """Operation panel with title, description, form fields and buttons."""

    def __init__(self, title, description=""):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        self.setObjectName("operationPanel")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        layout.setContentsMargins(20, 16, 20, 16)

        title_label = QLabel(title)
        title_label.setObjectName("sectionTitle")
        layout.addWidget(title_label)

        if description:
            desc_label = QLabel(description)
            desc_label.setWordWrap(True)
            desc_label.setObjectName("muted")
            layout.addWidget(desc_label)

        self.form = QFormLayout()
        self.form.setSpacing(10)
        self.form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.buttons = QHBoxLayout()
        self.buttons.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.buttons.setSpacing(6)

        layout.addLayout(self.form)
        layout.addLayout(self.buttons)
        layout.addStretch()

    def add_row(self, label, widget):
        self.form.addRow(label, widget)

    def add_button(self, text, callback):
        button = QPushButton(text)
        button.setMinimumWidth(90)
        if not self.buttons.count():
            button.setObjectName("primary")
        button.clicked.connect(lambda _checked=False: callback())
        self.buttons.addWidget(button)
        return button


class SectionWindow(QDialog):
    """Operations on the left, selected form and results on the right."""

    def __init__(self, title, store, output, top_height=320, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"DataLens | {title}")
        self.resize(1120, 820)
        self.setMinimumSize(800, 580)
        self.store = store
        self.output = output

        sidebar = QFrame()
        sidebar.setObjectName("card")
        sidebar.setFixedWidth(220)
        self.menu = QListWidget()
        self.menu.setObjectName("operationMenu")
        self.stack = QStackedWidget()
        self.menu.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.status = QLabel("Ready. Choose an operation to begin.")
        self.status.setObjectName("status")
        self.status.setWordWrap(True)
        self.dataset_label = QLabel()
        self.dataset_label.setObjectName("muted")
        self.dataset_label.setTextFormat(Qt.TextFormat.PlainText)
        self.dataset_label.setWordWrap(True)
        def refresh_dataset_label():
            if store.df is not None:
                self.dataset_label.setText(f"Active dataset  /  {store.df.shape[0]:,} rows  /  {store.df.shape[1]:,} columns")
        store.changed.connect(refresh_dataset_label)
        refresh_dataset_label()
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setHandleWidth(8)
        splitter.addWidget(self.stack)
        splitter.addWidget(output)
        splitter.setSizes([max(top_height, 300), 430])
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)
        right = QVBoxLayout()
        right.setSpacing(10)
        heading = QLabel(title)
        heading.setObjectName("pageTitle")
        right.addWidget(heading)
        right.addWidget(self.dataset_label)
        right.addWidget(splitter, 1)
        right.addWidget(self.status)
        self.left_layout = QVBoxLayout(sidebar)
        self.left_layout.setContentsMargins(12, 18, 12, 12)
        brand = QLabel("DataLens")
        brand.setObjectName("brand")
        self.left_layout.addWidget(brand)
        label = QLabel("OPERATIONS")
        label.setObjectName("eyebrow")
        self.left_layout.addWidget(label)
        self.left_layout.addWidget(self.menu, 1)
        back = QPushButton("Back to overview")
        back.clicked.connect(self.hide)
        self.left_layout.addWidget(back)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(16)
        layout.addWidget(sidebar)
        layout.addLayout(right, 1)

    def add_panel(self, name, panel):
        self.menu.addItem(name)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.viewport().setObjectName("operationViewport")
        scroll.viewport().setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(panel)
        self.stack.addWidget(scroll)
        if self.menu.count() == 1:
            self.menu.setCurrentRow(0)

    def warn(self, message):
        QMessageBox.warning(self, "Invalid input", message)
