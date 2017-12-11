#!/usr/bin/env python3

import base64
import click
import click_log
import hashlib
import json
import logging
import os.path
import requests

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

    with open(torrent_file, 'rb') as f:
        torrent = base64.b64encode(f.read())

    task_id = hashlib.sha1(torrent_file)
    data = json.dumps({'jsonrpc': '2.0', 'id': task_id, 'method': 'aria2.addTorrent', 'params': [torrent]})
    requests.get(aria2_rpc_url, data)


if __name__ == '__main__':
    main()
