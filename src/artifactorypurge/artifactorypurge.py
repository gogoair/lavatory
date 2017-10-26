import click
import imp
from .utils.logging import getLogger
from .credentials import load_credentials

from .utils.artifactory import Artifactory
from .utils.performance import get_performance_report

LOG = getLogger(__name__)

@click.command()
@click.option('--dryrun/--nodryrun', default=True, is_flag=True, help='Dryrun does not delete any artifacts. On by default')
@click.option('--reponame', default=None, help='Operate on single repo')
@click.option('--project', default=None, help='Operate on single project')
#@click.argument('url')
def purge(dryrun, reponame, project): #, url):
    exceptions = {}

    credentials = load_credentials()
    artifactory = Artifactory(credentials['artifactory_url'], 
                              credentials['artifactory_username'],
                              credentials['artifactory_password'])

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
        except ImportError:
            continue
        finally:
            if fp:
                fp.close()

    LOG.info("")
    LOG.info("Purging Performance:")
    after = artifactory.list(reponame)
    for repo, info in after.items():
        try:
            get_performance_report(repo, before[repo], info)
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
