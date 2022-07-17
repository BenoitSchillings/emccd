from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *

class Mover(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

        self.setMinimumSize(1, 30)




    def paintEvent(self, e):

        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawWidget(qp)
        qp.end()

    def drawWidget(self, qp):


        font = QtGui.QFont('Serif', 7, QtGui.QFont.Light)
        qp.setFont(font)

        size = self.size()
        w = size.width()
        h = size.height()
        
        qp.setBrush(Qt.NoBrush)
        pen = QtGui.QPen()
        pen.setWidth(1)
        qp.setPen(pen)
        qp.setPen(QColor(255, 0, 0))

        for d in range(10, 100, 20):
            qp.drawEllipse(100 - d,100 -d, d*2, d*2)


 
