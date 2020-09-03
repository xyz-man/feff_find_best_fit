'''
* Created by Zhenia Syryanyy (Yevgen Syryanyy)
* e-mail: yuginboy@gmail.com
* Last modified: 02.09.2020
'''
'''
https://www.pythoncircle.com/post/46/how-to-start-logging-errors-in-django-app/
Django uses python's built in logging module. Django's logging module consist four players.
Loggers
Handlers
Filters
Formatters

Logger is the entry point to any logging system. It is kind of a bucket with a name where you push your error message.
Handler decides what needs to be done for each message in logger.
Filters put restrictions on each message and decide which message should be passed from logger to handler.
	For example only messages with severity level equal to or higher than 'error' should be processed.
Formatters decide the format in which error messages should be displayed as text.



Log levels in python:
DEBUG: Low level system information for debugging purposes
INFO: General system information
WARNING: Information describing a minor problem that has occurred.
ERROR: Information describing a major problem that has occurred.
CRITICAL: Information describing a critical problem that has occurred.

Understanding the code:
Django uses dictConfig format for logging configurations. Version defines the schema version to be used here.
It accepts positive integer and as of now only acceptable valid value is 1 .
disable_existing_loggers if set to True disable any default loggers. This doesn't remove loggers from system but simply
deactivate them and any such loggers simply discard any logging message received by them.
In the code above we defined two type of formatters, large and tiny. In large formatter we will be logging descriptive
message with date time, log1 level, process, file name, function name, line number and error message.
In tiny formatter we will be logging on message and date time.
We defined two type of handlers, error_file and info_file. error_file handler will handle messages with log1 level equal
to or greater than error as defined by level key. logging.handlers.TimedRotatingFileHandler value in class field defines
that files are created on time basis. When field have value midnight  which means new file is created at midnight.
File name is the path to file. This path should have write permission. Formatter key define the formatter to use, large
in this case.
We created two named loggers, error_logger and info_logger. We defined the log1 level and handler to use for each logger.
If you do not want parent of any logger to capture and log1 the message then set propagation to false.
'''

import os
from pkg_lib.pkg_cfg.class_configure import Configuration

LOG_FOLDER_ABSOLUTE_PATH = os.path.join(Configuration.PATH_TO_ROOT_PROJECT_DIRECTORY, 'log', 'logging')
print('LOG_FOLDER_ABSOLUTE_PATH', LOG_FOLDER_ABSOLUTE_PATH)


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'large': {
            'format': '%(asctime)s  %(levelname)s  %(process)d  %(pathname)s  %(funcName)s  %(lineno)d  %(message)s  '
        },
        'tiny': {
            'format': '%(asctime)s  %(message)s  '
        }
    },
    'handlers': {
        'errors_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'when': 'midnight',
            'interval': 1,
            'filename': os.path.join(LOG_FOLDER_ABSOLUTE_PATH, 'ErrorLoggers.log'),
            'formatter': 'large',
        },
        'info_file': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'when': 'midnight',
            'interval': 1,
            'filename': os.path.join(LOG_FOLDER_ABSOLUTE_PATH, 'InfoLoggers.log'),
            'formatter': 'large',
        },
    },
    'loggers': {
        'error_logger': {
            'handlers': ['errors_file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'info_logger': {
            'handlers': ['info_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

if __name__ == '__main__':
    print('-> you run ', __file__, ' file in the main mode (Top-level script environment)')
