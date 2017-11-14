#!/usr/bin/env python


import click
import click_fish
import click_log
import logging
import requests
import rfc6266

from bs4 import BeautifulSoup
from urllib.parse import urljoin

logger = logging.getLogger(__name__)
click_log.basic_config(logger)


@click.command()
@click.argument('url')
@click.option('-v', '--verbose', count=True, help='set log level.\n'
                                                  '-v=warning\n'
                                                  '-vv=info,\n'
                                                  '-vvv=debug,\n'
                                                  '-vvvv=show http debug')
def mdt(url, verbose):
    """LoveLive! Master Data Tools."""
    logger.info(url)

    # parsed_url = urlparse(url)
    # parsed_query_string = parse_qs(parsed_url.query)
    # print(parsed_url, parsed_query_string)
    #
    # post_url = urljoin(url, 'fetch.php')
    # print(post_url)
    #
    # r = requests.post(post_url, {'code'})
    #
    # exit()

    r = requests.get(url)

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
    r = requests.post(urljoin(url, doc.form['action']), data=data)
    print(r)
    print(r.headers)
    filename = rfc6266.parse_headers(r.headers['Content-Disposition']).filename_unsafe
    with open(filename, 'wb') as f:
        f.write(r.content)


if __name__ == '__main__':
    mdt()
