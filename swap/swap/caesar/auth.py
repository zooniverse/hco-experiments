
from swap.utils import Singleton
import swap.config as config

from panoptes_client.panoptes import Panoptes

from getpass import getpass
import logging
from flask import Response
import threading

logger = logging.getLogger(__name__)


class Auth:

    def __init__(self, username, token):
        self._username = username
        self._token = self._mod_token(token)

    @staticmethod
    def _mod_token(token):
        return token.replace(' ', '').replace('\n', '')

    def check_auth(self, username, token):
        return username == self._username and token == self._token

    @staticmethod
    def authenticate():
        """
        Sends a 401 response that enables basic auth
        """
        return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


class _AuthCaesar:

    def __init__(self):
        self.client = Panoptes(endpoint='https://panoptes-staging.zooniverse.org')
        self.lock = threading.Lock()

    @property
    def token(self):
        return self.client.get_bearer_token()

    def login(self):
        with self.lock:
            logger.info('Logging in to panoptes')
            user = input('Username: ')
            password = getpass()

            self.client.login(user, password)
            token = self.client.get_bearer_token()

        print(token)
        return token

    def auth(self, headers=None):
        logger.info('adding authorization header')
        with self.lock:
            if self.token is None:
                raise self.NotLoggedIn
            token = self.token

        if headers is None:
            headers = {}

        headers.update({
            'Authorization': 'Bearer %s' % token
        })

        return headers

    class NotLoggedIn(Exception):
        def __init__(self):
            super().__init__(
                'Need to log in first. Either set panoptes oauth2 bearer '
                'token in config.online_swap.caesar.OAUTH, or try running '
                'app again with --login flag')


class AuthCaesar(_AuthCaesar, metaclass=Singleton):
    pass
