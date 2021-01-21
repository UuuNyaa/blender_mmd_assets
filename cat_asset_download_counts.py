# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of blender_mmd_assets.

import json
import sys

import requests


def list_asset_download_counts(session, repo):
    response = session.get(f'https://api.github.com/repos/{repo}/releases')
    response.raise_for_status()

    releases = json.loads(response.text)

    assets = []
    for release in releases:
        for asset in release['assets']:
            assets.append({
                'updated_at': asset['updated_at'],
                'name': asset['name'],
                'size': asset['size'],
                'download_count': asset['download_count'],
            })

    return assets


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f'ERROR: invalid arguments: {[a for a in sys.argv]}', file=sys.stderr)
        exit(1)

    repo = sys.argv[1]

    session = requests.Session()
    print(json.dumps(list_asset_download_counts(session, repo), indent=2, ensure_ascii=False))
