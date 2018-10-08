import logging
import os
import pathlib

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
    here = pathlib.Path(__file__).parent.absolute()
    default_path_obj = here / "../policies"
    default_path = str(default_path_obj.resolve())

    all_paths = [default_path]
    if extra_policies_path:
        extra_policies_obj = pathlib.Path(extra_policies_path)
        if extra_policies_obj.is_dir():
            extra_policies = get_directory_path(extra_policies_obj)
            all_paths.insert(0, str(extra_policies))
        else:
            raise InvalidPoliciesDirectory
    LOG.info("Searching for policies in %s", str(all_paths))
    plugin_base = PluginBase(package='lavatory.policy_plugins')
    plugin_source = plugin_base.make_plugin_source(searchpath=all_paths)
    LOG.debug("Policies found: %s", str(plugin_source.list_plugins()))
    return plugin_source


def get_policy(plugin_source, repository, default=True):
    """Gets policy from plugin_source.

    Args:
        plugin_source (PluginBase): the plugin source from loading plugin_base.
        repository (string): Name of repository.
        default (bool): If to load the default policy.

    Returns:
        policy (func): The policy python module.
    """
    policy_name = repository.replace("-", "_")
    try:
        policy = plugin_source.load_plugin(policy_name)
    except ImportError:
        if default:
            LOG.info("No policy found for %s. Applying Default", repository)
            policy = plugin_source.load_plugin('default')
        else:
            LOG.info("No policy found for %s. Skipping Default", repository)
            policy = None
    return policy


def get_directory_path(directory):
    """Gets policy from plugin_source.

    Args:
        directory (Path): Directory path

    Returns:
        full_path (Path): The full expanded directory path
    """
    full_path = ''
    if hasattr(directory, 'expanduser'):
        full_path = directory.expanduser().resolve()
    else:
        full_path = pathlib.Path(os.path.expanduser(directory)).resolve()
    return full_path
