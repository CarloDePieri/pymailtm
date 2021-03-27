from invoke import task


poetry_pypi_testing = "testpypi"
# Use the minimum python version required by the package
default_python_bin = "python3.7"


# If the most currently activated python version is desired, use 'inv install -p latest'
@task
def install(c, python=default_python_bin):
    if python == "latest":
        # don't do anithing here: poetry will use the default python version
        pass
    else:
        c.run("poetry env use {}".format(python))
    c.run("poetry install")


@task
def rm_venv(c):
    c.run("rm -rf .venv")


# Use this to change quickly python version
@task(rm_venv)
def reinstall(c, python=default_python_bin):
    install(c, python)


@task
def build(c):
    c.run("poetry build")


@task(build)
def publish_test(c):
    c.run(f"poetry publish -r {poetry_pypi_testing}")


@task(build)
def publish(c):
    c.run("poetry publish")


@task()
def test(c):
    c.run("poetry run pytest", pty=True)


@task()
def test_spec(c):
    c.run("poetry run pytest -p no:sugar --spec", pty=True)


@task()
def clear_cassettes(c):
    c.run("rm -rf tests/cassettes")
    print("Cleared!")


@task()
def test_cov(c):
    c.run("mkdir -p coverage")
    c.run("poetry run pytest --cov=pymailtm --cov-report annotate:coverage/cov_annotate --cov-report html:coverage/cov_html", pty=True)


@task(test_cov)
def html_cov(c):
    c.run("xdg-open coverage/cov_html/index.html")


@task
def run(c, n=False, l=False):
    if l:
        c.run("poetry run pymailtm -l", pty=True)
    elif n:
        c.run("poetry run pymailtm -n", pty=True)
    else:
        c.run("poetry run pymailtm", pty=True)
