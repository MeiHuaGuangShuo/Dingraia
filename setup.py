from setuptools import setup, find_packages
setup(
    name='dingraia',
    version='2.0.0',
    packages=find_packages(),
    url='https://github.com/MeiHuaGuangShuo/Dingraia',
    author='MeiHuaGuangShuo',
    author_email='meihuaguangshuo@gmail.com',
    description='A Dingtalk robot framework based on Python',
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
