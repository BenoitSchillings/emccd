import zmq
import numpy as np
import time
from datetime import datetime
import cv2
import astropy
from astropy.io import fits
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore, QT_LIB
from PyQt5 import QtWidgets
from PyQt5.QtGui  import *
from PyQt5.QtCore import *
import os
#import skyx
from util import *
import datetime
import random
from ser import SerWriter


from pyvcam import pvc
from pyvcam.camera import Camera
from pyvcam import constants as const


#--------------------------------------------------------
app = QtWidgets.QApplication([])

#--------------------------------------------------------
import argparse
#--------------------------------------------------------

class fake_emccd:
    def __init__(self, temp):
        
        print("init cam")
        self.frame = np.random.randint(0,4096, (512,512), dtype=np.uint16)
        self.stars_frame = self.stars(self.frame, 80, gain=2)

    def stars(self, image, number, max_counts=10000, gain=1):
        """
        Add some stars to the image.
        """
        from photutils.datasets import make_random_gaussians_table, make_gaussian_sources_image
        # Most of the code below is a direct copy/paste from
        # https://photutils.readthedocs.io/en/stable/_modules/photutils/datasets/make.html#make_100gaussians_image
        
        flux_range = [max_counts/10, max_counts]
        
        y_max, x_max = image.shape
        xmean_range = [0.1 * x_max, 0.9 * x_max]
        ymean_range = [0.1 * y_max, 0.9 * y_max]
        xstddev_range = [2, 2]
        ystddev_range = [2, 2]
        params = dict([('amplitude', flux_range),
                      ('x_mean', xmean_range),
                      ('y_mean', ymean_range),
                      ('x_stddev', xstddev_range),
                      ('y_stddev', ystddev_range),
                      ('theta', [0, 2*np.pi])])

        sources = make_random_gaussians_table(number, params,
                                              seed=12345)
        
        star_im = make_gaussian_sources_image(image.shape, sources)
        
        return star_im         

    def get_frame(self):        
        self.frame = np.random.randint(0,1024, (512,512), dtype=np.uint16)
        

        return self.frame + self.stars_frame.astype(np.uint16)
        
    def start(self, exposure):
        self.running = 1
        
    def close(self):
        self.running = 0


class emccd:
    def __init__(self, temp):
        
        print("init cam")
        pvc.init_pvcam()

        
        self.vcam = next(Camera.detect_camera())
        self.vcam.open()
        self.vcam.gain=2
        print(self.vcam.temp)
        self.vcam.temp_setpoint = temp * 100 
        print(self.vcam.temp_setpoint)
        self.vcam.clear_mode="Pre-Sequence"
        #self.vcam.clear_mode="Pre-Exposure"

        pvc.set_param(self.vcam.handle, const.PARAM_READOUT_PORT, 0)
        #v = pvc.get_param(self.vcam.handle, const.PARAM_FAN_SPEED_SETPOINT, const.ATTR_CURRENT) 
        pvc.set_param(self.vcam.handle, const.PARAM_GAIN_MULT_FACTOR, 0)
        
        #while(1):
            #print(self.vcam.temp)
        

    def get_frame(self):        
        frame = self.vcam.get_live_frame().reshape(self.vcam.sensor_size[::-1]) 
        return frame
        
    def start(self, exposure):
        self.vcam.start_live(exp_time=int(exposure*1000.0))
        
    def close(self):
        self.vcam.close()


#--------------------------------------------------------


class FrameWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self)
        self.quit = 0

    def closeEvent(self, event):
        self.quit = 1
        print("quit")
        QtWidgets.QMainWindow.closeEvent(self, event)

#--------------------------------------------------------

