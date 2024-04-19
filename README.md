# BiaodingProgram  ---- Calibration Program
## version-1.05 Support Multi-brand

Support multiple Lidar 270mini、3000 of Duge.  
支持杜格270mini、杜格3000的多雷达。  

## Introduction
This repository contains the project used for vertical lidar calibration.  You can get the calibration datas easily through the GUI window of the application.  
By the way, the word "Biaoding" means "calibration" in Chinese pingyin.
### Content
* python program .py files
* .ui file (which is used to design the GUI)
* packing file 
* .png .ico files
* hook_file 
* README.md
  
The ui file can be opened by Qtdesigner , you can design the GUI easily by dragging the block. The packing file, here is the mywindow.spec, the file helps you find the import files libraries. The spec file which is used to pack the program into an executive file. Hook_file is the folder contains hook files which can help you find the data and include when you are packing.

 
**注意**在使用UI to py工具的时候，生成的newGui.py最后一行的代码需要移动到开头。    
**Note**The file newGui.py generated by UI to py tools need modify a little bit. Move the last line to the begining part to avoid the error.
> #This line should move to the begining of file.  
> from mayaviQWidget import MayaviQWidget

## Require
**python 3.6**  
**PyQt5**  
**vtk**    (compatible version for python 3.6)  
**mayavi** (compatible for your python and your vtk version)

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

Now the version v1.05 is developing. The main feature of new version is supporting DuGe Lidar 270mini.
You can find it on the branch 270mini.
![Sample](/images/v1.05.png)



## Thanks
Thank to Sweaterz，for his efforts to build this project.


First Edit by Sweaterz, 2023.9.7.17:10 UTC+8:00.

