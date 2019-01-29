"""Main entry point."""
import logging

import click
import coloredlogs

from .commands.policies import policies
from .commands.purge import purge
from .commands.stats import stats

LOG = logging.getLogger(__name__)


@click.group()
@click.option('-v', '--verbose', count=True, help='Increases logging level.')
@click.pass_context
def root(ctx, verbose):
    """Lavatory is a tool for managing Artifactory Retention Policies."""
    LOG.debug('Passed args: %s, %s', ctx, verbose)
    coloredlogs.install(level=0, fmt='[%(levelname)s] %(name)s %(message)s', isatty=True)
    logging.root.setLevel(logging.INFO)  # colored logs likes to change root level
    verbosity = logging.root.getEffectiveLevel() - 10 * verbose or 1
    logging.getLogger(__package__).setLevel(verbosity)

    if verbosity < logging.DEBUG:
        logging.root.setLevel(verbosity)


@root.command()
def version():
    """Print version information."""
    import pkg_resources
    lavatory_version = pkg_resources.get_distribution('lavatory').version
    click.echo(lavatory_version)


root.add_command(policies)
root.add_command(purge)
root.add_command(stats)

if __name__ == '__main__':
    # pylint: disable=no-value-for-parameter
    root()
