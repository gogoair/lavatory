"""Artifactory purger module."""
import base64
import datetime
import logging

import certifi
import party

from ..credentials import load_credentials

LOG = logging.getLogger(__name__)


class Artifactory(object):
    """Artifactory purger class."""
    def __init__(self, repo_name=None):
        self.repo_name = repo_name
        self.credentials = load_credentials()
        self.artifactory = party.Party()
        if not self.credentials['artifactory_url'].endswith('/api'):
            self.credentials['artifactory_url'] = '/'.join([self.credentials['artifactory_url'], 'api'])
        self.artifactory.artifactory_url = self.credentials['artifactory_url']
        self.artifactory.username = self.credentials['artifactory_username']
        self.artifactory.password = base64.encodebytes(bytes(self.credentials['artifactory_password'], 'utf-8'))
        self.artifactory.certbundle = certifi.where()

    @staticmethod
    def _parse_artifact_name(name):
        """Artifact name parser.

        Args:
            name (str): Long name.

        Returns:
            simple_name (str): Simple name.
        """
        simple_name = '/'.join(name.split('/')[-4:])
        return simple_name

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

    def all_artifacts(self, search='', depth=3):
        """ Returns a dict of artifact and properties.

        Args:
            search (str): Search regex.
            depth (int): Depth.

        Returns:
            all_artifacts (dict): All artifacts.
        """
        LOG.debug('Finding all artifacts with: search=%s, repo=%s, depth=%s', search, self.repo_name, depth)

        all_artifacts = self.artifactory.find_by_pattern(filename=search, specific_repo=self.repo_name, max_depth=depth)

        for artifact in sorted(all_artifacts):
            artifact_simple_name = self._parse_artifact_name(artifact)
            LOG.debug('Found: %s', artifact_simple_name)
            self.artifactory.get_properties(artifact)

        LOG.info('Found %d artifacts in total.', len(all_artifacts))
        return all_artifacts

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
            LOG.info("%s purge %s:%s", (mode, self.repo_name, artifact))
            if dry_run:
                purged += 1
            else:
                try:
                    self.artifactory.request(artifact, method='delete')
                    purged += 1
                except Exception as error:
                    LOG.error(str(error))

        return purged

    def filter(self, terms=None, depth=3):
        """Get a subset of artifacts from the specified repo.

        XXX: this looks at the project level, but actually need to iterate lower at project level
        XXX: almost certainly needs to set depth parameter to get to specific build

        Args:
            terms (list): AQL terms.
            depth (int): Depth level.

        Returns:
            results: Results from aql search.

        This method does not use pagination. It assumes that this utility
        will be called on a repo sufficiently frequently that removing just
        the default n items will be enough.
        """

        if terms is None:
            terms = []

        terms.append({"repo": {"$eq": self.repo_name}})
        terms.append({"type": {"$eq": "folder"}})
        terms.append({"depth": {"$eq": depth}})

        aql = {"$and": terms}

        LOG.debug("AQL: %s", aql)

        response = self.artifactory.find_by_aql(criteria=aql, fields=['stat'])

        results = response['results']

        return results

    def retain(self, spec_project, depth=3, terms=None, count=None, weeks=None):
        """Returns purgable artifacts.

        Args:
            spec_project: Spec_project
            depth (int): Depth level.
            terms: Terms for filter.
            count (int): Count.
            weeks: Number of weeks.

        Returns:
            purgable (list): Purgable.
        """
        if [terms, count, weeks].count(None) != 2:
            raise ValueError("Must specify exactly one of terms, count, or weeks")

        purgable = []

        for project in self.filter(depth=depth):
            if spec_project and spec_project != project["name"]:
                continue

            path = "{}/{}".format(project["path"], project["name"])
            if count:
                filtered = self.filter(depth=depth + 1, terms=[{"path": path}])

                for artifact in filtered:
                    purgable.append("{}/{}".format(artifact["path"], artifact["name"]))

            if weeks:
                now = datetime.datetime.now()
                before = now - datetime.timedelta(weeks=weeks)
                created = before.strftime("%Y-%m-%dT%H:%M:%SZ")
                filtered = self.filter(depth=depth + 1, terms=[{"path": path}, {"created": created}])
                for artifact in filtered:
                    purgable.append("{}/{}".format(artifact["path"], artifact["name"]))

            if terms:
                pass

        return purgable
