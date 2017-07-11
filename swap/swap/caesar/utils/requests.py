
import swap.config as config
from swap.caesar.utils.address import Address
from swap.caesar.auth import AuthCaesar

from functools import wraps
import json
import requests
import logging

logger = logging.getLogger(__name__)


def request_wrapper(func):
    @wraps(func)
    def wrapper(cls, *args, **kwargs):
        r = func(cls, *args, **kwargs)

        if r.status_code not in [200, 204, 203]:
            raise cls.BadResponse(r)
        return r
    return wrapper


class Requests:

    @classmethod
    @request_wrapper
    def register_swap(cls):
        """
        Register swap as an extractor/reducer on caesar
        """
        data = Address.config_caesar()
        address = Address.root()

        logger.info('PUT to %s with %s', address, str(data))
        auth_header = AuthCaesar().auth()
        print(auth_header)
        r = requests.put(address, headers=auth_header, json=data)

        if r.status_code != 200:
            print(r)
            logger.error(str(r.__dict__))
            raise cls.BadResponse('Received status code %d' % r.status_code)
        logger.info('done')

    @classmethod
    @request_wrapper
    def unregister_swap(cls):
        pass

    @classmethod
    @request_wrapper
    def respond(cls, subject):
        """
        PUT subject score to Caesar
        """
        c = config.online_swap

        address = Address.reducer()

        body = {
            'reduction': {
                'subject_id': subject.id,
                'data': {
                    c.caesar.field: subject.score
                }
            }
        }

        print('responding!')
        # address='http://httpbin.org/put'
        logger.info('PUT to %s subject %d score %.4f to caesar',
                    address, subject.id, subject.score)

        headers = cls.headers()
        headers.update(AuthCaesar().auth())
        r = requests.put(address, headers=headers, json=body)
        logger.debug('done')

        return r

    class BadResponse(Exception):
        def __init__(self, response, msg=None):
            try:
                data = json.loads(response.text)
            except json.decoder.JSONDecodeError:
                data = response.text
            logger.error('%s\n%s', str(response), data)

            super().__init__(msg)

    @staticmethod
    def headers():
        return {
            'Accept': 'application/json',
            'Content-Type': 'application/json'}
