# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of blender_mmd_assets.

# Get latest asset download URL
import json
import requests

repo = 'UuuNyaa/blender_mmd_assets'
response = requests.get(
    f'https://api.github.com/repos/{repo}/releases/latest',
    headers={'Accept': 'application/vnd.github.v3+json'}
)

asset = json.loads(response.text)['assets'][0]
browser_download_url = asset['browser_download_url']

# Get assets zip file
response = requests.get(
    browser_download_url,
    headers={'Accept': 'application/zip'}
)

# Extract assets.json
import io
import zipfile

with zipfile.ZipFile(io.BytesIO(response.content)) as zip:
    assets_json = zip.read('assets.json').decode('utf-8')

print(assets_json)