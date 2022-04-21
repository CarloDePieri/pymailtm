from invoke import task


poetry_pypi_testing = "testpypi"
# Use the minimum python version required by the package
default_python_bin = "python3.7"


# If the most currently activated python version is desired, use 'inv install -p latest'
@task
def install(c, python=default_python_bin):
    if python == "latest":
        # don't do anything here: poetry will use the default python version
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
def publish_coverage(c):
    c.run(f"poetry run coveralls")


@task(build)
def publish_test(c):
    c.run(f"poetry publish -r {poetry_pypi_testing}")


@task(build)
def publish(c):
    c.run("poetry publish")


@task()
def test(c, full=False, s=False, t=False):
    marks = ""
    capture = ""
    if t:
        marks = " -m 'runthis'"
    elif not full:
        marks = " -m 'not graphical'"
    if s:
        capture = " -s"
    c.run(f"poetry run pytest{capture}{marks}", pty=True)


@task()
def test_spec(c, full=False):
    marks = ""
    if not full:
        marks = " -m 'not graphical'"
    c.run(f"poetry run pytest -p no:sugar --spec{marks}", pty=True)


@task()
def clear_cassettes(c):
    c.run("rm -rf tests/cassettes")
    print("Cleared!")


@task()
def test_cov(c, full=False):
    c.run("mkdir -p coverage")
    marks = ""
    if not full:
        marks = " -m 'not graphical'"
    c.run(f"poetry run pytest --cov=pymailtm --cov-report annotate:coverage/cov_annotate --cov-report html:coverage/cov_html{marks}", pty=True)


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

#
# ACT
#
act_dev_ctx = "act-dev-ci"
act_prod_ctx = "act-prod-ci"
act_secrets_file = ".secrets"


@task
def act_prod(c, cmd=""):
    if cmd == "":
        c.run("act -W .github/workflows/prod.yml", pty=True)
    elif cmd == "shell":
        c.run(f"docker exec --env-file {act_secrets_file} -it {act_prod_ctx} bash", pty=True)
    elif cmd == "clean":
        c.run(f"docker rm -f {act_prod_ctx}", pty=True)


@task
def act_dev(c, cmd=""):
    if cmd == "":
        c.run("act -W .github/workflows/dev.yml", pty=True)
    elif cmd == "shell":
        c.run(f"docker exec --env-file {act_secrets_file} -it {act_dev_ctx} bash", pty=True)
    elif cmd == "clean":
        c.run(f"docker rm -f {act_dev_ctx}", pty=True)
