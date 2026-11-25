import sys
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QFileDialog, QFrame, QHBoxLayout, QLabel, QMainWindow, QMessageBox, QPushButton,
    QVBoxLayout, QWidget, QStackedWidget,
)

import core.export as export
from ui.simple_theme import apply_theme
from ui.analysis_window import AnalysisWindow
from core.data_store import FILE_FILTER, DataStore, load_dataframe
from ui.transform_window import TransformWindow
from ui.visualization_window import VisualizationWindow
from ui.widgets import FAILED, DataFrameView, call_user_function

PREVIEW_ROWS = 100


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DataLens | Data workspace")
        self.resize(1200, 760)
        self.setMinimumSize(860, 580)
        self.store = DataStore()
        self.store.changed.connect(self._refresh_preview)
        self.sections = {}

        def label(text, style):
            widget = QLabel(text)
            widget.setObjectName(style)
            return widget

        def card():
            frame = QFrame()
            frame.setObjectName("card")
            return frame

        central = QWidget()
        layout = QHBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(18)

        sidebar = card()
        sidebar.setFixedWidth(240)
        nav = QVBoxLayout(sidebar)
        nav.setContentsMargins(16, 20, 16, 16)
        nav.setSpacing(10)
        nav.addWidget(label("DataLens", "brand"))
        nav.addWidget(label("Explore with confidence", "muted"))
        nav.addSpacing(18)
        nav.addWidget(label("WORKSPACE", "eyebrow"))
        self.section_buttons = []
        for title, description, window_class in (
            ("Transformation", "Clean and reshape data", TransformWindow),
            ("Analysis", "Inspect and summarize data", AnalysisWindow),
            ("Visualization", "Explore data through charts", VisualizationWindow),
        ):
            button = QPushButton(title)
            button.setObjectName("workspace")
            button.setEnabled(False)
            button.setToolTip(description)
            button.clicked.connect(lambda _checked=False, t=title, c=window_class: self._open_section(t, c))
            self.section_buttons.append(button)
            nav.addWidget(button)
            nav.addWidget(label(description, "muted"))
            nav.addSpacing(5)
        nav.addStretch()
        nav.addWidget(label("DATA WORKSPACE", "eyebrow"))
        nav.addWidget(label("Python  /  pandas  /  seaborn", "muted"))
        layout.addWidget(sidebar)

        body = QVBoxLayout()
        body.setSpacing(14)
        heading = QHBoxLayout()
        heading.addWidget(label("Dataset overview", "pageTitle"), 1)
        load_button = QPushButton("Open dataset")
        load_button.setObjectName("primary")
        load_button.clicked.connect(self._on_load)
        self.undo_button = QPushButton("Undo")
        self.undo_button.setEnabled(False)
        self.undo_button.clicked.connect(self.store.undo)
        self.export_button = QPushButton("Export CSV")
        self.export_button.setEnabled(False)
        self.export_button.clicked.connect(self._on_export)
        for button in (self.undo_button, self.export_button, load_button):
            heading.addWidget(button)
        body.addLayout(heading)
        self.info_label = label("No dataset loaded", "muted")
        self.info_label.setTextFormat(Qt.TextFormat.PlainText)
        body.addWidget(self.info_label)

        metrics = QHBoxLayout()
        self.metrics = {}
        for title in ("ROWS", "COLUMNS", "PREVIEW ROWS"):
            frame = card()
            group = QVBoxLayout(frame)
            group.setContentsMargins(15, 12, 15, 12)
            group.addWidget(label(title, "eyebrow"))
            value = label("—", "metric")
            group.addWidget(value)
            self.metrics[title] = value
            metrics.addWidget(frame)
        body.addLayout(metrics)

        preview_box = card()
        preview_layout = QVBoxLayout(preview_box)
        preview_layout.setContentsMargins(16, 14, 16, 16)
        preview_layout.addWidget(label("Data preview", "sectionTitle"))
        self.preview_note = label(f"Showing up to {PREVIEW_ROWS} rows of the active dataset.", "muted")
        preview_layout.addWidget(self.preview_note)
        self.preview = DataFrameView()
        self.preview_stack = QStackedWidget()
        empty = QWidget()
        empty_layout = QVBoxLayout(empty)
        empty_layout.addStretch()
        empty_title = label("Start with a dataset", "pageTitle")
        empty_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(empty_title)
        hint = label("Open a CSV, Excel or JSON file to begin exploring your data.", "muted")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setWordWrap(True)
        empty_layout.addWidget(hint)
        empty_layout.addStretch()
        self.preview_stack.addWidget(empty)
        self.preview_stack.addWidget(self.preview)
        preview_layout.addWidget(self.preview_stack, 1)
        body.addWidget(preview_box, 1)
        layout.addLayout(body, 1)
        self.setCentralWidget(central)

    def _on_load(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Data File", "", FILE_FILTER)
        if not path:
            return
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            df = load_dataframe(path)
        except Exception as exc:
            QMessageBox.critical(self, "File could not be read", str(exc))
            return
        finally:
            QApplication.restoreOverrideCursor()
        self.store.load(df, path)

    def _on_export(self):
        suggested = str(Path(self.store.path).with_suffix("")) + "_processed.csv"
        path, _ = QFileDialog.getSaveFileName(self, "Export as CSV", suggested, "CSV (*.csv)")
        if not path:
            return
        selected_path = path
        if not path.lower().endswith(".csv"):
            path += ".csv"
        # Confirm if the added extension targets an existing file.
        if Path(path).exists() and path != selected_path:
            if QMessageBox.question(self, "Replace file?", f"Replace the existing file?\n{path}") != QMessageBox.StandardButton.Yes:
                return
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            export.export_csv(self.store.df, path)
        except Exception as exc:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, "Export failed", str(exc))
            return
        QApplication.restoreOverrideCursor()
        QMessageBox.information(self, "Exported", f"Data exported to:\n{path}")

    def _refresh_preview(self):
        df = self.store.df
        self.preview.set_dataframe(df, PREVIEW_ROWS)
        self.info_label.setText(Path(self.store.path).name)
        self.info_label.setToolTip(str(self.store.path))
        self.metrics["ROWS"].setText(f"{df.shape[0]:,}")
        self.metrics["COLUMNS"].setText(f"{df.shape[1]:,}")
        self.metrics["PREVIEW ROWS"].setText(f"{min(len(df), PREVIEW_ROWS):,}")
        self.preview_stack.setCurrentWidget(self.preview)
        for button in self.section_buttons:
            button.setEnabled(True)
        self.export_button.setEnabled(True)
        self.undo_button.setEnabled(self.store.can_undo)

    def _open_section(self, title, window_class):
        window = self.sections.get(title)
        if window is None:
            window = self.sections[title] = window_class(self.store, self)
        window.show()
        window.raise_()
        window.activateWindow()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_theme(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
