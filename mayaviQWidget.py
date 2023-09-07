import time

from PyQt5 import QtWidgets
import os
import numpy as np
from numpy import cos
from mayavi.mlab import contour3d, clf, figure, plot3d
from class_biaoding import Biaoding

os.environ['ETS_TOOLKIT'] = 'qt4'
from pyface.qt import QtGui, QtCore
from traits.api import HasTraits, Instance, on_trait_change, Button
from traitsui.api import View, Item
from mayavi.core.ui.api import MayaviScene, MlabSceneModel, SceneEditor


## create Mayavi Widget and show
class Visualization(HasTraits):
    scene = Instance(MlabSceneModel, ())

    @on_trait_change('scene.activated')
    def update_plot(self):
        # init
        clf()

    view = View(Item('scene', editor=SceneEditor(scene_class=MayaviScene),
                     height=250, width=300, show_label=False),
                    resizable=True)


class MayaviQWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.layout = QtGui.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.visualization = Visualization()
        self.ui = self.visualization.edit_traits(parent=self,
                                                 kind='subpanel').control
        self.layout.addWidget(self.ui)
        self.ui.setParent(self)

    def clearAll(self):
        clf(figure=self.visualization.scene.mayavi_scene)

    def again(self):
        clf(figure=self.visualization.scene.mayavi_scene)
        time.sleep(2)
        filePath = '../use4demo/dat/20230802150247.dat'
        savePath = '../use4demo/bin/20230802150247.bin'
        temp = Biaoding(filePath, savePath, "dg")
        temp.readDatDG(up2down=False)
        temp.integrate_show(self.visualization.scene.mayavi_scene)  # 使用的时候把fig注释掉

    def show(self):
        pass

#### PyQt5 GUI ####
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):

    ## MAIN WINDOW
        MainWindow.setObjectName("MainWindow")
        MainWindow.setGeometry(200,200,1100,700)

    ## CENTRAL WIDGET
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)

    ## GRID LAYOUT
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")


    ## BUTTONS
        self.button_default = QtWidgets.QPushButton(self.centralwidget)
        self.button_default.setObjectName("button_default")
        self.gridLayout.addWidget(self.button_default, 1, 0, 1, 1)

        self.button_previous_data = QtWidgets.QPushButton(self.centralwidget)

        self.button_previous_data.setObjectName("button_previous_data")
        self.gridLayout.addWidget(self.button_previous_data, 1, 1, 1, 1)

    ## Mayavi Widget 1
        container = QtGui.QWidget()
        self.mayavi_widget1 = MayaviQWidget(container)
        self.gridLayout.addWidget(self.mayavi_widget1, 0, 0, 1, 1)
    ## Mayavi Widget 2
        # container1 = QtGui.QWidget()
        # self.mayavi_widget2 = MayaviQWidget(container1)
        # self.gridLayout.addWidget(self.mayavi_widget2, 0, 1, 1, 1)

    ## SET TEXT
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Simulator"))
        self.button_default.setText(_translate("MainWindow","Default Values"))
        self.button_previous_data.setText(_translate("MainWindow","Previous Values"))


class MyWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.button_default.clicked.connect(self.clearMayavi)
        self.button_previous_data.clicked.connect(self.nextMayavi)

    def clearMayavi(self):
        self.mayavi_widget1.clearAll()

    def nextMayavi(self):
        self.mayavi_widget1.again()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    MainWindow = MyWindow()

    MainWindow.show()
    sys.exit(app.exec_())
