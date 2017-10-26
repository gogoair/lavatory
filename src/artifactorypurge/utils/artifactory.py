import datetime
import json
from ..utils.logging import getLogger
import requests


LOG = getLogger(__name__)


class _Http(object):

    def __init__(self, baseurl, user, passwd):
        self.baseurl = baseurl
        self.apiurl = baseurl + "/api"
        self.auth = (user, passwd)

    def get(self, endpoint):
        response = requests.get(self.apiurl+endpoint, auth=self.auth)

        if response.ok:
            return response.json()
        else:
            response.raise_for_status()

    def post(self, endpoint, payload):
        response = requests.post(self.apiurl+endpoint, auth=self.auth, data=payload)

        if response.ok:
            return response.json()
        else:
            response.raise_for_status()

    def delete(self, path):
        LOG.info("DELETE", path)
        return

        """
        response = requests.delete(baseurl + "/" + path)

        if response.ok:
            return response.json()
        else:
            response.raise_for_status()
            #raise Exception("HTTP DELETE {}: Server code {}".format(endpoint, response.status_code))
        """


class Artifactory(object):

    def __init__(self, baseurl, user, passwd):
        self.http = _Http(baseurl, user, passwd)

    def list(self, reponame=None):
        """
        Return a list of repos with basic info about each
        If the optional parameter reponame is specified, then only return
        information pertaining to that repo
        """
    
        repos = {}
    
        json = self.http.get("/storageinfo")
        for repo in json["repositoriesSummaryList"]:
            if repo["repoKey"] == "TOTAL" :
                continue
                
            if not reponame or reponame == repo["repoKey"]:
                repos[repo["repoKey"]] = repo
    
        return repos
    
    def purge(self, repo, dryrun, artifacts):
        """ Purge artifacts from the specified repo

        Keyword arguments:
        repo -- the repo to target for this operation
        dryrun -- false to execute an actual purge
        artifacts -- a list of artifacts to operate upon
        """

        purged = 0
        mode = "DRYRUN" if dryrun else "LIVE"

        for artifact in artifacts:
            LOG.info("  {} purge {}:{}".format(mode, repo, artifact))
            if dryrun:
                purged += 1
            else:
                try:
                    self.http.delete(artifact)
                    purged += 1
                except Exception as e:
                    LOG.error(str(e))

        return purged

    def filter(self, repo, terms=[], depth=3, sort=None, offset=None, limit=None):
        """Get a subset of artifacts from the specified repo.

        XXX: this looks at the project level, but actually need to iterate lower at project level
        XXX: almost certainly needs to set depth parameter to get to specific build

        Keyword arguments:
        repo -- the repo to target for this operation
        terms -- an array of jql snippets that will be ANDed together
        depth -- how far down the folder hierarchy to look
        offset -- how many items from the beginning of the list should be skipped (optional)
        limit -- the maximum number of entries to return (optional)

        This method does not use pagination. It assumes that this utility
        will be called on a repo sufficiently frequently that removing just
        the default n items will be enough.
        """

        terms.append({"repo": {"$eq": repo}})
        terms.append({"type": {"$eq": "folder"}})
        terms.append({"depth": {"$eq": depth}})

        findexpr = json.dumps({"$and": terms})
    
        aql = "items.find({})".format(findexpr)
    
        if sort:
            aql += ".sort({})".format(json.dumps(sort))
    
        if offset:
            aql += ".offset({})".format(offset)
    
        if limit:
            aql += ".limit({})".format(limit)
    
        LOG.debug("AQL: {}".format(aql))
    
        response = self.http.post("/search/aql", aql)

        return response["results"]
    
    def retain(self, repo, specproject, depth, terms=None, count=None, weeks=None):
        if [terms, count, weeks].count(None) != 2:
            raise ValueError("Must specify exactly one of terms, count, or weeks")

        if weeks:
            now = datetime.datetime.now()
            before = now - datetime.timedelta(weeks=weeks)
            created = before.strftime("%Y-%m-%dT%H:%M:%SZ")

        purgable = []

        for project in self.filter(repo, depth=depth):
            if specproject and specproject!=project["name"]:
                continue

            path = "{}/{}".format(project["path"], project["name"])
            if count:
                for artifact in self.filter(repo, offset=count, depth=depth+1, terms=[{"path": path}], sort={"$desc": ["created"]}):
                    purgable.append("{}/{}".format(artifact["path"], artifact["name"]))

            if weeks:
                for artifact in self.filter(repo, offset=count, depth=depth+1, terms=[{"path": path}, {"created": created}]):
                    purgable.append("{}/{}".format(artifact["path"], artifact["name"]))

            if terms:
                pass

        return purgable
