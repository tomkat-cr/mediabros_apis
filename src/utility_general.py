# general_utilities.py
import sys
import traceback

from .utility_date import get_formatted_date


def get_api_standard_response():
    standard_response = dict()
    standard_response['error'] = False
    standard_response['error_message'] = ''
    standard_response['data'] = {}
    return standard_response


def get_command_line_args():
    params = dict()
    params['mode'] = 'api'
    params['config_filename'] = '.env'
    if len(sys.argv) > 1:
        params['mode'] = sys.argv[1]
    if len(sys.argv) > 2:
        params['config_filename'] = sys.argv[2]
    if len(sys.argv) > 3:
        params['body'] = ' '.join(
            [sys.argv[i] for i in range(3, len(sys.argv))]
        )
    print('get_command_line_args')
    print(f'params: {str(params)}')
    return params


def get_default_db_resultset():
    resultset = {
        'error': False,
        'error_message': None,
        'resultset': {}
    }
    return resultset


def log_warning(log_msg):
    print(log_msg)


def log_endpoint_debug(log_msg):
    print('---------')
    print(get_formatted_date())
    print(log_msg)


def format_stacktrace():
    parts = ["Traceback (most recent call last):\n"]
    parts.extend(traceback.format_stack(limit=25)[:-2])
    parts.extend(traceback.format_exception(*sys.exc_info())[1:])
    return "".join(parts)


def get_standard_base_exception_msg(err, message_code='NO_E_CODE'):
    """When a BaseException is fired, use this method to return
    a standard error message"""
    message_code = f"[{message_code=}]" if message_code == '' else ''
    response = f"Unexpected {err=}, {type(err)=} {message_code=}"
    log_warning(response)
    log_warning(format_stacktrace())
    return response
