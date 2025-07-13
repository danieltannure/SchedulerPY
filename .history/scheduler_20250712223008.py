from PyQt5.QtWidgets import (
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QDialog,
    QMessageBox,
    QGridLayout,
    QLabel,
    QScrollArea,
)
from PyQt5.QtCore import Qt
from activity import ActivityDialog


class CronogramaWindow(QMainWindow):
    def __init__(self, fonts, parent=None):
        super().__init__(parent)
        self.fonts = fonts
        self.setWindowTitle("Cronograma com Grid")
        self.resize(1000, 950)

        self.rows = 14  # 7h às 21h
        self.cols = 6  # dias da semana: seg a sáb
        self.cell_height = 60
        self.activities = {}  # (row, col): widget

        self.grid = QGridLayout()
        self.grid.setSpacing(6)
        self.grid.setContentsMargins(20, 20, 20, 20)

        grid_container = QWidget()
        grid_container.setLayout(self.grid)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(grid_container)

        # Preencher grade com horários e dias
        for row in range(self.rows):
            label = QLabel(f"{7 + row}:00 - {8 + row}:00")
            label.setFixedHeight(self.cell_height)
            label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.grid.addWidget(label, row + 1, 0)  # coluna 0: horários

        days = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]
        for col, day in enumerate(days):
            label = QLabel(day)
            label.setAlignment(Qt.AlignCenter)
            self.grid.addWidget(label, 0, col + 1)  # linha 0: cabeçalho

        # Botões
        self.add_button = QPushButton("Adicionar")
        self.add_button.clicked.connect(self.add_activity)

        self.delete_button = QPushButton("Apagar")
        self.delete_button.setCheckable(True)
        self.delete_mode = False
        self.delete_button.toggled.connect(
            lambda chk: setattr(self, "delete_mode", chk)
        )

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.add_button)
        btn_layout.addWidget(self.delete_button)
        btn_layout.addStretch()

        main_layout = QVBoxLayout()
        main_layout.addLayout(btn_layout)
        main_layout.addWidget(self.scroll)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def add_activity(self):
        dlg = ActivityDialog(self)
        if dlg.exec() != QDialog.Accepted:
            return

        data = dlg.get_data()
        if not data["code"].strip() or not data["title"].strip() or data["day"] == 0:
            QMessageBox.warning(self, "Erro", "Preencha todos os campos obrigatórios.")
            return

        start = data["start"].hour()
        end = data["end"].hour()
        row = start - 7
        span = end - start
        col = data["day"] - 1

        if span <= 0:
            QMessageBox.warning(self, "Erro", "Horário final deve ser após o início.")
            return

        # Verificar sobreposição
        for r in range(row, row + span):
            if (r, col) in self.activities:
                QMessageBox.warning(
                    self, "Conflito", "Já existe atividade nesse horário."
                )
                return

        # Passa height_px apenas para cálculos internos de texto, mas NÃO fixa altura
        height_px = self.cell_height * span
        widget = dlg.create_widget(self.fonts, parent=self, height_px=height_px)

        # REMOVIDO: widget.setFixedHeight(height_px)

        widget.mousePressEvent = lambda e, r=row, c=col: (
            self.delete_activity(r, c) if self.delete_mode else None
        )

        self.grid.addWidget(widget, row + 1, col + 1, span, 1)
        for r in range(row, row + span):
            self.activities[(r, col)] = widget

    def delete_activity(self, row, col):
        widget = self.activities.get((row, col))
        if not widget:
            return
        self.grid.removeWidget(widget)
        widget.setParent(None)

        # Limpar todas as referências a esse widget
        to_delete = [(r, c) for (r, c), w in self.activities.items() if w == widget]
        for key in to_delete:
            del self.activities[key]
