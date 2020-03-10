#!/usr/bin/env python3

from setuptools import setup

with open('README.rst') as f:
    readme = f.read()

setup(
    name='kube-cli',
    version='0.0.1',
    description='CLI for Kubernetes that simplifies usage of kubectl',
    long_description=readme,
    author='Denis Krumko',
    author_email='dkrumko@gmail.com',
    url='https://github.com/deniskrumko/kube-cli',
    license="MIT",
    entry_points={
        'console_scripts': [
            'kube = kube.main',
        ],
    },
    packages=['kube-cli'],
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
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
    ],
)