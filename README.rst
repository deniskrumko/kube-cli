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

Python 3.6 or higher

How to use
^^^^^^^^^^

.. code-block:: bash

    kube help                     # show all commands

    kube all ns                   # List of all namespaces
    kube all pods                 # List of all pods in all namespaces

    kube find ns <query>		     	# Find namespace
    kube find pod <query>			    # Find pod

    kube <namespace>			        # List of pods in namespace
    kube <namespace> pods			    # List of pods in namespace

    kube <namespace> <pod> logs		# Stream logs from pod
    kube <namespace> <pod> bash		# Run bash in pod

Fuzzy search
^^^^^^^^^^^^

Fuzzy search is a killing feature that allows to search namespaces and pods by short eqivalents.

For example, following commands are equal:

.. code-block:: bash

    kube 1234 redismetric

    kube jira-1234 rd-jira-5103-redis-metrics-57dff4f8b7-5c49k
