import click
from pluginbase import PluginBase
from .utils.logging import getLogger
from .credentials import load_credentials

from .utils.artifactory import Artifactory
from .utils.performance import get_performance_report

LOG = getLogger(__name__)

@click.command()
@click.option('--dryrun/--nodryrun', default=True, is_flag=True, help='Dryrun does not delete any artifacts. On by default')
@click.option('--plugin-path', required=True, help='Path to plugin directory')
#@click.argument('url')
def purge(dryrun, plugin_path): #, url):
    exceptions = {}

    credentials = load_credentials()
    artifactory = Artifactory(credentials['artifactory_url'], 
                              credentials['artifactory_username'],
                              credentials['artifactory_password'])

    plugin_source = setup_pluginbase(plugin_path)
    before = artifactory.list(None)
    for repo, info in before.items():
        fp = 0
        try:
            plugin_name = repo.replace("-", "_")
            try:
                artifactory_plugin = plugin_source.load_plugin(plugin_name)
            except ModuleNotFoundError:
                LOG.info("Not plugin found for %s. Applying Default", repo)
                artifactory_plugin = plugin_source.load_plugin('default')
            #fp, pathname, description = imp.find_module(modulename, ["repositories",])
            #module =  imp.load_module(modulename, fp, pathname, description)
            artifacts = artifactory_plugin.purgelist(artifactory, repo, None,)
            count = artifactory.purge(repo, dryrun, artifacts)
            LOG.info("processed {}, purged {}".format(repo, count))
        except IndexError as e:  # FIXME: return to generic catch
            exceptions[repo] = str(e)
        finally:
            if fp:
                fp.close()

    LOG.info("")
    LOG.info("Purging Performance:")
    after = artifactory.list(None)
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

def setup_pluginbase(plugin_path):
    plugin_base = PluginBase(package='artifactorypurge.plugins')
    plugin_source = plugin_base.make_plugin_source(searchpath=[plugin_path])
    return plugin_source


if __name__ == "__main__":
    purge()
