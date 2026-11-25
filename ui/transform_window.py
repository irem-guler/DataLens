import pandas as pd
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QCheckBox, QComboBox, QFileDialog, QLabel, QLineEdit, QMessageBox, QPushButton

import core.cleaning as cleaning
from core.data_store import FILE_FILTER, load_dataframe
from ui.widgets import (
    FAILED, ColumnComboBox, ColumnListWidget, OperationPanel, ResultView, SectionWindow,
    call_user_function,
)

DTYPES = ["int64", "float64", "str", "bool", "category", "datetime64[ns]"]
MATH_OPERATIONS = ["+", "-", "*", "/"]
MERGE_HOW = ["inner", "left", "right", "outer"]


class TransformWindow(SectionWindow):
    def __init__(self, store, parent=None):
        super().__init__("Data Transformation", store, ResultView(), parent=parent)
        self.other_df = None

        undo_button = QPushButton("Undo")
        undo_button.clicked.connect(self._on_undo)
        self.store.changed.connect(lambda: undo_button.setEnabled(self.store.can_undo))
        undo_button.setEnabled(self.store.can_undo)
        self.left_layout.addWidget(undo_button)

        self._build_duplicates()
        self._build_nulls()
        self._build_math_column()
        self._build_outliers()
        self._build_capitalize()
        self._build_rename()
        self._build_dtype()
        self._build_datetime()
        self._build_combine()
        self._build_replace_value()

    def _apply(self, func, *args):
        result = call_user_function(self, func, self.store.df.copy(deep=False), *args)
        if result is FAILED:
            return
        if not isinstance(result, pd.DataFrame):
            QMessageBox.warning(self, "Error", f"{func.__name__}() must return a DataFrame.")
            return
        self.store.apply(result)
        self.output.show_result(result)
        self.status.setText(f"Changes applied: {func.__name__.replace('_', ' ')}. You can undo this operation.")

    def _on_undo(self):
        self.store.undo()
        self.status.setText(f"Undo completed. Shape: {self.store.df.shape}")

    def _show(self, func, *args):
        result = call_user_function(self, func, self.store.df, *args)
        if result is FAILED:
            return
        self.output.show_result(result)
        self.status.setText(f"Completed: {func.__name__.replace('_', ' ').capitalize()}.")

    def _text(self, line_edit, label):
        text = line_edit.text().strip()
        if not text:
            self.warn(f"'{label}' cannot be empty.")
            return None
        return text

    def _bound(self, line_edit, label):
        text = line_edit.text().strip()
        if not text:
            return None
        try:
            return float(text.replace(",", "."))
        except ValueError:
            raise ValueError(f"'{label}' must be a number.")

    def _build_duplicates(self):
        panel = OperationPanel("Handle Duplicates", "Find or delete duplicate rows.")
        self.dup_columns = ColumnListWidget(self.store)
        panel.add_row("Columns:", self.dup_columns)
        panel.add_button("Show Duplicates", self._on_find_duplicates)
        panel.add_button("Remove Duplicates", self._on_remove_duplicates)
        self.add_panel("Duplicates", panel)

    def _selected_duplicate_columns(self):
        columns = self.dup_columns.columns()
        if not columns:
            self.warn("Select at least one column.")
        return columns

    def _on_find_duplicates(self):
        if columns := self._selected_duplicate_columns():
            self._show(cleaning.find_duplicates, columns)

    def _on_remove_duplicates(self):
        if columns := self._selected_duplicate_columns():
            self._apply(cleaning.remove_duplicates, columns)

    def _build_nulls(self):
        panel = OperationPanel("Handle Null Values", "Find and fill missing values.")
        panel.add_button("Show Null Values", lambda: self._show(cleaning.find_null_values))
        self.null_column = ColumnComboBox(self.store)
        self.null_use_mean = QCheckBox("Numeric column: use mean")
        self.null_value = QLineEdit()
        self.null_use_mean.toggled.connect(lambda checked: self.null_value.setDisabled(checked))
        panel.add_row("Column:", self.null_column)
        panel.add_row("", self.null_use_mean)
        panel.add_row("Fill value:", self.null_value)
        panel.add_button("Fill Null Values", self._on_fill_nulls)
        self.add_panel("Missing values", panel)

    def _on_fill_nulls(self):
        use_mean = self.null_use_mean.isChecked()
        value = None
        if not use_mean:
            value = self._text(self.null_value, "Fill value")
            if value is None:
                return
        self._apply(cleaning.fill_null_values, self.null_column.column(), use_mean, value)

    def _build_math_column(self):
        panel = OperationPanel("Create Math Column", "Create new column from operation on two columns.")
        self.math_a = ColumnComboBox(self.store, numeric_only=True)
        self.math_op = QComboBox()
        self.math_op.addItems(MATH_OPERATIONS)
        self.math_b = ColumnComboBox(self.store, numeric_only=True)
        self.math_new = QLineEdit()
        panel.add_row("Column A:", self.math_a)
        panel.add_row("Operation:", self.math_op)
        panel.add_row("Column B:", self.math_b)
        panel.add_row("New column name:", self.math_new)
        panel.add_button("Create", self._on_math_column)
        self.add_panel("Calculated column", panel)

    def _on_math_column(self):
        new_column = self._text(self.math_new, "New column name")
        if new_column is None:
            return
        self._apply(cleaning.create_math_column, self.math_a.column(), self.math_op.currentText(),
                    self.math_b.column(), new_column)

    def _build_outliers(self):
        panel = OperationPanel("Handle Outliers", "Change or remove values outside bounds.")
        self.outlier_column = ColumnComboBox(self.store, numeric_only=True)
        self.outlier_lower = QLineEdit()
        self.outlier_upper = QLineEdit()
        self.outlier_new = QLineEdit()
        panel.add_row("Column:", self.outlier_column)
        panel.add_row("Lower bound:", self.outlier_lower)
        panel.add_row("Upper bound:", self.outlier_upper)
        panel.add_row("New value:", self.outlier_new)
        panel.add_button("Replace Outliers", self._on_replace_outliers)
        panel.add_button("Remove Outliers", self._on_drop_outliers)
        self.add_panel("Outliers", panel)

    def _read_outlier_bounds(self):
        try:
            lower = self._bound(self.outlier_lower, "Lower bound")
            upper = self._bound(self.outlier_upper, "Upper bound")
        except ValueError as exc:
            self.warn(str(exc))
            return None
        if lower is None and upper is None:
            self.warn("Enter at least one bound.")
            return None
        return lower, upper

    def _on_replace_outliers(self):
        if (bounds := self._read_outlier_bounds()) is None:
            return
        try:
            new_value = self._bound(self.outlier_new, "New value")
        except ValueError as exc:
            self.warn(str(exc))
            return
        if new_value is None:
            self.warn("'New value' cannot be empty.")
            return
        self._apply(cleaning.replace_outliers, self.outlier_column.column(), *bounds, new_value)

    def _on_drop_outliers(self):
        if (bounds := self._read_outlier_bounds()) is not None:
            self._apply(cleaning.drop_outliers, self.outlier_column.column(), *bounds)

    def _build_capitalize(self):
        panel = OperationPanel("Capitalize Text", "Capitalize first letter of each word.")
        self.cap_column = ColumnComboBox(self.store)
        panel.add_row("Column:", self.cap_column)
        panel.add_button("Apply", self._on_capitalize)
        self.add_panel("Capitalize", panel)

    def _on_capitalize(self):
        self._apply(cleaning.capitalize_column_values, self.cap_column.column())

    def _build_rename(self):
        panel = OperationPanel("Rename Column", "Change column name.")
        self.rename_old = ColumnComboBox(self.store)
        self.rename_new = QLineEdit()
        panel.add_row("Old name:", self.rename_old)
        panel.add_row("New name:", self.rename_new)
        panel.add_button("Rename", self._on_rename)
        self.add_panel("Rename", panel)

    def _on_rename(self):
        new_name = self._text(self.rename_new, "New name")
        if new_name is None:
            return
        self._apply(cleaning.rename_column, self.rename_old.column(), new_name)

    def _build_dtype(self):
        panel = OperationPanel("Change Data Type", "Convert column to different data type.")
        self.dtype_column = ColumnComboBox(self.store)
        self.dtype_new = QComboBox()
        self.dtype_new.addItems(DTYPES)
        panel.add_row("Column:", self.dtype_column)
        panel.add_row("New type:", self.dtype_new)
        panel.add_button("Convert", self._on_dtype)
        self.add_panel("Data type", panel)

    def _on_dtype(self):
        self._apply(cleaning.change_dtype, self.dtype_column.column(), self.dtype_new.currentText())

    def _build_datetime(self):
        panel = OperationPanel("Create Date Column", "Convert string to datetime.")
        self.datetime_column = ColumnComboBox(self.store)
        self.datetime_new = QLineEdit()
        self.datetime_format = QLineEdit()
        self.datetime_format.setPlaceholderText("Ex: %Y-%m-%d")
        panel.add_row("Source column:", self.datetime_column)
        panel.add_row("New column name:", self.datetime_new)
        panel.add_row("Date format:", self.datetime_format)
        panel.add_button("Create", self._on_datetime)
        self.add_panel("DateTime", panel)

    def _on_datetime(self):
        new_col = self._text(self.datetime_new, "New column name")
        if new_col is None:
            return
        fmt = self.datetime_format.text().strip() or None
        self._apply(cleaning.create_datetime_column, self.datetime_column.column(), new_col, fmt)

    def _build_combine(self):
        panel = OperationPanel("Merge Data", "Combine with another file.")
        self.load_other = QPushButton("Load File")
        self.load_other.clicked.connect(self._on_load_other)
        self.other_label = QLabel("(Not loaded)")
        panel.buttons.addWidget(self.load_other)
        panel.form.addRow(self.other_label)

        self.combine_axis = QComboBox()
        self.combine_axis.addItems(["Stack (Axis 0)", "Side by side (Axis 1)"])
        self.merge_on = QLineEdit()
        self.merge_on.setPlaceholderText("Leave empty for concat")
        self.merge_how = QComboBox()
        self.merge_how.addItems(MERGE_HOW)
        panel.add_row("Type:", self.combine_axis)
        panel.add_row("Common column:", self.merge_on)
        panel.add_row("Method:", self.merge_how)
        panel.add_button("Merge", self._on_combine)
        self.add_panel("Combine datasets", panel)

    def _on_load_other(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "CSV, Excel (*.csv *.xlsx *.xls)")
        if path:
            try:
                self.other_df = load_dataframe(path)
                self.other_label.setText(f"File loaded")
            except Exception as exc:
                self.warn(str(exc))

    def _on_combine(self):
        if self.other_df is None:
            self.warn("Load file first.")
            return
        axis = 0 if self.combine_axis.currentIndex() == 0 else 1
        merge_on = self.merge_on.text().strip() or None
        if merge_on:
            self._apply(cleaning.merge_dataframes, self.other_df, [merge_on], self.merge_how.currentText())
        else:
            self._apply(cleaning.concat_dataframes, self.other_df, axis)

    def _build_replace_value(self):
        panel = OperationPanel("Replace Value", "Replace old value with new one.")
        self.replace_column = ColumnComboBox(self.store)
        self.replace_old = QLineEdit()
        self.replace_new = QLineEdit()
        panel.add_row("Column:", self.replace_column)
        panel.add_row("Old value:", self.replace_old)
        panel.add_row("New value:", self.replace_new)
        panel.add_button("Replace", self._on_replace)
        self.add_panel("Replace", panel)

    def _on_replace(self):
        old = self._text(self.replace_old, "Old value")
        new = self._text(self.replace_new, "New value")
        if old and new:
            self._apply(cleaning.replace_column_value, self.replace_column.column(), old, new)
