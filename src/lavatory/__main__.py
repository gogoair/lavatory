import logging
import pprint

import click
import coloredlogs
import pip

from .commands.purge import purge

LOG = logging.getLogger(__name__)


@click.group()
@click.option('-v', '--verbose', count=True, help='Increases logging level')
@click.pass_context
def root(ctx, verbose):
    """Lavatory is a tool for managing Artifactory Retention Policies."""
    coloredlogs.install(level=0, fmt='[%(levelname)s] %(name)s %(message)s', isatty=True)
    logging.root.setLevel(logging.INFO)  # coloredlogs likes to change root level
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


root.add_command(purge)

if __name__ == '__main__':
    root()