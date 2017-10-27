import logging

import click
import coloredlogs

from .commands.purge import purge

LOG = logging.getLogger(__name__)


@click.group()
@click.option('-v', '--verbose', count=True, help='Increases logging level')
@click.pass_context
def root(ctx, verbose):
    """Lavatory CLI entry point"""
    coloredlogs.install(level=0, fmt='[%(levelname)s] %(name)s %(message)s', isatty=True)
    logging.root.setLevel(logging.INFO)  # coloredlogs likes to change root level
    verbosity = logging.root.getEffectiveLevel() - 10 * verbose or 1
    logging.getLogger(__package__).setLevel(verbosity)

    if verbosity < logging.DEBUG:
        logging.root.setLevel(verbosity)


root.add_command(purge)

if __name__ == '__main__':
    root()
