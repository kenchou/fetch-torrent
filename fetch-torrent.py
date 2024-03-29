#!/usr/bin/env python3

import click
import click_log
import html
import html5lib
import logging
import requests

from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urljoin, urlparse, urlencode
from werkzeug.http import parse_options_header


LOGGING_LEVELS = {
    0: logging.WARNING,
    1: logging.INFO,
    2: logging.DEBUG
}

proxies = None
output_filename = None


@click.command()
@click.argument('url')
@click.option('-o', '--output', help='output filename')
@click.option('--proxy', help='proxy. example: socks5://user:pass@host:port')
@click.option('-v', '--verbose', count=True, help='set log level.')
def mdt(url, output, proxy, verbose):
    global proxies, output_filename
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

    if output:
        output_filename = output

    try:
        dispatch(url)
    except KeyError:
        post_form(url)


def dispatch(url):
    # hostname = urlparse(url).hostname
    # special_methods = {}
    # method = special_methods[hostname]
    return post_form(url)


def post_form(url):
    session = requests.Session()
    response = session.get(url, proxies=proxies, timeout=10)
    response.raise_for_status()

    print('POST Form: request URL', url)
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
    logging.info('Response URL: %s,  Status: %s, Headers: %s', response.url, response.status_code, response.headers)
    response.raise_for_status()
    if response.history:
        for resp in response.history:
            print(resp.status_code, resp.url)
    # print(r.text)
    if output_filename:
        filename = output_filename
    else:
        # detect filename from header or url
        filename = Path(urlparse(next_url).path).name
        if 'Content-Disposition' in response.headers:
            content_disposition = parse_options_header(response.headers['Content-Disposition'].encode('iso-8859-1').decode('utf-8'))
            for v in content_disposition:
                if isinstance(v, dict) and 'filename' in v:
                    filename = v['filename']
                    break
        filename = html.unescape(filename)

    print('Save to file', filename)
    with open(filename, 'wb') as f:
        f.write(response.content)


if __name__ == '__main__':
    mdt()
