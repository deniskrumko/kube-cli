import os
import subprocess
import sys
from typing import Iterable


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
            return self.show_all_pods_or_namespaces()

        # kube find ns <...>
        # kube find pod <...>
        if self.args[0] == 'find':
            return self.find_pod_or_namespace()

        # kube <namespace>
        # kube <namespace> pods
        if len(self.args) == 1 or self.args[1] == 'pods':
            return self.show_pods_in_namespace()

        # kube <namespace> <pod> logs
        # kube <namespace> <pod> bash
        return self.run_pod_commands()

    def show_all_pods_or_namespaces(self):
        """Show all pods or namespaces."""
        try:
            param = self.args[1].lower()
        except IndexError:
            param = ''

        if param in ('ns', 'namespaces'):
            return self.show_all_namespaces()
        elif 'pod' in param:
            return self.show_all_pods()

        # Help for command
        self.print('\nkube all <g>ns</g>\t-- List of all namespaces')
        self.print('kube all <g>pods</g>\t-- List of all pods')

    def show_all_namespaces(self):
        """Show all existing namespaces."""
        namespaces = set()
        for pod in self.get_all_pods():
            namespaces.add(pod[0])

        self.print('\n<g>All available namespaces</g>\n')
        print('\n'.join(f'  {name}' for name in sorted(namespaces)))
        self.print(f'\n<g>Found {len(namespaces)} namespaces</g>')

    def show_all_pods(self, initial_pods=None):
        """Show all existing pods."""
        self.show_pods(pods=self.get_all_pods())

    def show_pods(self, pods: list):
        """Show list of passed pods data."""
        namespaces = []
        names = []
        for pod in pods:
            namespaces.append(pod[0])
            names.append(pod[1])

        max_length = len(max(namespaces, key=len))
        indent = ' ' * (max_length + 1)

        self.print(f'\n<g>Pod</g>{indent}<g>Namespace</g>\n')
        for i in range(len(namespaces)):
            name, namespace = names[i], namespaces[i]
            spaces = ' ' * (max_length - len(namespace) + 4)
            print(f'{namespace}{spaces}{name}')

    def show_pods_in_namespace(self):
        """Show all pods in single namespace."""
        pattern = self.args[0].lower()
        results = sorted(self.find_pattern_in_data(
            pattern=pattern,
            data={value[0] for value in self.get_all_pods()},
        ))
        if results:
            if len(results) == 1:
                # If one result
                namespace = results[0]
            elif self.args[0] in results:
                # If there is exact match in results
                namespace = self.args[0]
            else:
                # If there are many matches
                self.print(
                    '\n<y>Found more than 1 namespace with pattern '
                    f'"{pattern}"</y>\n'
                )
                for result in results:
                    print(f'  {result}')
                return

            output = self.get_output(f'get pods --namespace={namespace}')
            data = output[1:-1]
            self.print(f'\n<g>Available pods in namespace "{namespace}"</g>\n')
            for line in data:
                pod = line.split()[0]
                print(f'  {pod}')
        else:
            self.print(f'\n<r>No namespace matched pattern "{pattern}"</r>')

    def find_pod_or_namespace(self):
        """Find pos or namespace."""
        try:
            param = self.args[1].lower()
        except IndexError:
            param = ''

        if param in ('ns', 'namespace'):
            return self.find_namespace()
        elif 'pod' in param:
            return self.find_pod()

        # Help for command
        self.print('\nkube find <g>ns</g> <b><pattern></b>\t-- Find namespace')
        self.print('kube find <g>pod</g> <b><pattern></b>\t-- Find pod')

    def find_namespace(self):
        """Find namespace by pattern."""
        try:
            pattern = self.args[2].lower()
        except IndexError:
            pattern = ''

        if pattern:
            results = sorted(self.find_pattern_in_data(
                pattern=pattern,
                data={value[0] for value in self.get_all_pods()},
            ))
            if results:
                self.print('\n<g>Found namespaces</g>\n')
                self.print('\n'.join(
                    f'  {value.replace(pattern, f"<y>{pattern}</y>")}'
                    for value in results
                ))
            else:
                self.print(
                    f'\n<r>No namespace matched pattern "{pattern}"</r>'
                )
            return

        # Help for command
        self.print('\nkube find ns <g><pattern></g>\t-- Find namespace')

    def find_pod(self):
        """Find pod by pattern."""
        try:
            pattern = self.args[2].lower()
        except IndexError:
            pattern = ''

        if pattern:
            results = sorted(self.find_pattern_in_data(
                pattern=pattern,
                data={value[1] for value in self.get_all_pods()},
            ))
            if results:
                self.print('\n<g>Found pods</g>\n')
                # TODO: Show namespace too
                self.print('\n'.join(
                    f'  {value.replace(pattern, f"<y>{pattern}</y>")}'
                    for value in results
                ))
            else:
                self.print(
                    f'\n<r>No pods matched pattern "{pattern}"</r>'
                )
            return

        # Help for command
        self.print('\nkube find pod <g><pattern></g>\t-- Find pod')

    def run_pod_commands(self):
        """Run pod commands."""
        if len(self.args) == 3:
            namespace = self.args[0].lower()
            pod_name = self.args[1].lower()
            command = self.args[2].lower()

            results = []
            clean_ns = self.clear_str(namespace)
            clean_pod = self.clear_str(pod_name)
            for line in self.get_all_pods():
                val0, val1 = self.clear_str(line[0]), self.clear_str(line[1])
                if clean_ns in val0 and clean_pod in val1:
                    results.append((line[0], line[1]))

            if len(results) == 1:
                # If one result
                namespace, pod_name = results[0]
            elif (self.args[0], self.args[1]) in results:
                # If there is exact match in results
                namespace, pod_name = self.args[0], self.args[1]
            elif results:
                # If there are many matches
                self.print('\n<y>Found more than namespace/pod</y>')
                for namespace, pod in results:
                    # TODO: Fix display
                    print(f'{namespace}\t\t{pod}')
                return
            else:
                self.print('\n<r>Cannot find namespace and pod</r>')
                return

            if command == 'logs':
                return self.stream_pod_logs(namespace, pod_name)
            if command == 'bash':
                return self.run_bash_in_pod(namespace, pod_name)

        self.print(
            '\nkube <b><namespace></b> <b><pod></b> <g>logs</g>\t'
            '-- Stream logs from pod'
        )
        self.print(
            'kube <b><namespace></b> <b><pod></b> <g>bash</g>\t'
            '-- Run bash in pod'
        )

    def stream_pod_logs(self, namespace, pod_name):
        """Stream logs from pod."""
        self.print(
            f'\nNamespace:\t<g>{namespace}</g>\nPod name:\t<g>{pod_name}</g>\n'
        )
        input('Press enter to start streaming logs\n')
        self.run_command(f'logs --namespace={namespace} -f {pod_name}')

    def run_bash_in_pod(self, namespace, pod_name):
        """Run bash in pod."""
        self.print(
            f'\nNamespace:\t<g>{namespace}</g>\nPod name:\t<g>{pod_name}</g>\n'
        )
        self.run_command(
            f'exec -it --namespace={namespace} {pod_name} -- bash'
        )

    def show_help(self):
        """Show help for program."""
        help_text = '''
<g>kube</g> is a CLI for Kubernetes that simplifies usage of kubectl

  Find more information at: https://github.com/deniskrumko/kube-cli

<g>Basic Commands</g>

  kube <g>all ns</g>\t\t\t\tList of all namespaces
  kube <g>all pods</g>\t\t\t\tList of all pods in all namespaces
  kube <g>find ns</g> <b><pattern></b>\t\tFind namespace
  kube <g>find pod</g> <b><pattern></b>\t\tFind pod
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
        self.print(help_text)

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

    def run_command(self, command: str) -> list:
        """Run kubectl command."""
        os.system(f'kubectl {command}')

    def get_all_pods(self) -> list:
        """Get list of all pods."""
        output = self.get_output('get pods --all-namespaces')
        return [line.split() for line in output[1:-1]]

    def find_pattern_in_data(self, pattern: str, data: Iterable):
        """Find pattern in iterable data."""
        pattern = self.clear_str(pattern)
        for value in data:
            if pattern in self.clear_str(value):
                yield value

    def clear_str(self, value: str) -> str:
        """Clear any redundant symbols from value."""
        return value.lower().replace(' ', '').replace('-', '').replace('_', '')


def main():
    KubeCLI().run()
