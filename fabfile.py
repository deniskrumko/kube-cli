from fabric.api import local, task

pypy = 'https://pypi.org'
test_pypy = 'https://test.pypi.org'


@task
def isort():
    """Fix imports formatting."""
    local('isort kube_cli -y -rc')


@task
def pep8(path='kube_cli'):
    """Check PEP8 errors."""
    return local('flake8 --config=.flake8 {}'.format(path))


@task
def lock():
    """Lock dependencies."""
    return local('pipenv lock')


@task
def install_dev():
    """Install packages for local development."""
    return local('pipenv install --dev')


@task
def build():
    """Build package for pypy."""
    local('rm -rf build dist kube_cli.egg-info')
    local('python3 setup.py sdist bdist_wheel')


@task
def pip_dev():
    """Show command how to install dev package."""
    print('pip3 install --index-url {test_pypy}/simple/ --no-deps kube-cli')


@task
def upload_to_dev():
    """Upload package to dev pypy."""
    local(
        f'python3 -m twine upload --repository-url {test_pypy}/legacy/ dist/*'
    )


@task
def upload_to_prod():
    """Upload package to real pypy."""
    local(f'python3 -m twine upload dist/*')
