[![PyPI](https://img.shields.io/pypi/v/pymailtm)](https://pypi.org/project/pymailtm/) [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pymailtm)](https://pypi.org/project/pymailtm/) [![CI Status](https://img.shields.io/github/workflow/status/CarloDePieri/pymailtm/prod?logo=github)](https://github.com/CarloDePieri/pymailtm/actions/workflows/prod.yml) [![Coverage Status](https://coveralls.io/repos/github/CarloDePieri/pymailtm/badge.svg?branch=master)](https://coveralls.io/github/CarloDePieri/pymailtm?branch=master) [![Maintenance](https://img.shields.io/maintenance/yes/2022)](https://github.com/CarloDePieri/pymailtm/)

This is a command line interface and python web-api wrapper for [mail.tm](https://mail.tm).

The api is documented [here](https://api.mail.tm/).

## Dependencies

`xclip` or `xsel` for clipboard copying.

A browser to open incoming html emails.

## Installation

#### With pip

```bash
pip install pymailtm
```

#### In a virtual env

```bash
python -m venv .venv
source .venv/bin/activate
pip install pymailtm
```

## Usage

The utility can be called with:

```bash
pymailtm
```

Remember that if you are in a virtual env you need to activate it first.

By default the command recover the last used account, copy it to the clipboard
and wait for a new message to arrive: when it does, it's opened in the browser
in a quick&dirty html view.

Exit the waiting loop by pressing `Ctrl+c`.

Calling the utility with the flag `-l` will print the account credentials, open
in the browser the [mail.tm](https://mail.tm) client and exit.

The flag `-n` can be used to force the creation of a new account.

## Security warnings

This is conceived as an **insecure**, fast throwaway temp mail account generator.

**DO NOT** use it with sensitive data.

Mails that arrive while the utility is running will be saved in **plain text**
files in the system temporary folder (probably `/tmp/`) so that they can be
opened by the browser.

The last used account's data and credentials will be saved in
**plain text** in `~/.pymailtm`.


## Development

Install [invoke](http://pyinvoke.org/) and [poetry](https://python-poetry.org/):

```bash
pip install invoke poetry
```

Now clone the git repo:

```bash
git clone git@github.com:CarloDePieri/pymailtm.git
cd pymailtm
inv install
```

This will try to create a virtualenv based on `python3.7` and install there all
project's dependencies. If a different python version is preferred, it can be
selected by specifying  the `--python` (`-p`) flag like this:

```bash
inv install -p python3.8
```

The script can now be run directly by launching `inv run`. It also accepts flags,
for example:

```bash
inv run -n
```

The test suite can be run with commands:

```bash
inv test         # run the test suite
inv test --full  # run even tests that requires a graphical environment
inv test-spec    # run the tests while showing the output as a spec document
inv test-cov     # run the tests suite and produce a coverage report
```

Tests take advantage of [vcrpy](https://github.com/kevin1024/vcrpy) to cache
network requests and responses. If you need to clear this cache run:

```bash
inv clear-cassettes
```

To test the github workflow with [act](https://github.com/nektos/act):

```bash
inv act-dev           # test the dev workflow
inv act-dev -c shell  # open a shell in the act container (the above must fail first!)
inv act-dev -c clean  # stop and delete a failed act container
```
