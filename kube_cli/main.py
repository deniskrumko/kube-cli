import os
import subprocess
import sys
from typing import Callable, Iterable, Optional, Union


class KubeCLI:
    """Main class for running kube CLI."""

    def __init__(self):
        """Initialize class instance."""
        self.args = sys.argv[1:]
        self.timeout = 20

    def run(self):
        """Run command."""
        # kube help
        if not self.args or 'help' in self.args[0]:
            return self.show_help()

        # kube all ns
        # kube all pods
        if self.args[0] == 'all':
            return self.command_for_namespace_or_pod(
                for_namespace=self.show_all_namespaces,
                for_pod=self.show_all_pods,
                help_text=(
                    '\nkube all <g>ns</g>\t-- List of all namespaces'
                    '\nkube all <g>pods</g>\t-- List of all pods'
                ),
            )

        # kube find ns <...>
        # kube find pod <...>
        if self.args[0] == 'find':
            return self.command_for_namespace_or_pod(
                for_namespace=self.find_namespace,
                for_pod=self.find_pod,
                query=self.get_argument(2),
                help_text=(
                    '\nkube find <g>ns</g> <b><query></b>\t-- Find namespace'
                    '\nkube find <g>pod</g> <b><query></b>\t-- Find pod'
                ),
            )

        # kube <namespace>
        # kube <namespace> pods
        if len(self.args) == 1 or self.args[1] == 'pods':
            return self.get_pods_in_namespace()

        # kube <namespace> <pod> logs
        # kube <namespace> <pod> bash
        return self.run_pod_commands()

    def command_for_namespace_or_pod(
        self,
        for_namespace: Callable,
        for_pod: Callable,
        help_text: str,
        **kwargs,
    ):
        """Run command where first parameter is namespace or pod.

        Method parser first argument and calls specified method.

        """
        try:
            param = self.args[1].lower()
        except IndexError:
            param = ''

        if param in ('ns', 'namespaces'):
            return for_namespace(**kwargs)
        elif 'pod' in param:
            return for_pod(**kwargs)

        self.print(help_text)

    def show_all_namespaces(self):
        """Show all existing namespaces."""
        namespaces = self.get_all_namespaces()
        if not namespaces:
            return self.print('\n<r>Cannot find any namespace</r>')

        self.print('\n<g>All available namespaces</g>\n')
        self.print_results(namespaces)

    def show_all_pods(self):
        """Show all existing pods."""
        self.print_namespaces_and_pods(results=self.request_data())

    def get_pods_in_namespace(self):
        """Get list of pods in single namespace."""
        query = self.args[0].lower()
        results = self.find_namespace_by_query(query=query)
        if not results:
            return self.print(f'\n<r>No namespace matched query "{query}"</r>')

        namespace = self.select_from_multiple_results(
            results=results,
            query=query,
            exact_match=self.args[0],
        )
        if not namespace:
            return

        output = self.get_output(f'get pods --namespace={namespace}')[1:-1]
        if not output:
            return self.print(f'\n<r>No pods in namespace "{namespace}"</r>\n')

        self.print(f'\n<g>Available pods in namespace "{namespace}"</g>\n')
        self.print_results([line.split()[0] for line in output])

    def find_namespace(self, query: str):
        """Find namespace by query."""
        if not query:
            return self.print(
                '\nkube find ns <g><query></g> -- Find namespace'
            )

        results = self.find_namespace_by_query(query)
        if not results:
            return self.print(f'\n<r>No namespace matched query "{query}"</r>')

        self.print('\n<g>Found namespaces</g>\n')
        self.print_results(results, query)

    def find_pod(self, query: str):
        """Find pod by query."""
        if not query:
            return self.print('\nkube find pod <g><query></g>\t-- Find pod')

        results = self.find_pod_by_query(query)
        if not results:
            return self.print(f'\n<r>No pods matched query "{query}"</r>')

        self.print('\n<g>Found pods</g>\n')
        self.print_results(results, query)  # TODO: Show namespace too

    def run_pod_commands(self):
        """Run pod commands."""
        def help_text():
            return self.print(
                '\nkube <b><namespace></b> <b><pod></b> <g>logs</g> '
                '-- Stream logs from pod'
                '\nkube <b><namespace></b> <b><pod></b> <g>bash</g> '
                '-- Run bash in pod'
            )

        if len(self.args) != 3:
            return help_text()

        namespace = self.args[0].lower()
        pod_name = self.args[1].lower()
        command = self.args[2].lower()

        clean_namespace = self.clear_str(namespace)
        clean_pod_name = self.clear_str(pod_name)
        results = [
            (_namespace, _pod_name)
            for _namespace, _pod_name, *other in self.request_data()
            if (
                clean_namespace in self.clear_str(_namespace)
                and clean_pod_name in self.clear_str(_pod_name)
            )
        ]

        if not results:
            return self.print(
                f'\n<r>Cannot find namespace "{namespace}" '
                f'and pod "{pod_name}"</r>'
            )

        values = self.select_from_multiple_results(
            results=results,
            exact_match=(self.args[0], self.args[1]),
            print_results=False,
        )
        if not values:
            self.print('\n<y>Found more than namespace/pod</y>')
            return self.print_namespaces_and_pods(
                results=results,
                namespace_query=namespace,
                pod_name_query=pod_name,
            )

        if command == 'logs':
            return self.stream_pod_logs(*values)
        if command == 'bash':
            return self.run_bash_in_pod(*values)

        self.print(f'\nUnknown command: <r>{command}</r>')
        return help_text()

    def stream_pod_logs(self, namespace: str, pod_name: str):
        """Stream logs from pod."""
        self.print_namespace_and_pod_name(namespace, pod_name)
        input('Press enter to start streaming logs\n')
        self.execute(f'logs --namespace={namespace} -f {pod_name}')

    def run_bash_in_pod(self, namespace: str, pod_name: str):
        """Run bash in pod."""
        self.print_namespace_and_pod_name(namespace, pod_name)
        self.execute(f'exec -it --namespace={namespace} {pod_name} -- bash')

    def show_help(self):
        """Show help for program."""
        help_text = '''
        <g>kube</g> is a CLI for Kubernetes that simplifies usage of kubectl

          Find more information at: https://github.com/deniskrumko/kube-cli

        <g>Basic Commands</g>

          kube <g>all ns</g>\t\t\t\tList of all namespaces
          kube <g>all pods</g>\t\t\t\tList of all pods in all namespaces
          kube <g>find ns</g> <b><query></b>\t\tFind namespace
          kube <g>find pod</g> <b><query></b>\t\tFind pod
          kube <b><namespace></b>\t\t\tList of pods in namespace
          kube <b><namespace></b> <g>pods</g>\t\t\tList of pods in namespace
          kube <b><namespace></b> <b><pod></b> <g>logs</g>\t\tStream logs from pod
          kube <b><namespace></b> <b><pod></b> <g>bash</g>\t\tRun bash in pod

        <g>Fuzzy search</g>

          Fuzzy search is a <r>killing feature</r> that allows to search namespaces and pods by short eqivalents.
          For example, following commands are equal:

          > kube <b>1234 redismetric</b>
          > kube jira-<b>1234</b> rd-jira-5103-<b>redis-metrics</b>-57dff4f8b7-5c49k

        ''' # noqa
        self.print(help_text.replace('\n        ', '\n'))

    # Helper methods

    def get_argument(self, index: int) -> str:
        """Get program argument by index."""
        try:
            return self.args[index].lower()
        except IndexError:
            return ''

    def print(self, msg: str):
        """Print colored message in console."""
        COLORS = {
            'b': ('\x1b[34m\x1b[22m', '\x1b[39m\x1b[22m'),  # blue
            'g': ('\x1b[32m\x1b[22m', '\x1b[39m\x1b[22m'),  # green
            'r': ('\x1b[31m\x1b[22m', '\x1b[39m\x1b[22m'),  # red
            'y': ('\x1b[33m\x1b[22m', '\x1b[39m\x1b[22m'),  # yellow
        }

        for name, data in COLORS.items():
            msg = msg.replace(f'<{name}>', data[0])
            msg = msg.replace(f'</{name}>', data[1])

        print(msg)

    def print_results(self, results: Iterable, query=None):
        """Print iterable results with colored query match."""
        for value in results:
            if query:
                value = value.replace(query, f'<y>{query}</y>')
            self.print(f'  {value}')

    def print_namespaces_and_pods(
        self,
        results: list,
        namespace_query: str = None,
        pod_name_query: str = None,
    ):
        """Print namespace and pod pairs."""
        max_length = len(max(results, key=lambda x: len(x[0]))[0])
        heading_indent = ' ' * (max_length - 6)

        self.print(f'\n<g>Namespace</g>{heading_indent}<g>Pod name</g>\n')
        for namespace, pod_name, *other in results:
            line_indent = ' ' * (max_length - len(namespace) + 3)
            if namespace_query:
                namespace = namespace.replace(
                    namespace_query,
                    f'<y>{namespace_query}</y>',
                )
            if pod_name_query:
                pod_name = pod_name.replace(
                    pod_name_query,
                    f'<y>{pod_name_query}</y>',
                )
            self.print(f'{namespace}{line_indent}{pod_name}')

    def print_namespace_and_pod_name(self, namespace, pod_name):
        """Print single namespace and pod name."""
        self.print(
            f'\nNamespace:\t<g>{namespace}</g>'
            f'\nPod name:\t<g>{pod_name}</g>\n'
        )

    def select_from_multiple_results(
        self,
        results: Iterable,
        exact_match: Union[str, tuple],
        query: str = None,
        print_results: bool = True,
    ) -> Optional[str]:
        """Select match from iterable results."""
        if len(results) == 1:
            return results[0]
        elif exact_match in results:
            return exact_match
        elif print_results:
            self.print('\n<y>Found more than 1 result</y>\n')
            self.print_results(results, query)

    def get_output(self, command: str) -> list:
        """Get output from kubectl executed command."""
        try:
            output_bytes = subprocess.check_output(
                ['kubectl'] + command.split(' '),
                timeout=self.timeout,
            )
            return output_bytes.decode('utf-8').split('\n')
        except subprocess.TimeoutExpired:
            self.print('\n<r>Timeout on getting response from kubectl</r>')
            exit()

    def execute(self, command: str):
        """Execute kubectl command."""
        os.system(f'kubectl {command}')

    def request_data(self) -> list:
        """Request all pods with namespaces from kubectl."""
        output = self.get_output('get pods --all-namespaces')
        return [line.split() for line in output[1:-1]]

    def get_all_namespaces(self) -> list:
        """Get set of all namespaces."""
        return sorted({value[0] for value in self.request_data()})

    def get_all_pod_names(self) -> set:
        """Get set of all namespaces."""
        return sorted({value[1] for value in self.request_data()})

    def find_namespace_by_query(self, query: str) -> list:
        """Find namespace by query."""
        return self.find_by_query(
            query=query,
            data=self.get_all_namespaces(),
        )

    def find_pod_by_query(self, query: str) -> list:
        """Find pod by query."""
        return self.find_by_query(
            query=query,
            data=self.get_all_pod_names(),
        )

    def find_by_query(self, query: str, data: Iterable) -> list:
        """Find query in iterable data."""
        query = self.clear_str(query)
        return [value for value in data if query in self.clear_str(value)]

    def clear_str(self, value: str) -> str:
        """Clear any redundant symbols from value."""
        return value.lower().replace(' ', '').replace('-', '').replace('_', '')


def main():
    KubeCLI().run()
