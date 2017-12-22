#!/usr/bin/env python3

import click
import click_fish
import click_log
import html5lib
import logging
import requests
import rfc6266

from bs4 import BeautifulSoup
from urllib.parse import urljoin


LOGGING_LEVELS = {
    0: logging.WARNING,
    1: logging.INFO,
    2: logging.DEBUG
}


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
    # print(r.text)
    doc = BeautifulSoup(r.text, 'html5lib')
    print(doc.form['action'])
    print('-------')
    data = {e['name']: e.get('value') for e in doc.form.find_all('input', {'name': True})}
    print(data)

    print('=======')
    r = requests.post(urljoin(url, doc.form['action']), data=data, proxies=proxies)
    print(r)
    print(r.headers)
    filename = rfc6266.parse_headers(r.headers['Content-Disposition']).filename_unsafe
    with open(filename, 'wb') as f:
        f.write(r.content)


if __name__ == '__main__':
    mdt()
