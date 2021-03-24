# pymailtm

This is a python interface to the web api of [mail.tm](https://mail.tm).

The api is documented [here](https://api.mail.tm/).

## Dependencies

`xclip` or `xsel` for clipboard copying.

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
in a quick html view.

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

Now download the repo with git:

```bash
git clone git@github.com:CarloDePieri/pymailtm.git
cd pymailtm
inv install
```

This will try to create a virtualenv based on `python3.7` and install there all
project's dependencies. If a different python version is wanted, it can be
used with the `--python` (`-p`) flag like this:

```bash
inv install -p python3.8
```

The script can now be run directly by launching `inv run`. It also accepts flags,
for example:

```bash
inv run -n
```

