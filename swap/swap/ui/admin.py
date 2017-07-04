
import swap.db.classifications as dbcl
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

    def call(self, args):
        """
        Define what to do if this interface's command was passed
        """

        if args.upload_dump:
            fname = args.upload_dump[0]
            dbcl.upload_project_dump(fname)
