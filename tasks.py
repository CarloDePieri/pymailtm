from invoke import task


@task
def run(c, n=False, l=False):
    if l:
        c.run("pipenv run python scripts/pymailtm -l", pty=True)
    elif n:
        c.run("pipenv run python scripts/pymailtm -n", pty=True)
    else:
        c.run("pipenv run python scripts/pymailtm", pty=True)
