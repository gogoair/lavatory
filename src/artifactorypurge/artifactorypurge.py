import click
from humanfriendly import parse_size, format_number, format_size
import imp
from .utils.logging import getLogger
from .credentials import CREDENTIALS

from utils.artifactory import Artifactory

LOG = getLogger(__name__)

def _performance(name, old, new):
    oldSpace = parse_size(old["usedSpace"])
    newSpace = parse_size(new["usedSpace"])

    oldFiles = old["filesCount"]
    newFiles = new["filesCount"]

    return "  {} size: {}; reduction: storage {} ({}%), files {} ({}%)".format(
            name, format_size(newSpace),
            format_size(newSpace-oldSpace), (100*(oldSpace-newSpace))/oldSpace,
            format_number(newFiles-oldFiles), (100*(oldFiles-newFiles))/oldFiles
            )


@click.command()
@click.option('--dryrun/--nodryrun', default=True, is_flag=True, help='Dryrun does not delete any artifacts. On by default')
@click.option('--reponame', default=None, help='Operate on single repo')
@click.option('--project', default=None, help='Operate on single project')
#@click.argument('url')
def purge(dryrun, reponame, project): #, url):
    exceptions = {}

    artifactory = Artifactory(CREDENTIALS['artifactory_url'], 
                              CREDENTIALS['artifactory_username'],
                              CREDENTIALS['artifactory_password'])

    before = artifactory.list(reponame)
    for repo, info in before.items():
        fp = 0
        try:
            modulename = repo.replace("-", "_")
            fp, pathname, description = imp.find_module(modulename, ["repositories",])
            module =  imp.load_module(modulename, fp, pathname, description)
            artifacts = module.purgelist(artifactory, repo, project)
            count = artifactory.purge(repo, dryrun, artifacts)
            LOG.info("processed {}, purged {}".format(repo, count))
        except IndexError as e:  # FIXME: return to generic catch
            exceptions[repo] = str(e)
        finally:
            if fp:
                fp.close()

    LOG.info("")
    LOG.info("Purging Performance:")
    after = artifactory.list(reponame)
    for repo, info in after.items():
        try:
            LOG.info(_performance(repo, before[repo], info))
        except IndexError:
            pass

    if len(exceptions):
        LOG.error("There were errors:")
        for repo, exception in exceptions.items():
            LOG.error("  {}: {}".format(repo, exception))

        exit(1)

    LOG.info("Done.")

    exit(0)


if __name__ == "__main__":
    purge()
