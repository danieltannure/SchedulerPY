# schedule.py

import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QTableWidget,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
    QAbstractScrollArea,
    QHeaderView,
    QDialog,
    QMessageBox,
)
from PyQt5.QtCore import QTimer
from activity import AdaptiveLabel

# Importa o diálogo do outro arquivo
from activity import ActivityDialog


class CronogramaWindow(QMainWindow):
    def __init__(self, fonts, parent=None):
        super().__init__(parent)
        self.fonts = fonts
        self.setWindowTitle("Cronograma")
        self.resize(900, 950)

        # --- Tabela ---
        self.table = QTableWidget(14, 6)
        self.table.setHorizontalHeaderLabels(["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"])
        self.table.setVerticalHeaderLabels(
            [f"{7 + i}:00 - {8+i}:00" for i in range(14)]
        )
        self.table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        header = self.table.verticalHeader()
        header.setSectionResizeMode(QHeaderView.Fixed)
        header.setDefaultSectionSize(60)  # altura fixa desejada
        header.setMinimumSectionSize(60)

        self.table.resizeRowsToContents()

        # --- Botões ---
        self.add_button = QPushButton("Adicionar")
        self.add_button.setStyleSheet(
            """
            QPushButton {
                background-color: #007bff;
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover { background-color: #0056b3; }
            QPushButton:pressed { background-color: #004080; }
        """
        )
        self.add_button.clicked.connect(self.add_activity)

        self.delete_button = QPushButton("Apagar")
        self.delete_button.setCheckable(True)
        self.delete_button.setStyleSheet(
            """
            QPushButton {
                background-color: #dc3545;
                color: white;
                border-radius: 4px;
                width: 50px;
                padding: 6px 12px;
                font-weight: normal;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed, QPushButton:checked {
                background-color: #a71d2a;
                font-weight: bold;
            }
        """
        )

        # --- Estado de exclusão ---
        self.delete_mode = False
        self.delete_button.toggled.connect(
            lambda chk: setattr(self, "delete_mode", chk)
        )
        self.table.cellClicked.connect(self.on_cell_clicked)

        # --- Layout dos botões ---
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.add_button)
        btn_layout.addWidget(self.delete_button)
        btn_layout.addStretch()

        # --- Layout principal ---
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.addLayout(btn_layout)
        main_layout.addWidget(self.table)
        self.setCentralWidget(container)

        QTimer.singleShot(0, self.table.resizeRowsToContents)

    def add_activity(self):
        dlg = ActivityDialog(self)
        if dlg.exec() != QDialog.Accepted:
            return

        data = dlg.get_data()
        # validações
        if not data["code"].strip():
            QMessageBox.warning(self, "Erro", "Preencha o código da matéria.")
            return
        if not data["title"].strip():
            QMessageBox.warning(self, "Erro", "Preencha o título da matéria.")
            return
        if data["day"] == 0:
            QMessageBox.warning(self, "Erro", "Selecione um dia da semana.")
            return

        start = data["start"].hour()
        end = data["end"].hour()
        row = start - 7
        span = end - start
        col = data["day"] - 1

        if span <= 0:
            QMessageBox.warning(self, "Erro", "O horário final deve ser após o início.")
            return

        for r in range(row, row + span):
            if self.table.rowSpan(r, col) > 1 or self.table.cellWidget(r, col):
                QMessageBox.warning(
                    self,
                    "Conflito de horário",
                    "Já existe uma atividade nesse período nesse dia.",
                )
                return

        required = row + span
        if self.table.rowCount() < required:
            self.table.setRowCount(required)

        # Calcular altura total do widget baseado nas linhas
        height_px = sum(self.table.rowHeight(row + i) for i in range(span))

        # ** Use somente o widget criado pelo diálogo **
        widget = dlg.create_widget(self.fonts, parent=self, height_px=height_px)

        self.table.setSpan(row, col, span, 1)
        self.table.setCellWidget(row, col, widget)
        print(f"✅ Widget adicionado na célula ({row}, {col})")
        self.table.resizeRowsToContents()
        self.table.updateGeometries()

    def on_cell_clicked(self, row, col):
        if not getattr(self, "delete_mode", False):
            return

        # Encontra o início do bloco: o índice row0 onde o widget realmente existe
        start_row = row
        while (
            start_row > 0
            and self.table.cellWidget(start_row - 1, col) is None
            and self.table.rowSpan(start_row - 1, col) > 1
        ):
            start_row -= 1

        # A partir daí, obtenha o span total
        span = self.table.rowSpan(start_row, col)
        if span < 1:
            # Sem widget ou sem span, nada para fazer
            return

        # Remove o widget e redefine o span a 1
        self.table.removeCellWidget(start_row, col)
        self.table.setSpan(start_row, col, 1, 1)

        # Limpa quaisquer widgets remanescentes nas linhas correspondentes
        for r in range(start_row + 1, start_row + span):
            self.table.removeCellWidget(r, col)
