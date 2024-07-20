import os
import pkgutil
import importlib


def load_modules():
    pkg_path = os.path.dirname(__file__)
    pkg_name = "dingraia.module"

    for _, file, _ in pkgutil.iter_modules([pkg_path]):
        importlib.import_module(pkg_name + '.' + file)
