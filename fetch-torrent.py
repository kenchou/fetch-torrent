#!/usr/bin/env python3

import click
import click_fish
import click_log
import html5lib
import logging
import requests
import rfc6266

from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urljoin, urlparse, urlencode


LOGGING_LEVELS = {
    0: logging.WARNING,
    1: logging.INFO,
    2: logging.DEBUG
}

proxies = None


@click.command()
@click.argument('url')
@click.option('--proxy', help='proxy. example: socks5://user:pass@host:port')
@click.option('-v', '--verbose', count=True, help='set log level.')
def mdt(url, proxy, verbose):
    """LoveLive! Master Data Tools."""
    logging.basicConfig(level=LOGGING_LEVELS.get(verbose, logging.INFO))
    logger = logging.getLogger(__name__)
    click_log.basic_config(logger)
    logger.info(url)

    if proxy:
        proxies = {
            'http': proxy,
            'https': proxy,
        }
    else:
        proxies = {}

    dispatch(url)


def dispatch(url):
    hostname = urlparse(url).hostname
    return {
        'www.jandown.com': post_form,
        'www.rmdown.com': post_form,
        'xavbt.com': post_form,
    }[hostname](url)


def post_form(url):
    session = requests.Session()
    response = session.get(url, proxies=proxies, timeout=10)

    print('request URL', url)
    logging.info('r.url: %s', response.url)
    logging.info('Code: %s', response.status_code)
    logging.info('Encoding: %s', response.encoding)
    logging.info('Response Headers: %s', response.headers)

    # print(r.text)
    doc = BeautifulSoup(response.text, 'html5lib')

    next_url = urljoin(response.url, doc.form['action'])
    method = doc.form['method']
    logging.info('action: %s', doc.form['action'])
    logging.info('method: %s', doc.form['method'])

    data = {e['name']: e.get('value') for e in doc.form.find_all('input', {'name': True})}
    logging.info('params: %s', data)

    logging.info('======= Next Request ========')
    logging.info('next request: %s, params: %s',  next_url, data)
    if 'get' == method:
        response = session.get(next_url, params=data, proxies=proxies, timeout=10)
    elif 'post' == method:
        response = session.post(next_url, data=data, proxies=proxies, timeout=10)
    logging.info('Response Headers: %s', response.headers)
    # print(r.text)
    filename = rfc6266.parse_headers(response.headers['Content-Disposition']).filename_unsafe
    print('Save to file', filename)
    with open(filename, 'wb') as f:
        f.write(response.content)


if __name__ == '__main__':
    mdt()
