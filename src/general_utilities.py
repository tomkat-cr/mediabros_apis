# general_utilities.py
import sys


def get_api_standard_response():
    standard_response = dict()
    standard_response['error'] = False
    standard_response['error_message'] = ''
    standard_response['data'] = dict()
    return standard_response


def get_command_line_args():
    params = dict()
    params['mode'] = 'api'
    params['config_filename'] = '.env'
    if len(sys.argv) > 1:
        params['mode'] = sys.argv[1]
    if len(sys.argv) > 2:
        params['config_filename'] = sys.argv[2]
    return params
