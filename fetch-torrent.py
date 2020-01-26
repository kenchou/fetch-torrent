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
from urllib.parse import urljoin, urlparse


LOGGING_LEVELS = {
    0: logging.WARNING,
    1: logging.INFO,
    2: logging.DEBUG
}

proxies = None
logger = logging.getLogger(__name__)
click_log.basic_config(logger)


@click.command()
@click.argument('url')
@click.option('--proxy', help='proxy. example: socks5://user:pass@host:port')
@click.option('-v', '--verbose', count=True, help='set log level.')
def mdt(url, proxy, verbose):
    """LoveLive! Master Data Tools."""
    logging.basicConfig(level=LOGGING_LEVELS.get(verbose, logging.DEBUG))
    logger.info(url)

    if proxy:
        proxies = {
            'http': proxy,
            'https': proxy,
        }
    else:
        proxies = {}

    r = requests.get(url, proxies=proxies)
    print('Code    :', r.status_code)
    print('Encoding:', r.encoding)
    print(r.headers)
    print('r.url:', r.url)

    dispatch(url)(r)


def dispatch(url):
    hostname = urlparse(url).hostname
    return {
        'jandown.com': post_form,
        'www.jandown.com': post_form,
        'rmdown.com': post_form,
        'www.rmdown.com': post_form,
    }[hostname]


def post_form(response):
    print('jandown:')
    # print(r.text)
    doc = BeautifulSoup(response.text, 'html5lib')
    print(doc.form['action'])
    print('-------')
    data = {e['name']: e.get('value') for e in doc.form.find_all('input', {'name': True})}
    print(data)

    print('=======')
    r = requests.post(urljoin(response.url, doc.form['action']), data=data, proxies=proxies)
    print(r)
    print(r.headers)
    if 'Content-Disposition' in r.headers:
        filename = rfc6266.parse_headers(r.headers['Content-Disposition']).filename_unsafe
    elif 'ref' in data:
        filename = Path(data['ref']).with_suffix('.torrent')
    else:
        raise IOError('Undetected filename')
    with open(filename, 'wb') as f:
        f.write(r.content)


if __name__ == '__main__':
    mdt()
