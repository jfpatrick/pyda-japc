"""
setup.py for pyda-japc.

For reference see
https://packaging.python.org/guides/distributing-packages-using-setuptools/

"""
from pathlib import Path
from setuptools import setup, find_packages
from setuptools_scm import get_version


HERE = Path(__file__).parent.absolute()
with (HERE / 'README.md').open('rt') as fh:
    LONG_DESCRIPTION = fh.read().strip()


REQUIREMENTS: dict = {
    'core': [
        'pyds-model',
        'pyda',
        'pyrbac',
        'cmmnbuild-dep-manager~=2.7',
    ],
    'test': [
        'pytest',
    ],
    'doc': [
        'acc-py-sphinx',
    ],
}

# Get the version from setuptools_scm using the same scheme defined
# in pyproject.toml. Note that we use a no-local-version scheme
# (where versions are defined as "X.Y.Z.devN[+local-scheme]") so that
# the entry-point follows a valid entry-point specification as per
# https://packaging.python.org/specifications/entry-points/.
VERSION = get_version(local_scheme="no-local-version")

setup(
    name='pyda-japc',

    author='Acc-Py team',
    author_email='acc-python-support@cern.ch',
    description='A JAPC provider for PyDA',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    url='https://gitlab.cern.ch/acc-co/devops/python/prototypes/pyda',

    packages=find_packages(),
    python_requires='~=3.7',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],

    install_requires=REQUIREMENTS['core'],
    extras_require={
        **REQUIREMENTS,
        # The 'dev' extra is the union of 'test' and 'doc', with an option
        # to have explicit development dependencies listed.
        'dev': [req
                for extra in ['dev', 'test', 'doc']
                for req in REQUIREMENTS.get(extra, [])],
        # The 'all' extra is the union of all requirements.
        'all': [req for reqs in REQUIREMENTS.values() for req in reqs],
    },
    entry_points={
        # Register with cmmnbuild_dep_manager.
        'cmmnbuild_dep_manager': [f'pyda_japc={VERSION}'],
    },
)
