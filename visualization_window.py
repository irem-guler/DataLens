from PyQt6.QtWidgets import QCheckBox

import visualization
from widgets import (
    FAILED, ColumnComboBox, ColumnListWidget, OperationPanel, PlotCanvas, SectionWindow,
    call_user_function,
)


class VisualizationWindow(SectionWindow):
    def __init__(self, store, parent=None):
        super().__init__("Data Visualization", store, PlotCanvas(), top_height=190, parent=parent)

        self._build_scatter()
        self._build_line()
        self._build_dist()
        self._build_bar()
        self._build_heatmap()

    def _plot(self, func, *args):
        figure = call_user_function(self, func, self.store.df, *args)
        if figure is FAILED:
            return
        self.output.show_figure(figure)
        self.status.setText(f"Chart created: {func.__name__.replace('_', ' ')}.")

    def _build_scatter(self):
        panel = OperationPanel("Scatter Plot", "X and Y axes as numeric columns, optional color by category.")
        x = ColumnComboBox(self.store)
        y = ColumnComboBox(self.store)
        hue = ColumnComboBox(self.store, optional=True)
        panel.add_row("X:", x)
        panel.add_row("Y:", y)
        panel.add_row("Color group (optional):", hue)
        panel.add_button("Plot", lambda: self._plot(visualization.scatter_plot, x.column(), y.column(), hue.column()))
        self.add_panel("Scatter", panel)

    def _build_line(self):
        panel = OperationPanel("Line Plot", "Show X and Y change as line, optional color by category.")
        x = ColumnComboBox(self.store)
        y = ColumnComboBox(self.store)
        hue = ColumnComboBox(self.store, optional=True)
        panel.add_row("X:", x)
        panel.add_row("Y:", y)
        panel.add_row("Color group (optional):", hue)
        panel.add_button("Plot", lambda: self._plot(visualization.line_plot, x.column(), y.column(), hue.column()))
        self.add_panel("Line", panel)

    def _build_dist(self):
        panel = OperationPanel("Distribution", "Show distribution of numeric column.")
        column = ColumnComboBox(self.store, numeric_only=True)
        hue = ColumnComboBox(self.store, optional=True)
        kde = QCheckBox("Show density curve (KDE)")
        kde.setChecked(True)
        panel.add_row("Column:", column)
        panel.add_row("Color group (optional):", hue)
        panel.add_row("", kde)
        panel.add_button("Plot", lambda: self._plot(visualization.dist_plot, column.column(), hue.column(),
                                                    kde.isChecked()))
        self.add_panel("Distribution", panel)

    def _build_bar(self):
        panel = OperationPanel("Bar Plot", "Compare categories with values.")
        x = ColumnComboBox(self.store)
        y = ColumnComboBox(self.store)
        hue = ColumnComboBox(self.store, optional=True)
        panel.add_row("X:", x)
        panel.add_row("Y:", y)
        panel.add_row("Color group (optional):", hue)
        panel.add_button("Plot", lambda: self._plot(visualization.bar_plot, x.column(), y.column(), hue.column()))
        self.add_panel("Bar", panel)

    def _build_heatmap(self):
        panel = OperationPanel("Heatmap", "Show correlation between numeric columns.")
        self.heatmap_columns = ColumnListWidget(self.store)
        panel.add_row("Columns:", self.heatmap_columns)
        panel.add_button("Plot", self._on_heatmap)
        self.add_panel("Heatmap", panel)

    def _on_heatmap(self):
        columns = self.heatmap_columns.columns()
        if len(columns) < 2:
            self.warn("Select at least 2 columns for heatmap.")
            return
        self._plot(visualization.heatmap_plot, columns)
