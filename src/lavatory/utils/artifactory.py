"""Artifactory purger module."""
import base64
import datetime
import logging

import certifi
import party
from requests.exceptions import (BaseHTTPError, ConnectionError, HTTPError, InvalidURL, RequestException)

from ..credentials import load_credentials

LOG = logging.getLogger(__name__)


class Artifactory(object):
    """Artifactory purger class."""

    def __init__(self, repo_name=None):
        self.repo_name = repo_name
        self.credentials = load_credentials()
        self.base_url = self.credentials['artifactory_url']
        self.artifactory = party.Party()
        if not self.base_url.endswith('/api'):
            self.api_url = '/'.join([self.base_url, 'api'])
        else:
            self.api_url = self.base_url
        self.artifactory.artifactory_url = self.api_url
        self.artifactory.username = self.credentials['artifactory_username']
        self.artifactory.password = base64.encodebytes(bytes(self.credentials['artifactory_password'], 'utf-8'))
        self.artifactory.certbundle = certifi.where()

    def repos(self, repo_type='local'):
        """
        Return a dictionary of repos with basic info about each.

        Args:
            repo_type (str): Type of repository to list. (local/virtual/cache/any)

        Returns:
            repos (dict): Dictionary of repos.
        """
        repos = {}

        raw_data = self.artifactory.get('storageinfo')
        data = raw_data.json()
        LOG.debug('Storage info data: %s', data)
        for repo in data["repositoriesSummaryList"]:
            if repo['repoKey'] == "TOTAL":
                continue
            if repo['repoType'].lower() != repo_type and repo_type != 'any':
                LOG.debug("Skipping repo %s, not of type %s", repo['repoKey'], repo_type)
                continue

            repos[repo['repoKey']] = repo

        return repos

    def purge(self, dry_run, artifacts):
        """ Purge artifacts from the specified repo.

        Args:
            dry_run (bool): Dry run mode True/False
            artifacts (list): Artifacts.

        Returns:
            purged (int): Count purged.
        """
        purged = 0
        mode = 'DRYRUN' if dry_run else 'LIVE'
        LOG.info('Running mode: %s', mode)

        for artifact in artifacts:
            artifact_path = '{}/{}/{}'.format(self.repo_name, artifact['path'], artifact['name'])
            LOG.info('%s purge %s', mode, artifact_path)
            full_artifact_url = '{}/{}'.format(self.base_url, artifact_path)
            if dry_run:
                purged += 1
            else:
                try:
                    self.artifactory.query_artifactory(full_artifact_url, query_type='delete')
                    purged += 1
                except (BaseHTTPError, HTTPError, InvalidURL, RequestException, ConnectionError) as error:
                    LOG.error(str(error))

        return purged

    def move_artifacts(self, artifacts=None, dest_repository=None):
        """Moves a list of artifacts to dest_repository.

        Args:
            artifacts (list): List of artifacts to move.
            dest_repository (str): The name of the destination repo.
        """
        base_endpoint = "move/{}".format(self.repo_name)
        dest_prefix = "?to=/{}".format(dest_repository)
        for artifact in artifacts:
            move_url = "{0}/{1}/{2}{3}/{1}/{2}".format(base_endpoint, artifact['path'], artifact['name'], dest_prefix)
            LOG.info("Moving %s to repository %s", artifact['name'], dest_repository)
            r = self.artifactory.post(move_url)
            if not r.ok:
                LOG.warning("error moving artifact %s: %s", artifact['name'], r.text)
        return True

    # pylint: disable-msg=too-many-arguments
    def filter(self, terms=None, depth=3, sort=None, offset=0, limit=0, fields=None, item_type="folder"):
        """Get a subset of artifacts from the specified repo.
        This looks at the project level, but actually need to iterate lower at project level

        This method does not use pagination. It assumes that this utility
        will be called on a repo sufficiently frequently that removing just
        the default n items will be enough.

        Args:
            terms (list): an array of jql snippets that will be ANDed together
            depth (int, optional): how far down the folder hierarchy to look
            fields (list): Fields
            sort (dict): How to sort Artifactory results
            offset (int): how many items from the beginning of the list should be skipped (optional)
            limit (int): the maximum number of entries to return (optional)
            item_type (str): The item type to search for (file/folder/any).

        Returns:
            list: List of artifacts returned from query
        """

        if sort is None:
            sort = {}
        if fields is None:
            fields = []
        if terms is None:
            terms = []

        terms.append({"path": {"$nmatch": "*/repodata"}})  # ignore all repodata. In future make configurable
        terms.append({"repo": {"$eq": self.repo_name}})
        terms.append({"type": {"$eq": item_type}})
        if depth:
            terms.append({"depth": {"$eq": depth}})

        aql = {"$and": terms}

        LOG.debug("AQL: %s", aql)
        response = self.artifactory.find_by_aql(
            fields=fields, criteria=aql, order_and_fields=sort, offset_records=offset, num_records=limit)

        results = response['results']

        return results

    def get_artifact_properties(self, artifact):
        """Given an artifact, queries for properties from artifact URL

        Args:
            artifact (dict): Dictionary of artifact info. Needs artifact['name'] and ['path'].

        Returns:
            dict: Dictionary of all properties on specific artifact
        """
        artifact_url = "{0}/{1}/{2}/{3}".format(self.base_url, self.repo_name, artifact['path'], artifact['name'])
        LOG.debug("Getting properties for %s", artifact_url)
        self.artifactory.get_properties(artifact_url)
        return self.artifactory.properties  # pylint: disable=no-member

    def get_all_repo_artifacts(self, depth=None, item_type='file', with_properties=True):
        """returns all artifacts in a repo with metadata

        Args:
            depth (int): How far down Artifactory folder to look. None will go to bottom of folder.
            item_type (str): The item type to search for (file/folder/any).
            with_properties (bool): Include artifact properties or not.

        Returns:
            list: Sorted list of all artifacts in a repository.
        """
        LOG.info("Searching for all artifacts in %s.", self.repo_name)
        if with_properties:
            fields = ['stat', 'property.*']
        else:
            fields = []
        artifacts = self.filter(item_type=item_type, depth=depth, fields=fields)
        return sorted(artifacts, key=lambda k: k['path'])

    def time_based_retention(self, keep_days=None, item_type='file', extra_aql=None):
        """Retains artifacts based on number of days since creation.

            extra_aql example: [{"@deployed": {"$match": "dev"}}, {"@deployed": {"$nmatch": "prod"}}]
            This would search for artifacts that were created after <keep_days> with
            property "deployed" equal to dev and not equal to prod.

        Args:
            keep_days (int): Number of days to keep an artifact.
            item_type (str): The item type to search for (file/folder/any).
            extra_aql (list). List of extra AQL terms to apply to search

        Return:
            list: List of artifacts matching retention policy
        """
        if extra_aql is None:
            extra_aql = []

        now = datetime.datetime.now()
        before = now - datetime.timedelta(days=keep_days)
        created_before = before.strftime("%Y-%m-%dT%H:%M:%SZ")
        aql_terms = [{"created": {"$lt": created_before}}]
        aql_terms.extend(extra_aql)
        purgable_artifacts = self.filter(item_type=item_type, depth=None, terms=aql_terms)
        return sorted(purgable_artifacts, key=lambda k: k['path'])

    def count_based_retention(self,
                              retention_count=None,
                              project_depth=2,
                              artifact_depth=3,
                              item_type='folder',
                              extra_aql=None):
        """Return all artifacts except the <count> most recent.

        Args:
            retention_count (int): Number of artifacts to keep.
            project_depth (int):  how far down the Artifactory folder hierarchy to look for projects.
            artifact_depth (int):  how far down the Artifactory folder hierarchy to look for specific artifacts.
            item_type (str): The item type to search for (file/folder/any).
            extra_aql (list). List of extra AQL terms to apply to search

        Returns:
            list: List of all artifacts to delete.
        """
        purgable_artifacts = []
        LOG.info("Searching for purgable artifacts with count based retention in %s.", self.repo_name)
        for project in self.filter(depth=project_depth):
            LOG.debug("Processing artifacts for project %s", project)
            if project['path'] == '.':
                path = "{}".format(project["name"])
            else:
                path = "{}/{}".format(project["path"], project["name"])
            terms = [{"path": path}]
            if extra_aql:
                terms += extra_aql
            purgable_artifacts.extend(
                self.filter(
                    offset=retention_count,
                    item_type=item_type,
                    depth=artifact_depth,
                    terms=terms,
                    sort={
                        "$desc": ["created"]
                    }))

        return sorted(purgable_artifacts, key=lambda k: k['path'])
