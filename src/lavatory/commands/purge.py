import logging
import click 

from  ..lavatory import run_purge

LOG = logging.getLogger(__name__)

@click.command()
@click.pass_context
@click.option(
    '--dryrun/--nodryrun', default=True, is_flag=True, help='Dryrun does not delete any artifacts. On by default')
@click.option('--default/--no-default', default=True, is_flag=True, help='If false, does not apply default policy')
@click.option('--policies-path', required=False, help='Path to extra policies directory')
#@click.argument('url')
def purge(ctx, dryrun, policies_path, default):
    run_purge(dryrun, policies_path, default)
