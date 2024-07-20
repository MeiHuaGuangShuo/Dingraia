import os
import pkgutil


def load_modules():
    pkg_path = os.path.dirname(__file__)
    pkg_name = os.path.basename(pkg_path)

    for _, file, _ in pkgutil.iter_modules([pkg_path]):
        __import__(pkg_name + '.' + file)
