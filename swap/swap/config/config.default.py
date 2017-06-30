
# Place config overrides that should not propagate to the git repo in this file


def override(config):
    # True: static swap, False: dynamic swap
    config.back_update = True

    # Prior probability
    # config.p0 = 0.12

    # config.mdr = 0.1

    # Parse data types in csv dump
    # config.database.builder.types = {
    #     'object_id': int,
    #     'machine_score': float,
    #     'mag': float,
    #     'mag_err': float
    # }

    # Metadata in csv dump
    # config.database.builder.metadata = [
    #     'mag',
    #     'mag_err',
    #     'machine_score',
    #     'diff',
    #     'object_id'] + [
    #     'random%d' % (i + 1) for i in range(15)]

    # Database configuration
    # config.database.name = 'swapDB'
    # config.database.host = 'localhost'
    # config.database.port = 27017

    ##################################################
    # Online SWAP configuration

    # Interface and port for SWAP to listen on
    # config.online_swap.port = 5000
    # config.online_swap.bind = '0.0.0.0'

    # Workflow ID for incoming classifications
    # config.online_swap.workflow = 1737

    # Address to send response to
    # config.online_swap.response.host = '10.10.10.10'
    # config.online_swap.response.port = 3000

    # Response AUTH token
    # config.online_swap.response.token = ''

    # Name of reducer registered in Caesar
    # config.online_swap.response.reducer = 'swap'
    # Name of variable in Caesar
    # config.online_swap.response.field = 'swap_score'

    return None
