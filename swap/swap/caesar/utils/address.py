
import swap.config as config
from swap.caesar.auth import Auth

import logging

logger = logging.getLogger(__name__)


class Address:
    config = config.online_swap

    @classmethod
    def root(cls):
        host = cls.config.caesar.host
        port = cls.config.caesar.port
        workflow = cls.config.workflow
        return cls.config.address._base % \
            {'host': host, 'port': port, 'workflow': workflow}

    @classmethod
    def reducer(cls):
        reducer = cls.config.caesar.reducer
        addr = cls.config.address._reducer
        return cls.root() + addr % {'reducer': reducer}

    @classmethod
    def swap_classify(cls):
        addr = cls.config.address._swap
        host = cls.config.host
        port = cls.config.ext_port

        username = cls.config._auth_username
        password = cls.config._auth_key
        password = Auth._mod_token(password)

        return addr % \
            {'user': username, 'pass': password,
             'host': host, 'port': port}
