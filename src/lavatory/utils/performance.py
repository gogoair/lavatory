"""Performance comparison"""
import logging

from humanfriendly import format_number, format_size, parse_size

LOG = logging.getLogger(__name__)


def get_performance_report(repo_name, old_info, new_info):
    """compares retention policy performance, showing old amount of space and new.

    Args:
        repo_name (str): Name of repository
        old_info (dict): Metadata of repository before run
        new_info (dict): Metadata of repository after run
    """
    old_space = _get_human_friendly_used_space(old_info)
    new_space = _get_human_friendly_used_space(new_info)
    old_files = old_info["filesCount"]
    new_files = new_info["filesCount"]

    LOG.info("%s size: %s; reduction: storage %s (%.1f%%), files %s (%.1f%%)", repo_name,
             format_size(new_space),
             format_size(new_space - old_space),
             get_percentage(old_space, new_space),
             format_number(new_files - old_files), get_percentage(old_files, new_files))


def _get_human_friendly_used_space(info):
    return parse_size(info['usedSpace'].replace(',', ''))


def get_percentage(old, new):
    """Gets percentage from old and new values

    Args:
        old (num): old value
        new (num): new value
    Returns:
        number: Percentage, or zero if none
    """
    try:
        return 100 * (old - new) / old
    except ZeroDivisionError:
        return 0
