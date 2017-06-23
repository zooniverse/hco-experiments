import logging
import os

import swap.config as config
import swap


# def get_path(file):
#     # Get log path
#     path = os.path.dirname(os.path.abspath(file))
#     path = os.path.join(path, '../logs')
#     path = os.path.abspath(path)

#     # Ensure log path exists
#     if not os.path.exists(path):
#         os.makedirs(path)

#     return path

def get_path():

    # Get log path
    path = os.path.dirname(os.path.abspath(swap.__file__))
    path = os.path.join(path, '../logs')
    path = os.path.abspath(path)

    # Ensure log path exists
    if not os.path.exists(path):
        os.makedirs(path)

    return path


# def get_logger(name):
#     return logging.getLogger('hco.%s' % name)


def init():
    # logging.setLoggerClass(MyLogger)

    # pylint: disable=E1101
    # global log level
    level = config.logging.level
    # stdout log level
    console_level = config.logging.console_level
    # filename structure for log output
    fname = config.logging.filename
    # file log output format
    f_format = config.logging.file_format
    # console log output format
    c_format = config.logging.console_format
    # format for date
    date_format = config.logging.date_format
    # pylint: enable=E1101

    # Set appropriate log level
    for i in range(0, 51, 10):
        if level == logging.getLevelName(i):
            level = i
            break

    for i in range(0, 51, 10):
        if console_level == logging.getLevelName(i):
            console_level = i
            break

    handlers = []
    # Ensure each process has its own unique log file
    # to prevent file write conflicts
    # TODO implement global log server with unique uuid per process
    fname = fname % os.getppid()
    # Create file handler
    fname = os.path.join(get_path(), fname)
    handler = logging.FileHandler(fname)

    # Add formatter
    formatter = logging.Formatter(f_format, date_format)
    handler.setFormatter(formatter)
    handler.setLevel(level)

    handlers.append(handler)

    # Create console handler
    handler = logging.StreamHandler()
    handler.setLevel(console_level)

    formatter = logging.Formatter(c_format, date_format)
    handler.setFormatter(formatter)

    handlers.append(handler)

    logging.basicConfig(handlers=handlers, level=level, datefmt=date_format)
    logging.info('Initialized logging')


class MyLogger(logging.Logger):

    def makeRecord(self, name, level, fn, lno, msg, args, exc_info,
                   func=None, extra=None, sinfo=None):

        msg += 'asdfasdfasdf'
        path = os.path.dirname(os.path.abspath(swap.__file__))
        path = os.path.abspath(os.path.join(path, '../..'))
        print(path)

        path = os.path.relpath(fn, path)
        path = os.path.splitext(path)[0]
        print(path)

        module = '.'.join(path.split('/')[1:])
        # module = 'a123'

        return super().makeRecord(
            module, level, fn, lno, msg, args, exc_info,
            func=None, extra=None, sinfo=None)


if not __name__ == "__main__":
    init()
