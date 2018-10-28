# -*- coding: utf-8 -*-

import io
import os
import datetime
import jinja2

import twitter as twitter_api

from sirius.web.twitter import get_latest_tweet

DEFAULT_TEMPLATE_FILE = os.path.join(os.path.dirname(__file__), 'templates/default.html')

ENV = jinja2.Environment()

# TODO apply scrubber library if wanted.
# https://pypi.python.org/pypi/scrubber

def default_template(raw_html, from_name):
    with open(DEFAULT_TEMPLATE_FILE) as f:
        template = f.read()

    t = ENV.from_string(template)
    return t.render(
        raw_html=raw_html,
        date=datetime.datetime.now(),
        from_name=from_name
    ).encode('utf-8')


def deep_web_template():
    template_path = os.path.join(os.path.dirname(__file__), 'templates/deep_web.html')
    with io.open(template_path, mode='r', encoding='utf-8') as f:
        template = f.read()

    t = ENV.from_string(template)

    tiny_star_field = get_latest_tweet('tiny_star_field')['text']
    ten_print_chr = get_latest_tweet('10_print_chr')['text']
    a_strange_voyage = get_latest_tweet('str_voyage')['text']
    the_last_deck = get_latest_tweet('thelastdeck')['entities']['media'][0]['media_url_https']

    return t.render(
        tiny_star_field=tiny_star_field,
        ten_print_chr=ten_print_chr,
        the_last_deck=the_last_deck,
        a_strange_voyage=a_strange_voyage,
        timestamp=datetime.datetime.now(),
    ).encode('utf-8')
