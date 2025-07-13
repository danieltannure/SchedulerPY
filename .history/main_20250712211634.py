# main.py
from PyQt5.QtGui import QFontDatabase
from PyQt5.QtWidgets import QApplication
import sys, os
from scheduler import CronogramaWindow  # importar a janela


def load_fonts():
    base = os.path.join(os.path.dirname(__file__), "text")
    loaded = {}
    for fname in ("Poppins-Bold.ttf", "Poppins-Medium.ttf", "Roboto-Light.ttf"):
        path = os.path.join(base, fname)
        fid = QFontDatabase.addApplicationFont(path)
        if fid < 0:
            print(f"❌ Falha ao carregar {fname}")
            continue
        loaded[fname] = QFontDatabase.applicationFontFamilies(fid)[0]
    return loaded


if __name__ == "__main__":
    app = QApplication(sys.argv)
    fonts = load_fonts()
    win = CronogramaWindow(fonts)  # passando fonts adiante
    win.show()
    sys.exit(app.exec_())
