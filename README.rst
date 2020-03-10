KUBE-CLI
========

.. image:: https://img.shields.io/pypi/v/kube-cli.svg
    :target: https://pypi.org/project/kube-cli/
    :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/kube-cli.svg
    :target: https://pypi.org/project/kube-cli/
    :alt: Python versions

.. image:: https://img.shields.io/pypi/l/kube-cli.svg
    :target: https://raw.githubusercontent.com/deniskrumko/kube-cli/master/LICENSE
    :alt: License


Command line interface for Kubernetes that simplifies usage of kubectl.


TODO
====

- Умный поиск pod'a
- Readme

1. Help
kube
kube --help
kube help

2.1 All namespaces

kube all
- Parses command: kubectl get pods --all-namespaces

2. Namespace

kube <namespace>
- Namespace not found
- If found then show "kube <namespace> pods"

3. Pods

kube <namespace> pods
- List of pods

4. Logs of pod
kube <namespace> <pod> logs

5. Bash
kube <namespace> <pod> bash
