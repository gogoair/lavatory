"""Helper method for getting artifactory information."""
import logging

from .artifactory import Artifactory


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

    logging.debug('Storage info: %s', storage_info)
    logging.debug('Keys: %s', keys)

    return storage_info, keys
