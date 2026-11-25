from PyQt6.QtWidgets import QComboBox, QLineEdit, QSpinBox

import core.analysis as analysis
from ui.widgets import (
    FAILED, ColumnComboBox, ColumnListWidget, OperationPanel, ResultView, SectionWindow,
    call_user_function,
)

AGG_FUNCS = ["mean", "sum", "count", "min", "max", "median"]


class AnalysisWindow(SectionWindow):
    def __init__(self, store, parent=None):
        super().__init__("Data Analysis", store, ResultView(), parent=parent)

        self._build_correlation()
        self._build_describe_info()
        self._build_dtype()
        self._build_groupby()
        self._build_shape()
        self._build_head_tail()
        self._build_filter()
        self._build_mean_mode()

    def _show(self, func, *args):
        result = call_user_function(self, func, self.store.df, *args)
        if result is FAILED:
            return
        self.output.show_result(result)
        self.status.setText(f"Completed: {func.__name__.replace('_', ' ').capitalize()}.")

    def _build_correlation(self):
        panel = OperationPanel("Correlation", "Calculate correlation between two numeric columns.")
        self.corr_a = ColumnComboBox(self.store, numeric_only=True)
        self.corr_b = ColumnComboBox(self.store, numeric_only=True)
        panel.add_row("Column A:", self.corr_a)
        panel.add_row("Column B:", self.corr_b)
        panel.add_button("Calculate",
                         lambda: self._show(analysis.get_correlation, self.corr_a.column(), self.corr_b.column()))
        self.add_panel("Correlation", panel)

    def _build_describe_info(self):
        panel = OperationPanel("Data Summary", "Show statistical summary or detailed info.")
        panel.add_button("Describe", lambda: self._show(analysis.get_describe))
        panel.add_button("Info", lambda: self._show(analysis.get_info))
        self.add_panel("Summary", panel)

    def _build_dtype(self):
        panel = OperationPanel("Column Data Type", "Check data type of a column.")
        self.dtype_column = ColumnComboBox(self.store)
        panel.add_row("Column:", self.dtype_column)
        panel.add_button("Show Type",
                         lambda: self._show(analysis.get_column_dtype, self.dtype_column.column()))
        self.add_panel("Data type", panel)

    def _build_groupby(self):
        panel = OperationPanel("Group By", "Group by columns and apply operation on target column.")
        self.group_columns = ColumnListWidget(self.store)
        self.group_target = ColumnComboBox(self.store)
        self.group_agg = QComboBox()
        self.group_agg.addItems(AGG_FUNCS)
        panel.add_row("Group by columns:", self.group_columns)
        panel.add_row("Target column:", self.group_target)
        panel.add_row("Operation:", self.group_agg)
        panel.add_button("Group", self._on_groupby)
        self.add_panel("Group By", panel)

    def _on_groupby(self):
        columns = self.group_columns.columns()
        if not columns:
            self.warn("Select at least one column.")
            return
        self._show(analysis.group_by_data, columns, self.group_target.column(), self.group_agg.currentText())

    def _build_shape(self):
        panel = OperationPanel("Data Shape", "Show number of rows and columns.")
        panel.add_button("Show Shape", lambda: self._show(analysis.get_shape))
        self.add_panel("Shape", panel)

    def _build_head_tail(self):
        panel = OperationPanel("Head / Tail", "Show first or last N rows.")
        self.head_tail_n = QSpinBox()
        self.head_tail_n.setRange(1, 100000)
        self.head_tail_n.setValue(5)
        panel.add_row("Row count:", self.head_tail_n)
        panel.add_button("Head", lambda: self._show(analysis.get_head, self.head_tail_n.value()))
        panel.add_button("Tail", lambda: self._show(analysis.get_tail, self.head_tail_n.value()))
        self.add_panel("Head / Tail", panel)

    def _build_filter(self):
        panel = OperationPanel("Filter by Value", "Show rows where column equals specified value.")
        self.filter_column = ColumnComboBox(self.store)
        self.filter_value = QLineEdit()
        panel.add_row("Column:", self.filter_column)
        panel.add_row("Value:", self.filter_value)
        panel.add_button("Filter", self._on_filter)
        self.add_panel("Filter", panel)

    def _on_filter(self):
        value = self.filter_value.text().strip()
        if not value:
            self.warn("'Value' cannot be empty.")
            return
        self._show(analysis.filter_rows_by_value, self.filter_column.column(), value)

    def _build_mean_mode(self):
        panel = OperationPanel("Mean / Mode", "Calculate mean or find most frequent value.")
        self.stat_column = ColumnComboBox(self.store)
        panel.add_row("Column:", self.stat_column)
        panel.add_button("Mean", lambda: self._show(analysis.get_column_mean, self.stat_column.column()))
        panel.add_button("Mode", lambda: self._show(analysis.get_column_mode, self.stat_column.column()))
        self.add_panel("Statistics", panel)
