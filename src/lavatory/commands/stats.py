"""Statistics of the repo."""
import logging

import click

from ..utils.get_artifactory_info import get_artifactory_info

LOG = logging.getLogger(__name__)


@click.command()
@click.pass_context
@click.option(
    '--repo',
    default=None,
    multiple=True,
    required=False,
    help='Name of specific repository to run against. Can use --repo multiple times. If not provided, uses all repos.')
def stats(ctx, repo):
    """Get statistics of repos."""
    LOG.debug('Passed args: %s, %s.', ctx, repo)
    storage, keys = get_artifactory_info(repo_names=repo, repo_type='any')

    for repository in keys:
        repo = storage.get(repository)
        if repo is None:
            LOG.error('Repo name %s does not exist.', repository)
            continue

        LOG.info('Repo Name: %s.', repo.get('repoKey'))
        LOG.info('Repo Type: %s - %s.', repo.get('repoType'), repo.get('packageType'))
        LOG.info('Repo Used Space: %s - %s of total used space.', repo.get('usedSpace'), repo.get('percentage'))
        LOG.info('Repo Folders %s, Files %s. Total items count: %s.',
                 repo.get('foldersCount'), repo.get('filesCount'), repo.get('itemsCount'))
        LOG.info('-' * 25)

    click.echo('Done.')
