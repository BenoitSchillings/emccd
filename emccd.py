import zmq
import numpy as np
import time
import cv2
import astropy
from astropy.io import fits
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore, QT_LIB
from PyQt5 import QtWidgets
from PyQt5.QtGui  import *
import os
import skyx
import datetime
from coo import *
import random


#--------------------------------------------------------
app = QtWidgets.QApplication([])

#--------------------------------------------------------
import argparse
#--------------------------------------------------------

def bin(a):
    return(a[0:None:2, 0:None:2] + a[1:None:2, 0:None:2] + a[0:None:2, 1:None:2] + a[1:None:2, 1:None:2])

#--------------------------------------------------------

def crop_center(img,crop):
    y,x = img.shape
    startx = x//2 - crop//2
    starty = y//2 - crop//2    
    return img[starty:starty+crop, startx:startx+crop]

#--------------------------------------------------------





  



class UI:
    def click(self, event):
        event.accept()  
        self.pos = event.pos()
        print (int(self.pos.x()),int(self.pos.y()))


    def __init__(self):
        self.capture_state = 0

        self.array = np.random.randint(0,32768, (128,128), dtype=np.uint16)

        self.win = QtWidgets.QMainWindow()
        self.win.resize(800,800)
        
        self.imv = pg.ImageView()
        self.imv.setImage(self.array)
        
      
        self.win.setCentralWidget(self.imv)

        self.statusBar = QtWidgets.QStatusBar()

        self.filename = QtWidgets.QLineEdit("capture.ser")
        self.statusBar.addPermanentWidget(self.filename)

        self.capture_button =  QtWidgets.QPushButton("Start Capture")
        self.statusBar.addPermanentWidget(self.capture_button)

        self.button2 =  QtWidgets.QPushButton("update")
        self.statusBar.addPermanentWidget(self.button2)

        self.win.setStatusBar(self.statusBar)
        
      
        self. win.setWindowTitle('emccd')
        self.imv.getImageItem().mouseClickEvent = self.click
        self.cnt = 0

        self.capture_button.clicked.connect(self.Capture_buttonClick)


        self.win.show()




    def Capture_buttonClick(self):
        print("button")

        if (self.capture_state == 0):
            self.capture_state = 1
            self.capture_button.setText("Stop Capture")
        else:
            self.capture_state = 0
            self.capture_button.setText("Start Capture")



    def mainloop(self, args):

 
        while(1):
            time.sleep(0.03)
            
            self.statusBar.showMessage(str(self.cnt), 2000)
            app.processEvents()
            self.array = np.random.randint(0,1, (128,128), dtype=np.uint16)
            self.imv.setImage(self.array, autoRange=False, autoLevels=False, autoHistogramRange=False)
            #if (cnt % 10 == 0):
            #    imv.ui.histogram.setImageItem(pg.ImageItem(array))
            self.cnt = self.cnt + 1




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", type=str, default = '', help="generic file name")
    parser.add_argument("-exp", type=float, default = 1.0, help="exposure in seconds (default 1.0)")
    parser.add_argument("-gain", "--gain", type=int, default = 101, help="camera gain (default 200)")
    parser.add_argument("-bin", "--bin", type=int, default = 1, help="camera binning (default 1-6)")
    parser.add_argument("-guide", "--guide", type=int, default = 0, help="frame per guide cycle (0 to disable)")
    parser.add_argument("-count", "--count", type=int, default = 100, help="number of frames to capture")
    args = parser.parse_args()

    ui = UI()
    ui.mainloop(args)


