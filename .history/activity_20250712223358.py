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
    QLinearGradient,
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
        self.GRADIENT_COLORS = [
            ("Azul", "#448388"),
            ("Verde", "#4e743b"),
            ("Amarelo", "#a59357"),
            ("Laranja", "#9a6850"),
            ("Rosa", "#a7627d"),
            ("Lilás", "#88739b"),
            ("Cinza", "#818585"),
        ]
        model = self.day_combo.model()
        item = model.item(0)
        if item:
            item.setSelectable(False)
            item.setEnabled(False)
        self.day_combo.addItems(["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"])
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
            item.setData(name, Qt.UserRole + 1)  # guarda o nome da cor
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
        name = self.color_combo.currentData(Qt.UserRole + 1)
        return {
            "day": self.day_combo.currentIndex(),
            "code": self.code.text(),
            "title": self.title.text(),
            "start": self.start_time.time(),
            "end": self.end_time.time(),
            "color": color,
            "color_name": name,
        }

    def create_widget(self, fonts, parent, height_px):
        data = self.get_data()
        time_str = (
            f"{data['start'].toString('HH:mm')} – {data['end'].toString('HH:mm')}"
        )
        base_font = QFont(fonts["Poppins-Medium.ttf"], 10)
        line_h = QFontMetrics(base_font).lineSpacing()
        rows = height_px // line_h  # usado só para cálculo de linhas de texto

        widget = AdaptiveLabel(fonts, parent=parent)
        widget.set_parts(data["code"], data["title"], time_str)

        # NÃO usa setFixedHeight — o layout controla o tamanho do widget
        # widget.setFixedHeight(height_px)  <-- REMOVIDO

        # Aplica degradê com base no nome da cor
        grad_dict = dict(self.GRADIENT_COLORS)
        grad_hex = grad_dict.get(data["color_name"], "#000000")
        widget.set_gradient_colors(data["color"].name(), grad_hex)

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
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")
        self.setAutoFillBackground(False)
        self.setContentsMargins(4, 4, 4, 4)

        self.base_color = None
        self.gradient_color = None

    def set_gradient_colors(self, base_hex, grad_hex=None):
        self.base_color = QColor(base_hex)
        self.gradient_color = (
            QColor(grad_hex) if grad_hex else QColor(base_hex).darker(130)
        )

    def set_parts(self, code, title, time):
        self.code, self.title, self.time = code, title, time
        self.update()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)
        rect = self.contentsRect().adjusted(4, 4, -4, -4)

        radius = 10
        base = self.base_color or self.palette().window().color()
        grad = self.gradient_color or base.darker(130)

        # Aplica opacidade ao gradiente
        grad_opaco = QColor(grad)
        grad_opaco.setAlpha(180)  # valor de 0 (transparente) a 255 (opaco)

        gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())  # vertical

        # Degradê começa só perto do fim
        gradient.setColorAt(0.0, base)
        gradient.setColorAt(0.6, base)
        gradient.setColorAt(1.0, grad_opaco)

        painter.setPen(Qt.NoPen)
        painter.setBrush(gradient)
        painter.drawRoundedRect(rect, radius, radius)

        # Fonte e textos
        base_font = self.font()
        line_h = QFontMetrics(base_font).lineSpacing()
        rows = rect.height() // line_h

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

        small = QFont(self.fonts["Roboto-Light.ttf"], max(6, base_font.pointSize() - 2))
        small.setBold(True)
        painter.setFont(small)
        painter.setPen(Qt.white)
        painter.drawText(
            QRect(rect.left(), rect.bottom() - line_h + 1, rect.width(), line_h),
            Qt.AlignHCenter | Qt.AlignVCenter,
            self.time,
        )
