#!/usr/bin/env python3

from setuptools import setup

from kube_cli import get_version

with open('README.rst') as f:
    readme = f.read()

setup(
    name='kube-cli',
    version=get_version(),
    description='CLI for Kubernetes that simplifies usage of kubectl',
    long_description=readme,
    author='Denis Krumko',
    author_email='dkrumko@gmail.com',
    url='https://github.com/deniskrumko/kube-cli',
    license="MIT",
    entry_points={
        'console_scripts': [
            'kube = kube.main:main',
        ],
    },
    packages=['kube_cli'],
    python_requires=">=3.6",
    keywords='CLI, Kubernetes',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
    ],
)
