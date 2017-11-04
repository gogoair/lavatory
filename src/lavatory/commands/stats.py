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
    required=True,
    help='Name of specific repository to run statistics against.')
def stats(ctx, repo):
    LOG.debug('Passed args: %s, %s, %s, %s, %s,', ctx, repo)
    artifactory = Artifactory(repo_name=repo)

    statistics = artifactory.get_statistics()

    LOG.info('Done: %s', statistics)
