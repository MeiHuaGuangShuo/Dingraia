from setuptools import setup, find_packages
from dingraia.VERSION import VERSION

setup(
    name='dingraia',
    version=VERSION,
    packages=find_packages(),
    url='https://github.com/MeiHuaGuangShuo/Dingraia',
    author='MeiHuaGuangShuo',
    author_email='meihuaguangshuo@gmail.com',
    description='A Dingtalk robot framework based on Python, supported http and stream mode.',
    long_description='A Dingtalk robot framework, easier to use.',
    install_requires=[
        "loguru",
        "requests",
        "aiohttp",
        "pycryptodome",
        "websockets",
        "rich",
        "deprecation"
    ],
    python_requires='>3.7',
    zip_safe=True,
)
