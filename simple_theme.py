"""Shared visual theme for DataLens."""

SIMPLE_STYLESHEET = """
QWidget { font-family: 'Segoe UI', 'Arial'; font-size: 13px; color: #26364b; }
QMainWindow, QDialog, QStackedWidget, QScrollArea { background-color: #f3f6fa; }
QWidget#operationViewport { background-color: #f3f6fa; }
QLabel { background: transparent; }
QLabel#brand { font-size: 28px; font-weight: 700; color: #11283e; }
QLabel#eyebrow { font-size: 11px; font-weight: 700; color: #137d82; }
QLabel#pageTitle { font-size: 23px; font-weight: 700; color: #142b43; }
QLabel#muted { color: #65758a; }
QLabel#metric { font-size: 24px; font-weight: 700; color: #142b43; }
QLabel#sectionTitle { font-size: 16px; font-weight: 700; color: #142b43; }
QLabel#status { background: #e8eff5; color: #455b70; padding: 10px; border-radius: 6px; }
QFrame#card, QFrame#operationPanel { background: #ffffff; border: 1px solid #dbe3ec; border-radius: 10px; }
QPushButton { background: #ffffff; color: #29465c; border: 1px solid #cbd8e4; border-radius: 7px; padding: 9px 15px; font-weight: 600; }
QPushButton:hover { background: #eaf4f5; border-color: #489b9c; }
QPushButton:pressed { background: #d8eeef; }
QPushButton:disabled { color: #9aa8b7; background: #edf1f5; border-color: #e0e6ed; }
QPushButton#primary { background: #127c80; color: white; border: 1px solid #127c80; }
QPushButton#primary:hover { background: #0d686c; }
QPushButton#primary:disabled { background: #dce7e8; color: #869b9e; border-color: #dce7e8; }
QPushButton#workspace { text-align: left; font-size: 14px; padding: 15px; }
QLineEdit, QPlainTextEdit, QComboBox, QSpinBox { background: white; border: 1px solid #cbd8e4; border-radius: 6px; padding: 7px 10px; selection-background-color: #d6eeed; selection-color: #173e46; }
QLineEdit:focus, QComboBox:focus, QSpinBox:focus { border: 1px solid #127c80; }
QLineEdit:disabled { background: #edf1f5; color: #8796a8; }
QComboBox QAbstractItemView { background: white; selection-background-color: #d6eeed; selection-color: #173e46; }
QListWidget, QTableView { background: white; border: 1px solid #dbe3ec; border-radius: 7px; gridline-color: #e6edf3; alternate-background-color: #f6f9fc; selection-background-color: #d8eeed; selection-color: #15434a; }
QListWidget::item { padding: 7px 10px; margin: 2px; border-radius: 5px; }
QListWidget::item:hover { background: #edf4f7; }
QListWidget::item:selected { background: #d8eeed; color: #14565a; }
QListWidget#operationMenu { border: none; background: #ffffff; }
QListWidget#operationMenu::item { padding: 11px 12px; margin: 3px 5px; }
QHeaderView::section { background: #eaf0f6; color: #43576c; padding: 9px 10px; border: none; border-right: 1px solid #dbe3ec; border-bottom: 1px solid #dbe3ec; font-weight: 600; }
QTableCornerButton::section { background: #eaf0f6; border: none; }
QGroupBox { background: white; border: 1px solid #dbe3ec; border-radius: 9px; margin-top: 16px; padding-top: 12px; font-weight: 600; }
QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; }
QCheckBox { spacing: 8px; color: #26364b; }
QCheckBox::indicator { width: 15px; height: 15px; }
QGroupBox::title { color: #26364b; }
QMessageBox { background-color: #f3f6fa; }
QScrollBar:vertical { background: #edf2f6; width: 10px; margin: 0; }
QScrollBar:horizontal { background: #edf2f6; height: 10px; margin: 0; }
QScrollBar::handle { background: #aebfce; border-radius: 4px; min-height: 24px; min-width: 24px; }
QScrollBar::add-line, QScrollBar::sub-line { width: 0; height: 0; }
QSplitter::handle { background: #dfe7ee; }
QToolBar { background: #ffffff; border: none; spacing: 5px; }
QToolButton { padding: 5px; border-radius: 4px; }
QToolButton:hover { background: #d8eeed; }
QToolTip { background: #173449; color: white; border: none; padding: 5px; }
"""


def apply_theme(app):
    """Use a consistent light palette even when Windows uses dark mode."""
    from PyQt6.QtGui import QColor, QPalette
    app.setStyle("Fusion")
    palette = QPalette()
    colors = {
        "Window": "#f3f6fa", "WindowText": "#26364b",
        "Base": "#ffffff", "AlternateBase": "#f6f9fc",
        "Text": "#26364b", "Button": "#ffffff", "ButtonText": "#29465c",
        "Highlight": "#d8eeed", "HighlightedText": "#15434a",
        "ToolTipBase": "#173449", "ToolTipText": "#ffffff",
        "PlaceholderText": "#65758a", "Light": "#ffffff",
        "Midlight": "#e6edf3", "Mid": "#aebfce", "Dark": "#65758a",
        "Shadow": "#455b70", "BrightText": "#ffffff",
        "Link": "#127c80", "LinkVisited": "#455b70",
    }
    for role, value in colors.items():
        palette.setColor(getattr(QPalette.ColorRole, role), QColor(value))
    for role in (QPalette.ColorRole.Text, QPalette.ColorRole.WindowText, QPalette.ColorRole.ButtonText):
        palette.setColor(QPalette.ColorGroup.Disabled, role, QColor("#8796a8"))
    app.setPalette(palette)
    app.setStyleSheet(SIMPLE_STYLESHEET)
