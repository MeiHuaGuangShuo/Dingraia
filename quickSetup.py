import os
import platform
from shutil import copy2

os.chdir(os.path.dirname(os.path.abspath(__file__)))

appKey = input("输入AppKey: ")
appSecret = input("输入AppSecret: ")

if not os.path.exists("main_example.py"):
    print("克隆不完整，请重新克隆 / Breach incomplete, please clone again.")
    os.system("pause")
    exit(1)

copy2("main_example.py", "main.py")

with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("'AppKey'", f"'{appKey}'")
content = content.replace("'robotCode'", f"'{appKey}'")
content = content.replace("'AppKey1'", f"'{appKey}'")
content = content.replace("'AppSecret'", f"'{appSecret}'")
content = content.replace("'AppSecret1'", f"'{appSecret}'")

with open("main.py", "w", encoding="utf-8") as f:
    f.write(content)

print("是否创建 Python 虚拟环境？/ Create Python virtual environment? (y/n): ")
if input("> ") in ("y", "Y"):
    if platform.system() == "Windows":
        os.system("python -m venv venv")
        os.system(r".\venv\python.exe -m pip install -r requirements.txt")
        with open("start.bat", "w", encoding="utf-8") as f:
            f.write(f"@echo off\n.\\venv\\Scripts\\python.exe .\\main.py")
        print("使用 start.bat 启动程序 / Use start.bat to start the program.")
        os.system("pause")
        exit(0)
    else:
        os.system("python3 -m venv venv")
        os.system(r"./venv/bin/pip install -r requirements.txt")
        with open("start.sh", "w", encoding="utf-8") as f:
            f.write(f"#!/bin/bash\n./venv/bin/python ./main.py")
        print("使用 start.sh 启动程序 / Use start.sh to start the program.")
        os.system("chmod +x start.sh")
        os.system("bash start.sh")
        exit(0)
else:
    if platform.system() == "Windows":
        with open("start.bat", "w", encoding="utf-8") as f:
            f.write(f"@echo off\npython .\\main.py")
        print("使用 start.bat 启动程序 / Use start.bat to start the program.")
        os.system("pause")
        exit(0)
    else:
        with open("start.sh", "w", encoding="utf-8") as f:
            f.write(f"#!/bin/bash\npython ./main.py")
        os.system("chmod +x start.sh")
        print("使用 start.sh 启动程序 / Use start.sh to start the program.")
        os.system("pause")
        exit(0)
