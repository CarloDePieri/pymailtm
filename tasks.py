from invoke import task


@task
def run(c):
    c.run("pipenv run python run.py", pty=True)
