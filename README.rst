kube-cli
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


Installation
^^^^^^^^^^^^
.. code-block:: bash

    pip install kube-cli


Requirements
^^^^^^^^^^^^

- python 3.6 or higher
- `kubectl <https://kubernetes.io/docs/tasks/tools/install-kubectl/>`_
- kubectl config file in ~/.kube/config

How to use
^^^^^^^^^^

.. code-block:: bash

    # show help
    kube help

    # List all namespaces / pods
    kube all ns
    kube all pods

    # Find namespace / pod
    kube find ns <query>
    kube find pod <query>

    # Operations with namespace
    kube <namespace>
    kube <namespace> pods

    # Scaling deployments
    kube <namespace> scale
    kube <namespace> scale <deployment>
    kube <namespace> scale <deployment> <value>

    # Operations with pod
    kube <namespace> <pod> logs
    kube <namespace> <pod> logs -f
    kube <namespace> <pod> bash

Fuzzy search
^^^^^^^^^^^^

Fuzzy search is a killing feature that allows to search namespaces and pods by short equivalents.

For example, following commands are equal:

.. code-block:: bash

    kube 1234 redismetric logs

    kube jira-1234 rd-jira-5103-redis-metrics-57dff4f8b7-5c49k logs
