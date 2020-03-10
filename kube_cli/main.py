import sys


class KubeCLI:

    def __init__(self):
        """Initialize class instance."""
        self.args = sys.argv[1:]

    def run(self):
        pass


if __name__ in ('kube_cli.main', '__main__'):
    KubeCLI().run()
