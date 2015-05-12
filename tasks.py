from invoke import run, task

@task
def test(cov=True, verbose=False):
    """
    Runs all tests in the 'tests/' directory
    """
    cmd = 'py.test tests'
    if verbose:
        cmd += ' -v'
    if cov:
        cmd += ' --cov-report term-missing --cov-config .coveragerc --cov .'

    run(cmd, pty=True)
