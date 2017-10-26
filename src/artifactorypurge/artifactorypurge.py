import os

import click
from pluginbase import PluginBase

from .credentials import load_credentials
from .utils.artifactory import Artifactory
from .utils.logging import getLogger
from .utils.performance import get_performance_report

LOG = getLogger(__name__)


@click.command()
@click.option(
    '--dryrun/--nodryrun', default=True, is_flag=True, help='Dryrun does not delete any artifacts. On by default')
@click.option('--plugin-path', required=True, help='Path to plugin directory')
@click.option('--default/--no-default', default=True, is_flag=True, help='If false, does not apply default policy')
#@click.argument('url')
def purge(dryrun, plugin_path, default):  #, url):
    credentials = load_credentials()
    artifactory = Artifactory(credentials['artifactory_url'], credentials['artifactory_username'],
                              credentials['artifactory_password'])

    plugin_source = setup_pluginbase(plugin_path)
    before = artifactory.list(None)
    for repo, info in before.items():
        plugin_name = repo.replace("-", "_")
        try:
            artifactory_plugin = plugin_source.load_plugin(plugin_name)
        except ModuleNotFoundError:
            if default:
                LOG.info("No plugin found for %s. Applying Default", repo)
                artifactory_plugin = plugin_source.load_plugin('default')
            else:
                LOG.info("No plugin found for %s. Skipping Default", repo)
                continue
        artifacts = artifactory_plugin.purgelist(
            artifactory,
            repo,
            None,
        )
        count = artifactory.purge(repo, dryrun, artifacts)
        LOG.info("processed {}, purged {}".format(repo, count))

    LOG.info("")
    LOG.info("Purging Performance:")
    after = artifactory.list(None)
    for repo, info in after.items():
        try:
            get_performance_report(repo, before[repo], info)
        except IndexError:
            pass

    LOG.info("Done.")

    exit(0)


def setup_pluginbase(plugin_path):
    """Sets up plugin base with default path and provided path
    
    Args:
        plugin_path (str): Extra path to find plugins in

    Returns:
        PluginSource: PluginBase PluginSource for finding plugins
    """
    here = os.path.dirname(os.path.realpath(__file__))
    default_path = "{}/plugins".format(here)
    LOG.info("Searching for plugins in %s and %s", plugin_path, default_path)
    plugin_base = PluginBase(package='artifactorypurge.plugins')
    plugin_source = plugin_base.make_plugin_source(searchpath=[plugin_path, default_path])
    return plugin_source


if __name__ == "__main__":
    purge()
