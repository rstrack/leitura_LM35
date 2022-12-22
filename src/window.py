from threading import Thread
from PyQt6 import QtWidgets, QtCore, QtGui
import os
import serial
from datetime import datetime

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._flag = False
        self.setWindowTitle('Leitura LM35')
        self.setWindowIcon(QtGui.QIcon('./resources/icon.png'))
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
        '''Inicia a leitura de dados da porta serial.'''
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
        '''Encerra a leitura de dados da porta serial.'''
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

    def leitura(self):
        '''Leitura de dados da porta serial. Converte o sinal digital lido em temperatura em °C.'''
        with open('./dados.csv', "w") as file, serial.Serial("COM3", 115200) as s:
            file.write('Data;Tempo (us);Tempo (ms);Temperatura (°C)\r')
            while(self._flag):
                try:
                    linha = s.readline().decode().replace('\n', '').split(';')
                    temp = round(int(linha[2])*0.302734375, 1)
                    linha = f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')};{linha[0]};{linha[1]};{str(temp).replace('.', ',', 1)}\r"
                    file.write(linha)
                    # Constante de conversão leitura ADC para °C:
                    # 1024 == 3,0V -> utilizar 0.29296875
                    # 1024 == 3,1V -> utilizar 0.302734375
                    # 1024 == 3,15V -> utilizar 0.307617188
                    # 1024 == 3,2V -> utilizar 0.3125
                    # 1024 == 3,3V -> utilizar 0.322265625
                    self.labeltemp.setText(f'{temp} °C')
                except Exception as e:
                    # print(e)
                    pass

    def closeEvent(self, event) -> None:
        if self._flag:
            self._flag = False
            self._threadCSV.join()
        event.accept()