from PyQt6 import QtWidgets
import sys

from window import MainWindow

class Main():
    def __init__(self) -> None:
        self.app = QtWidgets.QApplication(sys.argv)
        self.app.setStyle("Fusion")
        style = open("./styles.qss").read()
        self.app.setStyleSheet(style)

    def run(self):
        self.window = MainWindow()
        self.window.show()
        self.app.exec()

if __name__ == '__main__':
    app = Main()
    app.run()