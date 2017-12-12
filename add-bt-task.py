#!/usr/bin/env python3

import base64
import click
import click_log
import hashlib
import json
import logging
import os.path
import requests


logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)
click_log.basic_config(logger)


@click.command()
@click.argument('torrent-file')
def main(torrent_file):
    """Aria2 RPC Client"""
    logger.info(torrent_file)

    config_file = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_file) as f:
        config = json.load(f)
    aria2_rpc_url = config.get('aria2-rpc-url', 'http://localhost:6800/jsonrpc')
    token = config.get('token')

    params = []
    if token:
        params.append('token:{}'.format(token))

    with open(torrent_file, 'rb') as f:
        torrent = base64.b64encode(f.read()).decode('utf-8')
        params.append(torrent)

    task_id = hashlib.sha1(os.path.basename(torrent_file).encode('utf-8')).hexdigest()

    data = json.dumps({'jsonrpc': '2.0', 'id': task_id, 'method': 'aria2.addTorrent', 'params': params})

    # print(aria2_rpc_url, torrent_file)

    headers = {'content-type': 'application/json'}

    response = requests.post(aria2_rpc_url, data=data, headers=headers)

    print(response.json())


if __name__ == '__main__':
    main()
