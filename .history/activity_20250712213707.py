from PyQt5.QtWidgets import (
    QDialog,
    QFormLayout,
    QLineEdit,
    QTimeEdit,
    QPushButton,
    QColorDialog,
    QDialogButtonBox,
    QLabel,
    QComboBox,
)
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import (
    QFontMetrics,
    QPainter,
    QFont,
    QIcon,
    QPixmap,
    QColor,
    QStandardItemModel,
    QStandardItem,
)


class ActivityDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Adicionar Atividade Acadêmica")

        self.code = QLineEdit()
        self.title = QLineEdit()
        self.start_time = QTimeEdit()
        self.end_time = QTimeEdit()
        self.color_btn = QPushButton("Escolher cor")
        self.color = None
        self.color_btn.clicked.connect(self.choose_color)

        self.day_combo = QComboBox()
        self.day_combo.addItem("(Dia)")
        self.PASTEL_COLORS = [
            ("Azul", "#66c5cc"),
            ("Verde", "#87c55f"),
            ("Amarelo", "#f6cf71"),
            ("Laranja", "#f89c74"),
            ("Rosa", "#fe88b1"),
            ("Lilás", "#dcb0f2"),
            ("Cinza", "#dbdbdb"),
        ]
        model = self.day_combo.model()
        item = model.item(0)
        if item:
            item.setSelectable(False)
            item.setEnabled(False)
        self.day_combo.addItems(["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"])
        self.day_combo.setCurrentIndex(0)
        self.code.setPlaceholderText("(Código)")
        self.title.setPlaceholderText("(Título)")

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        self.color_combo = QComboBox()
        self.color_combo.setModel(QStandardItemModel(self.color_combo))
        for name, hexc in self.PASTEL_COLORS:
            pix = QPixmap(16, 16)
            pix.fill(Qt.transparent)
            p = QPainter(pix)
            p.setBrush(QColor(hexc))
            p.setPen(Qt.NoPen)
            p.drawEllipse(0, 0, 16, 16)
            p.end()
            icon = QIcon(pix)
            item = QStandardItem(icon, name)
            item.setData(QColor(hexc), Qt.UserRole)
            self.color_combo.model().appendRow(item)

        layout = QFormLayout(self)
        layout.addRow("Código da matéria:", self.code)
        layout.addRow("Título:", self.title)
        layout.addRow("Dia:", self.day_combo)
        layout.addRow("Início:", self.start_time)
        layout.addRow("Fim:", self.end_time)
        layout.addRow("Cor:", self.color_combo)
        layout.addWidget(buttons)

    def choose_color(self):
        col = QColorDialog.getColor()
        if col.isValid():
            self.color = col

    def get_data(self):
        color = self.color_combo.currentData(Qt.UserRole)
        return {
            "day": self.day_combo.currentIndex(),
            "code": self.code.text(),
            "title": self.title.text(),
            "start": self.start_time.time(),
            "end": self.end_time.time(),
            "color": color,
        }

    def create_widget(self, fonts, parent, height_px):
        data = self.get_data()
        time_str = (
            f"{data['start'].toString('HH:mm')} – {data['end'].toString('HH:mm')}"
        )
        base_font = QFont(fonts["Poppins-Medium.ttf"], 10)
        line_h = QFontMetrics(base_font).lineSpacing()
        rows = height_px // line_h

        widget = AdaptiveLabel(fonts, parent=parent)
        widget.set_parts(data["code"], data["title"], time_str)
        widget.setFixedHeight(height_px)
        if data["color"]:
            widget.setStyleSheet(f"background-color:{data['color'].name()};")
        return widget

    def adjust_label_font(self, label):
        font = label.font()
        fm = QFontMetrics(font)
        w = label.width() * 0.9
        text = label.text().replace("\n", " ")
        size = font.pointSize()
        while size > 6 and fm.width(text) > w:
            size -= 1
            font.setPointSize(size)
            fm = QFontMetrics(font)
        label.setFont(font)


class AdaptiveLabel(QLabel):
    def __init__(self, fonts, parent=None):
        super().__init__(parent)
        self.fonts = fonts
        self.code = ""
        self.title = ""
        self.time = ""
        self.setWordWrap(True)
        self.setAlignment(Qt.AlignCenter)

        # 🧼 Corrige fundo visível que impede arredondamento
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")
        self.setAutoFillBackground(False)
        self.setContentsMargins(4, 4, 4, 4)

    def set_parts(self, code, title, time):
        self.code, self.title, self.time = code, title, time
        self.update()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)

        rect = self.contentsRect().adjusted(4, 4, -4, -4)

        # Fundo arredondado
        radius = 10
        color = None
        ss = self.styleSheet()
        if "background-color" in ss:
            part = ss.split("background-color:")[-1].split(";")[0].strip()
            color = QColor(part)
        if not color:
            color = self.palette().window().color()

        painter.setPen(Qt.NoPen)
        painter.setBrush(color)
        painter.drawRoundedRect(rect, radius, radius)

        # Cálculo de linhas
        base_font = self.font()
        line_h = QFontMetrics(base_font).lineSpacing()
        rows = rect.height() // line_h

        # Código
        pop = QFont(self.fonts["Poppins-Bold.ttf"], base_font.pointSize())
        pop.setBold(True)
        painter.setFont(pop)
        painter.setPen(self.palette().text().color())
        painter.drawText(
            QRect(rect.left(), rect.top(), rect.width(), line_h),
            Qt.AlignHCenter | Qt.AlignTop,
            self.code,
        )
        if rows <= 2:
            return

        # Título
        inter = QFont(self.fonts["Poppins-Medium.ttf"], base_font.pointSize())
        painter.setFont(inter)
        painter.setPen(self.palette().text().color())
        if rows > 3:
            self.setWordWrap(True)
            middle = QRect(
                rect.left(),
                rect.top() + line_h,
                rect.width(),
                rect.height() - 2 * line_h,
            )
            painter.drawText(middle, Qt.TextWordWrap | Qt.AlignCenter, self.title)

        # Horário
        small = QFont(self.fonts["Roboto-Light.ttf"], max(6, base_font.pointSize() - 2))
        small.setBold(True)
        painter.setFont(small)
        painter.setPen(Qt.white)
        painter.drawText(
            QRect(rect.left(), rect.bottom() - line_h + 1, rect.width(), line_h),
            Qt.AlignHCenter | Qt.AlignVCenter,
            self.time,
        )
