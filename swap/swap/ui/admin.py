
from swap.db import DB
from swap.ui.ui import Interface


class AdminInterface(Interface):
    """
    Interface that defines a set of options and operations.
    Designed to be subclassed and overriden
    """

    @property
    def command(self):
        """
        Command used to select parser.

        For example, this would return 'swap' for SWAPInterface
        and 'roc' for RocInterface
        """
        return 'admin'

    def options(self, parser):
        """
        Add options to the parser
        """

        parser.add_argument(
            '--upload-dump', nargs=1,
            help='Upload project dump to mongo database')

        parser.add_argument(
            '--gen-stats', action='store_true',
            help='Regenerate run stats for classifications in db'
        )

    def call(self, args):
        """
        Define what to do if this interface's command was passed
        """

        if args.upload_dump:
            fname = args.upload_dump[0]
            DB().classifications.upload_project_dump(fname)

        if args.gen_stats:
            DB().classifications._gen_stats()
