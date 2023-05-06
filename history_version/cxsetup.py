#coding=utf-8
#cxsetup.py代码
from cx_Freeze import setup, Executable
setup(
    name="test",
    version="0.1",
    description="Test application",
    author="zhy",
    executables=[Executable("history_version/MyWindow.py")]
)