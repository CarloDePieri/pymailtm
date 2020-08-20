# pymailtm

This is a python interface to the web api of [mail.tm](https://mail.tm).

The api is documented [here](https://api.mail.tm/).

## Installation

#### With pip

```bash
pip install --user git+https://github.com/CarloDePieri/pymailtm.git#egg=pymailtm
```

#### In a virtual env

```bash
python -m venv .venv
source .venv/bin/activate
pip install git+https://github.com/CarloDePieri/pymailtm.git#egg=pymailtm
```

#### With Pipenv

```bash
pipenv --three
pipenv install git+https://github.com/CarloDePieri/pymailtm.git#egg=pymailtm
```

#### With git and Pipenv (dev)

```bash
git clone git@github.com:CarloDePieri/pymailtm.git
pipenv install --dev
```

## Usage

You can now import the library `pymailtm` and call the utility with the same name:

```bash
pymailtm
```

Remember that if you are in a virtual env you need to activate it first.

If you are using Pipenv you can use directly:

```bash
pipenv run pymailtm
```

If using git + Pipenv, and have [invoke](https://github.com/pyinvoke/invoke) installed, you can even:

```bash
inv run
```

Exit the utility by pressing `Ctrl+c`.

## Security warnings

This is conceived as an insecure, fast throwaway temp mail account generator.

Do not use it with sensitive data.

Mails that arrive while the utility is running will be saved in clear text files in a temp folder (probably `/tmp/`) so 
that they can be opened by the browser.
