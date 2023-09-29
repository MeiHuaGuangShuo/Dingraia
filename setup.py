from setuptools import setup, find_packages

setup(
    name='dingraia',
    version='2.0.2',
    packages=find_packages(),
    url='https://github.com/MeiHuaGuangShuo/Dingraia',
    author='MeiHuaGuangShuo',
    author_email='meihuaguangshuo@gmail.com',
    description='A Dingtalk robot framework based on Python, supporting http and stream mode.',
    long_description='A Dingtalk robot framework based on official, easier and advanced to use.',
    install_requires=[
        "loguru",
        "requests",
        "aiohttp",
        "pycryptodome",
        "websockets"
    ],
    python_requires='>3.7',
    zip_safe=True,
)
