"""Helper method for getting artifactory information."""
import logging

from .artifactory import Artifactory


def get_artifactory_info(repo_name=None, repo_type='local'):
    """Get storage info from Artifactory.

    Args:
        repo_name (tuple, optional): Name of artifactory repo.
        repo_type (str): Type of artifactory repo.

    Returns:
         keys (dict, optional): Dictionary of repo data.
         storage_info (dict): Storage information api call.
    """
    artifactory = Artifactory(repo_name=repo_name)
    storage_info = artifactory.list(repo_type=repo_type)

    if repo_name:
        keys = repo_name
    else:
        keys = storage_info.keys()

    logging.debug('Storage info: %s', storage_info)
    logging.debug('Keys: %s', keys)

    return storage_info, keys
