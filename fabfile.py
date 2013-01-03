from fabric.api import task
import requests
import json
from pygments import highlight
from pygments.lexers import JSONLexer
from pygments.formatters import Terminal256Formatter
from settings import *
from local_settings import INSTAGRAM_PUSH_CALLBACK_URL as INSTAGRAM_PUSH_CALLBACK_URL_LOCAL

INSTAGRAM_SUB_URL = "https://api.instagram.com/v1/subscriptions"
INSTAGRAM_TAG_BASE = "https://api.instagram.com/v1/tags"


def format_json(json_str):
    formatted_output = json.dumps(json_str, sort_keys=True,
                                  indent=2, separators=(',', ':'))
    return highlight(formatted_output, JSONLexer(),
                     Terminal256Formatter(style='monokai'))


@task(alias='lsub')
def list_subscription():
    query_str = {
        'client_secret': INSTAGRAM_APP_SECRET,
        'client_id': INSTAGRAM_APP_ID
    }
    r = requests.get(INSTAGRAM_SUB_URL, params=query_str)
    print(format_json(r.json))


@task(alias='dsub')
def del_subscription():
    query_str = {
        'client_secret': INSTAGRAM_APP_SECRET,
        'client_id': INSTAGRAM_APP_ID,
        'object': 'all'
    }
    r = requests.delete(INSTAGRAM_SUB_URL, params=query_str)
    print(format_json(r.json))


@task(alias='rsub_local')
def reset_subscription_local():
    del_subscription()
    payload = {
        'client_secret': INSTAGRAM_APP_SECRET,
        'client_id': INSTAGRAM_APP_ID,
        'object': 'tag',
        'aspect': 'media',
        'object_id': TAG,
        'callback_url': INSTAGRAM_PUSH_CALLBACK_URL_LOCAL
    }
    r = requests.post(INSTAGRAM_SUB_URL, data=payload)
    print(format_json(r.json))


@task(alias='rsub_remote')
def reset_subscription_local():
    del_subscription()
    payload = {
        'client_secret': INSTAGRAM_APP_SECRET,
        'client_id': INSTAGRAM_APP_ID,
        'object': 'tag',
        'aspect': 'media',
        'object_id': TAG,
        'callback_url': INSTAGRAM_PUSH_CALLBACK_URL
    }
    r = requests.post(INSTAGRAM_SUB_URL, data=payload)
    print(format_json(r.json))
