from PySide6.QtWidgets import (
    QComboBox,
    QMenu,
    QToolButton
)

class TargetCombo:       


        def combo(self, target="main"):    
            self.target_combo = QComboBox()
            for key, label in (("main", "Main Dataset"),
                            ("result", "Result Dataset")):
                if key in self.MainWindow.target_dataframes:
                    self.target_combo.addItem(label, key)
            self.target_combo.setCurrentIndex(
                max(0, self.target_combo.findData(target))
            )
            
        