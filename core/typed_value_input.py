from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSpinBox,
    QDoubleSpinBox,
    QCheckBox,
    QDateTimeEdit,
)

from PySide6.QtCore import QDateTime
import pandas as pd


class TypedValueInput(QWidget):

    def __init__(self, dtype, parent=None):
        super().__init__(parent)

        self.dtype = dtype

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.widget = self.create_widget(dtype)

        layout.addWidget(self.widget)

    def create_widget(self, dtype):

        if dtype in ("boolean", "bool") or pd.api.types.is_bool_dtype(dtype):
            return QCheckBox()

        if dtype in ("integer", "int") or pd.api.types.is_integer_dtype(dtype):
            widget = QSpinBox()
            widget.setRange(
                -2147483648,
                2147483647
            )
            return widget

        if dtype in ("float", "double") or pd.api.types.is_float_dtype(dtype):
            widget = QDoubleSpinBox()
            widget.setRange(
                -1e15,
                1e15
            )
            widget.setDecimals(6)
            return widget

        if dtype in ("datetime", "datetime64") or pd.api.types.is_datetime64_any_dtype(dtype):
            widget = QDateTimeEdit()
            widget.setCalendarPopup(True)
            widget.setDateTime(
                QDateTime.currentDateTime()
            )
            return widget

        return QLineEdit()

    def get_value(self):

        if isinstance(self.widget, QCheckBox):
            return self.widget.isChecked()

        if isinstance(self.widget, QSpinBox):
            return self.widget.value()

        if isinstance(self.widget, QDoubleSpinBox):
            return self.widget.value()

        if isinstance(self.widget, QDateTimeEdit):
            return self.widget.dateTime().toPython()

        return self.widget.text()