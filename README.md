# blender_mmd_assets
blender_mmd_assets is an asset maintenance project for Blender and MMD.

The results of this project are being used by [UuuNyaa/blender_mmd_uuunyaa_tools](https://github.com/UuuNyaa/blender_mmd_uuunyaa_tools).

## Examples

### Get latest assets.json
```python
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
```

### Format of assets.json
```
{
  "format": "blender_mmd_assets:2",
  "description": "This file is a release asset of blender_mmd_assets",
  "license": "CC-BY-4.0 License",
  "created_at": "yyyy-mm-ddTHH:MM:SSZ",
  "asset_count": 9999,
  "assets": [
    {
      "id": "99999",
      "type": "MODEL_MMD",
      "url": "https://api.github.com/repos/UuuNyaa/blender_mmd_assets/issues/99999",
      "name": "English name",
      "tags": {
        "Male": "Male / 男性",
        "Official": "Official / 公式"
        ...
      },
      "updated_at": "yyyy-mm-ddTHH:MM:SSZ",
      "thumbnail_url": "https://.../thumbnail.png",
      "download_url": "https://.../download_asset.zip",
      "import_action": "unzip(f'{file}',encoding='cp932'); import_pmx('path/to.pmx',scale=0.08)",
      "aliases": {
        "en": "English name",
        "zh": "Chinese name",
        "ja": "Japanese name",
        ...
      },
      "note": "Something note"
    },
    ...
  ]
}
```

#### Types
- MODEL_MMD
- MODEL_BLENDER

#### Tags
- See [issue labels](https://github.com/UuuNyaa/blender_mmd_assets/labels)
