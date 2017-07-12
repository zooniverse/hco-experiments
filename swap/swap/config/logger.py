import logging
import logging.handlers
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


def log_level(level):
    for i in range(0, 51, 10):
        if level == logging.getLevelName(i):
            return i


def console_handler(date_format):
    level = log_level(config.logging.console_level)
    format_ = config.logging.console_format

    # Create console handler
    handler = logging.StreamHandler()
    handler.setLevel(level)

    formatter = logging.Formatter(format_, date_format)
    handler.setFormatter(formatter)

    return handler


def file_handler(date_format):
    def static():
        fname = config.logging.files.static
        fname = os.path.join(get_path(), fname)

        max_size = config.logging.files.max_size_mb * (1024 ** 2)
        keep = config.logging.files.keep_logs

        return logging.handlers.RotatingFileHandler(
            fname, maxBytes=max_size, backupCount=keep)

    def dynamic():
        fname = config.logging.files.dynamic
        fname = fname % {'pid': os.getppid()}
        # Create file handler
        fname = os.path.join(get_path(), fname)
        return logging.FileHandler(fname)

    version = config.logging.files.version
    if version == 'static':
        handler = static()
    if version == 'dynamic':
        handler = dynamic()

    format_ = config.logging.file_format
    level = log_level(config.logging.level)

    # Add formatter
    formatter = logging.Formatter(format_, date_format)
    handler.setFormatter(formatter)
    handler.setLevel(level)

    return handler


def system_file_handler(date_format):
    path = config.logging.system.location
    fname = config.logging.system.name
    fname = os.path.join(path, fname)

    max_size = config.logging.system.max_size * (1024 ** 2)
    keep = config.logging.system.keep

    handler = logging.handlers.RotatingFileHandler(
        fname, maxBytes=max_size, backupCount=keep)

    level = config.logging.level
    format_ = config.logging.file_format

    # Add formatter
    formatter = logging.Formatter(format_, date_format)
    handler.setFormatter(formatter)
    handler.setLevel(level)

    return handler


# def get_logger(name):
#     return logging.getLogger('hco.%s' % name)


def init():
    date_format = config.logging.date_format
    level = log_level(config.logging.level)

    handlers = []
    # Ensure each process has its own unique log file
    # to prevent file write conflicts
    # TODO implement global log server with unique uuid per process
    handlers.append(file_handler(date_format))
    handlers.append(console_handler(date_format))

    if config.logging.system.active:
        handlers.append(system_file_handler(date_format))

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
