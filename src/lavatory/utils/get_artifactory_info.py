"""Helper method for getting artifactory information."""
import logging

import requests

from .artifactory import Artifactory

LOG = logging.getLogger(__name__)


def _artifactory(artifactory=None, repo_names=None):
    if not artifactory:
        artifactory = Artifactory(repo_name=repo_names)
    return artifactory


def get_storage(repo_names=None, repo_type=None):
    artifactory = _artifactory(repo_names=repo_names)
    storage_info = []
    try:
        storage_info = artifactory.repos(repo_type=repo_type)
    except requests.exceptions.HTTPError:
        LOG.warning('Account is not an admin and may not be able to get storage details.')
    LOG.debug('Storage info: %s', storage_info)
    return storage_info


def get_repos(repo_names=None, repo_type='local'):
    repos = []
    if repo_names:
        repos = repo_names
    else:
        repos = get_storage(repo_names=repo_names, repo_type=repo_type)
    return repos


def get_artifactory_info(repo_names=None, repo_type='local'):
    """Get storage info from Artifactory.

    Args:
        repo_names (tuple, optional): Name of artifactory repo.
        repo_type (str): Type of artifactory repo.

    Returns:
         keys (dict, optional): Dictionary of repo data.
         storage_info (dict): Storage information api call.
    """
    artifactory = Artifactory(repo_name=repo_names)
    storage_info = artifactory.repos(repo_type=repo_type)

    if repo_names:
        keys = repo_names
    else:
        keys = storage_info.keys()

    LOG.debug('Storage info: %s', storage_info)
    LOG.debug('Keys: %s', keys)

    return storage_info, keys
