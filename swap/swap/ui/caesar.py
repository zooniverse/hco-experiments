################################################################
"""
    An interface to interact with our utilities from the command line.
    Makes it easier to repeated run SWAP under different conditions.

    UI:
        Container for all the different interfaces

    Interface:
        A construct that manages options and determines the right action

    SWAPInterface:
        An interface for interacting with SWAP

    RocInterface:
        An interface to generate roc curves from multiple SWAP exports
"""

import swap.config as config
import swap.caesar.app as caesar
from swap.caesar.auth import AuthCaesar
from swap.ui.ui import Interface

import logging

logger = logging.getLogger(__name__)

class CaesarInterface(Interface):
    """
    Interface to launch the caesar app
    """

    def init(self):
        """
        Method called on init, after having registered with ui
        """
        pass

    @property
    def command(self):
        return 'caesar'

    def options(self, parser):
        parser.add_argument(
            '--load', nargs=1,
            help='NOT IMPLEMENTED Pre-load a swap instance from db')

        parser.add_argument(
            '--register', action='store_true',
            help='Register swap as an external extractor/reducer'
        )

        parser.add_argument(
            '--unregister', action='store_true',
            help='Clear swap registration from caesar'
        )

        parser.add_argument(
            '--run', action='store_true',
            help='Run the app')

        parser.add_argument(
            '--port', nargs=1,
            help='Modify the port used by the app')

        parser.add_argument(
            '--login', action='store_true'
        )

    def call(self, args):
        """
        Define what to do if this interface's command was passed
        """
        swap = None

        if args.port:
            config.online_swap.port = int(args.port[0])

        if args.load:
            swap = self.load(args.load[0])

        if args.login:
            AuthCaesar().login()

        if args.register:
            caesar.Requests.register_swap()
        elif args.unregister:
            caesar.Requests.unregister_swap()

        if args.run:
            self.run(swap)

    @staticmethod
    def run(swap=None):
        control = caesar.init_threader(swap)
        api = caesar.API(control)
        logger.info('launching flask app')
        api.run()
