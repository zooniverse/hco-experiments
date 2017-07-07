
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
            help='Upload panoptes project dump to mongo database')

        parser.add_argument(
            '--upload-golds', nargs=1,
            help='Upload gold data from csv with subject id and gold label. '
                 'Doesn\'t need every subject, only the ones with a gold label')

        parser.add_argument(
            '--gen-stats', action='store_true',
            help='Force regeneration of classification stats in db for swap'
        )

    def call(self, args):
        """
        Define what to do if this interface's command was passed
        """

        if args.upload_dump:
            fname = args.upload_dump[0]
            DB().classifications.upload_project_dump(fname)

        if args.upload_golds:
            fname = args.upload_golds[0]
            DB().golds.upload_golds_csv(fname)

        if args.gen_stats:
            DB().classifications._gen_stats()
