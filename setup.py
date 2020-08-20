from setuptools import setup

setup(
    name="pymailtm",
    version="0.1",
    packages=["pymailtm"],
    install_requires=[
        "random-username>=1.0.2",
        "requests>=2.24.0"
    ],
    url="https://github.com/CarloDePieri/pymailtm",
    license='GPLv3',
    author='Carlo De Pieri',
    author_email='depieri.carlo@gmail.com',
    description='A python wrapper around mail.tm web api.',
)
