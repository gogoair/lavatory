import logging
import os

from pluginbase import PluginBase

from ..exceptions import InvalidPoliciesDirectory

LOG = logging.getLogger(__name__)


def setup_pluginbase(extra_policies_path=None):
    """Sets up plugin base with default path and provided path

    Args:
        extra_policies_path (str): Extra path to find plugins in

    Returns:
        PluginSource: PluginBase PluginSource for finding plugins
    """
    here = os.path.dirname(os.path.realpath(__file__))
    default_path = "{}/../policies".format(here)
    all_paths = [default_path]
    if extra_policies_path:
        if not os.path.isdir(extra_policies_path):
            raise InvalidPoliciesDirectory
        all_paths.append(extra_policies_path)
    LOG.info("Searching for policies in %s", str(all_paths))
    plugin_base = PluginBase(package='lavatory.policy_plugins')
    plugin_source = plugin_base.make_plugin_source(searchpath=all_paths)
    LOG.debug("Policies found: %s", str(plugin_source.list_plugins()))
    return plugin_source
