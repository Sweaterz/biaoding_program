# bd_program  
## Introduction
This repository contains the project used for vertical lidar calibration.  You can get the calibration datas easily through the GUI window of the application.
### Content
* python program .py files
* .ui file (which is used to design the GUI)
* packing file 
* .png .ico files
* hook_file 
* README.md

 ui file can be opened by Qtdesigner , you can design the GUI easily by dragging the block. The packing file, here is the mywindow.spec, the file helps you find the import files libraries. The spec file which is used to pack the program into an executive file. Hook_file is the folder contains hook files which can help you find the data and include when you are packing.

## Require
python 3.6  
PyQt5
vtk compatible version for python 3.6  
mayavi compatible for your python and your vtk version

## Setup Environment
Firstly you need to pip install vtk.  
Then pip install mayavi.
pip install pyqt5  

## Packing Program
just to use the pyinstaller
You need to install first.
pip install pyinstaller

And then you can using pyinstaller mywindow.spec in your command line to build a package.
The packed program is located in dist directory. You could use it or distribute it conveniently.


## Published Version
### Windows 64 bit:
[version v1.04](https://pan.baidu.com/s/1HLnKvbfyMUEazOsZk6PLpA?pwd=1234)<br />  
>
>
## Thanks
Thanks Sweaterz.


First Edit by Sweaterz, 2023.9.7.17:10 CST.

