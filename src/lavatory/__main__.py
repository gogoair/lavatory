"""Main entry point."""
import logging
import pprint

import click
import coloredlogs
import pip

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
    for package_info in pip.commands.show.search_packages_info([__package__]):
        LOG.debug('Full package info: %s', pprint.pformat(package_info))

        name = package_info['name']
        if name != __package__:
            LOG.debug('This is not the package you are looking for: %s', name)
            continue

        click.echo(package_info['version'])
        break
    else:
        raise KeyError('Could not find {0}'.format(__package__))


root.add_command(policies)
root.add_command(purge)
root.add_command(stats)

if __name__ == '__main__':
    root()
