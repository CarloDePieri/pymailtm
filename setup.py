import io
import re
from setuptools import setup


with io.open('pymailtm/__init__.py', 'rt', encoding='utf8') as f:
    version = re.search(r'__version__ = \'(.*?)\'', f.read()).group(1)

setup(
    name="pymailtm",
    version=version,
    packages=["pymailtm"],
    install_requires=[
        "random-username>=1.0.2",
        "requests>=2.24.0",
        "pyperclip>=1.8.0"
    ],
    url="https://github.com/CarloDePieri/pymailtm",
    license='GPLv3',
    author='Carlo De Pieri',
    author_email='depieri.carlo@gmail.com',
    description='A python wrapper around mail.tm web api.',
    include_package_data=True,
    scripts=["scripts/pymailtm"],
)
