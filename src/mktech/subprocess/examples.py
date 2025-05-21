import click

from mktech import subprocess

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(
    context_settings=CONTEXT_SETTINGS,
    no_args_is_help=True,
)
@click.argument('command')
def run_in_subprocess(command: str) -> None:
    """
    Run COMMAND and print its exit code.

    COMMAND have arguments and be interactive.
    """

    result = subprocess.run(command)

    print(f'command: "{command}", exit code: {result.exit_code}')


if __name__ == '__main__':
    run_in_subprocess()
