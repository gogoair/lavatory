"""Artifactory purger module."""
import base64
import datetime
import logging

import certifi
import party
import requests

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

    def list(self):
        """
        Return a dictionary of repos with basic info about each.

        Returns:
            repos (dict): Dictionary of repos.
        """
        repos = {}

        raw_data = self.artifactory.get('storageinfo')
        data = raw_data.json()
        LOG.debug('Storage info data: %s', data)
        for repo in data["repositoriesSummaryList"]:
            if repo["repoKey"] == "TOTAL":
                continue

            repos[repo["repoKey"]] = repo

        return repos

    def get_statistics(self):
        """Get statistics of a repo.
            Examples: lavatory stats --repo docker-local

        Returns:
            str.
        """
        storage = self.list()
        try:
            repo = storage[self.repo_name]
            LOG.info('Repo Name: %s.', repo.get('repoKey'))
            LOG.info('Repo Type: %s - %s.', repo.get('repoType'), repo.get('packageType'))
            LOG.info('Repo Used Space: %s - %s of total used space.', repo.get('usedSpace'), repo.get('percentage'))
            LOG.info('Repo Folders %s, Files %s. Total items count: %s.',
                     repo.get('foldersCount'), repo.get('filesCount'), repo.get('itemsCount'))
        except KeyError as error:
            LOG.error('Repo %s does not exist.', self.repo_name)
            return error

        return 'OK.'

    def purge(self, dry_run, artifacts):
        """ Purge artifacts from the specified repo.

        Args:
            dry_run (bool): Dry run mode True/False
            artifacts (list): Artifacts.

        Returns:
            purged (int): Count purged.
        """
        purged = 0
        mode = "DRYRUN" if dry_run else "LIVE"

        for artifact in artifacts:
            artifact_path = "{}/{}".format(artifact['path'], artifact['name'])
            LOG.info("  %s purge %s:%s", mode, self.repo_name, artifact_path)
            if dry_run:
                purged += 1
            else:
                try:
                    self.artifactory.delete(artifact_path)
                    purged += 1
                except requests.exceptions.BaseHTTPError as error:
                    LOG.error(str(error))

        return purged

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
            item_type (str): The itme type to search for (file/folder/any).

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

    def count_based_retention(self, retention_count=None, project_depth=2, artifact_depth=3, item_type='folder'):
        """Return all artifacts except the <count> most recent.

        Args:
            retention_count (int): Number of artifacts to keep.
            project_depth (int):  how far down the Artifactory folder hierarchy to look for projects.
            artifact_depth (int):  how far down the Artifactory folder hierarchy to look for specific artifacts.
            item_type (str): The item type to search for (file/folder/any).

        Returns:
            list: List of all artifacts to delete.
        """
        purgable_artifacts = []
        LOG.info("Searching for purgable artifacts with count based retention in %s.", self.repo_name)
        for project in self.filter(depth=project_depth):
            LOG.debug("Processing artifacts for project %s", project)
            path = "{}/{}".format(project["path"], project["name"])
            purgable_artifacts.extend(
                self.filter(
                    offset=retention_count,
                    item_type=item_type,
                    depth=artifact_depth,
                    terms=[{
                        "path": path
                    }],
                    sort={"$desc": ["created"]}))

        return sorted(purgable_artifacts, key=lambda k: k['path'])
