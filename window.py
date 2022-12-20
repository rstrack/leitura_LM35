from threading import Thread
from PyQt6 import QtWidgets, QtCore, QtGui
import os
import serial

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._flag = False
        self.setWindowTitle('Leitura LM35')
        self.setWindowIcon(QtGui.QIcon('./icon.png'))
        self.resize(400, 400)
        self.mainframe = QtWidgets.QFrame(self)
        self.vlayout = QtWidgets.QVBoxLayout(self.mainframe)
        self.vlayout.setContentsMargins(0,50,0,50)
        self.vlayout.setSpacing(5)
        self.vlayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.botaoiniciar = QtWidgets.QPushButton('Iniciar leitura', self.mainframe)
        self.botaoiniciar.setFixedWidth(300)
        self.labeltemp = QtWidgets.QLabel('0.0 °C', self.mainframe)
        self.labeltemp.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.labeltemp.setObjectName('leitura')
        self.botaoencerrar = QtWidgets.QPushButton('Encerrar leitura', self.mainframe)
        self.botaoencerrar.setFixedWidth(300)
        self.botaoabrircsv = QtWidgets.QPushButton('Abrir arquivo CSV', self.mainframe)
        self.botaoabrircsv.setFixedWidth(300)

        self.vlayout.addWidget(self.botaoiniciar)
        self.vlayout.addWidget(self.labeltemp)
        self.vlayout.addWidget(self.botaoencerrar)
        self.vlayout.addWidget(self.botaoabrircsv)

        self.setCentralWidget(self.mainframe)

        self.botaoiniciar.clicked.connect(self.iniciar)
        self.botaoencerrar.clicked.connect(self.encerrar)
        self.botaoabrircsv.clicked.connect(lambda: os.startfile(os.path.abspath('./dados.csv')))

    
    def iniciar(self):
        if self._flag:
            msg = QtWidgets.QMessageBox()
            msg.setWindowIcon(QtGui.QIcon('./icon.png'))
            msg.setWindowTitle('Aviso')
            msg.setIcon(QtWidgets.QMessageBox.Icon.Information)
            msg.setText('Leitura já iniciada')
            msg.exec()
            return
        self._flag = True
        self._threadCSV = Thread(target=self.leitura)
        self._threadCSV.start()

    def encerrar(self):
        if not self._flag:
            msg = QtWidgets.QMessageBox()
            msg.setWindowIcon(QtGui.QIcon('./icon.png'))
            msg.setWindowTitle('Aviso')
            msg.setIcon(QtWidgets.QMessageBox.Icon.Information)
            msg.setText('Leitura não iniciada')
            msg.exec()
            return
        self._flag = False
        self._threadCSV.join()
        self.labeltemp.setText('0.0 °C')

    def closeEvent(self, event) -> None:
        if self._flag:
            self._flag = False
            self._threadCSV.join()
        event.accept()

    def leitura(self):
        with open('./dados.csv', "w") as file:
            s = serial.Serial("COM3", 1000000)
            file.write('Tempo(us);Tempo(ms);Valor\r')
            while(self._flag):
                linha = s.readline().decode().replace('\n', '')
                file.write(linha)
                try:
                    self.labeltemp.setText(f'{round(int(linha.split(";")[2])*0.322265625, 1)} °C') #constante levando em conta 1024 == 3,3V
                except Exception as e:
                    print(e)