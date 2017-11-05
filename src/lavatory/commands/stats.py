"""Statistics of the repo."""
import logging

import click

from ..utils.artifactory import Artifactory

LOG = logging.getLogger(__name__)


@click.command()
@click.pass_context
@click.option(
    '--repo',
    default=None,
    required=False,
    help='Name of specific repository to run against. If not provided, uses all repos.')
def stats(ctx, repo):
    """Get statistics of a repo."""
    LOG.debug('Passed args: %s, %s.', ctx, repo)
    artifactory = Artifactory(repo_name=repo)
    statistics = artifactory.get_statistics()

    click.echo('Done, return output: {}.'.format(statistics))