class UI:
    def click(self, event):
        event.accept()  
        self.pos = event.pos()
        print (int(self.pos.x()),int(self.pos.y()))

    def convert_nparray_to_QPixmap(self,img):
        w,h = img.shape

        qimg = QImage(img.data, h, w, QImage.Format_Grayscale16) 
        qpixmap = QPixmap(qimg)

        return qpixmap



    def __init__(self,  args):
        self.capture_state = 0
        self.update_state = 1
        self.pos = QPoint(256,256)
        self.array = np.random.randint(0,8192, (512,512), dtype=np.uint16)
        
        self.win = FrameWindow()
        self.EDGE = 16
        
        self.win.resize(800,800)
        
        self.imv = pg.ImageView()
        self.imv.setImage(self.array)
        
      
        self.win.setCentralWidget(self.imv)

        self.statusBar = QtWidgets.QStatusBar()


        temp_widget = QtWidgets.QWidget(self.win)
        temp_widget.setLayout(QtWidgets.QHBoxLayout())
        temp_widget.setFixedSize(768, 256)
        self.zoom_view = QtWidgets.QLabel(self.win)
        
        temp_widget.layout().addWidget(self.zoom_view)
        
        self.statusBar.addPermanentWidget(temp_widget, 1)


        rightlayout = QtWidgets.QWidget(self.win)
        rightlayout.setLayout(QtWidgets.QVBoxLayout())
        rightlayout.setFixedSize(384, 128)
        
        self.filename = QtWidgets.QLineEdit(args.filename)
        rightlayout.layout().addWidget(self.filename)

        

        self.capture_button =  QtWidgets.QPushButton("Start Capture")
        rightlayout.layout().addWidget(self.capture_button)

        self.update_button =  QtWidgets.QPushButton("slow_update")
        rightlayout.layout().addWidget(self.update_button)
        self.txt1 = QtWidgets.QLabel(self.win)
        rightlayout.layout().addWidget(self.txt1)
        self.txt1.setText("status_text 1")


        self.statusBar.addPermanentWidget(rightlayout)

        self.win.setStatusBar(self.statusBar)
        
      
        self. win.setWindowTitle('emccd')
        self.imv.getImageItem().mouseClickEvent = self.click
        self.cnt = 0

        self.capture_button.clicked.connect(self.Capture_buttonClick)
        self.update_button.clicked.connect(self.Update_buttonClick)
        
        self.win.show()



    def Update_buttonClick(self):
        print("button")

        if (self.update_state == 1):
            self.update_button.setText("fast_update")
            self.update_state = 0
          
        else:
            self.update_button.setText("slow_update")
            self.update_state = 1


    def Capture_buttonClick(self):
        print("button")

        if (self.capture_state == 0):
            
            self.capture_button.setText("Stop Capture")
            vnow = time.time_ns()
            self.capture_filename = self.filename.text() + str(vnow) + ".ser"
            self.capture_file = SerWriter(self.capture_filename)
            self.capture_file.set_sizes(512, 512, 2)
            self.capture_state = 1
            self.cnt = 0
        else:
            self.capture_state = 0
            self.capture_button.setText("Start Capture")
            self.capture_file.close()

    

    def clip(self, pos):
        if (pos.x() < self.EDGE):
            pos.setX(self.EDGE)
        if (pos.y() < self.EDGE):
            pos.setY(self.EDGE)

        if (pos.x() > (511-self.EDGE)):
            pos.setX(511-self.EDGE)
        if (pos.y() > (511-self.EDGE)):
            pos.setY(511-self.EDGE)

        
        return pos


    def mainloop(self, args, camera):

 
        while(self.win.quit == 0):
            time.sleep(0.03)
            
            self.statusBar.showMessage(str(self.cnt), 2000)
            app.processEvents()
            self.array = camera.get_frame()
            if (self.capture_state == 1):
                self.capture_file.add_image(self.array)

            need_update = False
            if (self.update_state == 1):
                need_update = True
            if (self.update_state == 0 and self.cnt % 30 == 0):
                need_update = True

            if (need_update):
                self.imv.setImage(self.array, autoRange=False, autoLevels=False, autoHistogramRange=False)
                pos = self.clip(self.pos)
                
               
                sub = self.array[int(pos.x())-self.EDGE:int(pos.x())+self.EDGE, int(pos.y())-self.EDGE:int(pos.y())+self.EDGE].copy()
                sub = np.rot90(sub, 1)
                sub = np.flip(sub, axis=0)
                min = np.min(sub)
                max = np.max(sub)
                fwhm = fit_gauss_circular(sub)


                self.txt1.setText("FWHM= " + "{:.2f}  ".format(fwhm) + "min=" + str(min) + " max=" + str(max) + " frame=" + str(self.cnt))
                sub =  sub * int(65535/max)
                sub = sub.astype(np.uint16)
                sub = cv2.resize(sub, dsize=(256, 256), interpolation=cv2.INTER_NEAREST)
                pixmap = self.convert_nparray_to_QPixmap(sub)
                self.zoom_view.setPixmap(pixmap)
            #if (cnt % 10 == 0):
            #    imv.ui.histogram.setImageItem(pg.ImageItem(array))
            self.cnt = self.cnt + 1

        if (self.capture_state == 1):
            self.capture_file.close()



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", type=str, default = 'emccd_capture_', help="generic file name")
    parser.add_argument("-exp", type=float, default = 1.0, help="exposure in seconds (default 1.0)")
    parser.add_argument("-gain", "--gain", type=int, default = 101, help="camera gain (default 200)")
    parser.add_argument("-bin", "--bin", type=int, default = 1, help="camera binning (default 1-6)")
    parser.add_argument("-guide", "--guide", type=int, default = 0, help="frame per guide cycle (0 to disable)")
    parser.add_argument("-count", "--count", type=int, default = 100, help="number of frames to capture")
    args = parser.parse_args()

    ui = UI(args)
    camera = fake_emccd(-30)
    ui.mainloop(args, camera)


