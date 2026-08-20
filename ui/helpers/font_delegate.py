from PySide6.QtWidgets import QStyledItemDelegate
from PySide6.QtGui import QFont


class FontDelegate(QStyledItemDelegate):

    def paint(self, painter, option, index):

        font_name = index.data()

        if font_name:
            option.font = QFont(
                font_name,
                option.font.pointSize()
            )

        super().paint(
            painter,
            option,
            index
        )