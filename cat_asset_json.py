# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of blender_mmd_assets.

import ast
import datetime
import itertools
import json
import os
import re
import sys

import requests


def find_child_element(element, element_type):
    for e in element['children']:
        if e['element'] == element_type:
            return e
    return None


def find_child_elements(element, element_type):
    return [
        e for e in element['children']
        if e['element'] == element_type
    ]


class markdown:
    @staticmethod
    def parse_line(markdown_line):
        # image
        match = re.fullmatch(r'!\[([^\]]*)\]\((.*?)\s*("(?:.*[^"])")?\s*\)', markdown_line)
        if match:
            return {'type': 'image', 'markdown': markdown_line, 'alt': match.group(1), 'url': match.group(2)}

        match = re.fullmatch(r'\|\s([^\|]+)\s\|\s([^\|]+)\s\|', markdown_line)
        if match:
            return {'type': 'alias', 'markdown': markdown_line, 'language': match.group(1), 'representation': match.group(2)}

        return {'type': 'plain', 'markdown': markdown_line}

    @staticmethod
    def parse(markdown_text):
        lines = []
        root_block = {'header': '', 'depth': 0, 'lines': lines, 'children': []}
        block_stack = [root_block]

        def append_child(child_block):
            block_stack[-1]['children'].append(child_block)
            block_stack.append(child_block)

        def remove_empty_lines(lines, line_number):
            if len(lines) == 0:
                return

            while len(lines[line_number]['markdown'].strip()) == 0:
                del lines[line_number]

        for markdown_line in markdown_text.split('\n'):
            markdown_line = markdown_line.rstrip()
            if markdown_line.startswith('```'):
                continue
            elif not markdown_line.startswith('#'):
                lines.append(markdown.parse_line(markdown_line))
                continue

            match = re.fullmatch(r'^(#+)\s+(.+)$', markdown_line)
            header_level = len(match.group(1))
            header_text = match.group(2)

            # remove head empty lines
            remove_empty_lines(lines, +0)

            # remove tail empty lines
            remove_empty_lines(lines, -1)

            if block_stack[-1]['depth'] >= header_level:
                while block_stack[-1]['depth'] >= header_level:
                    del block_stack[-1]
            else:
                while block_stack[-1]['depth'] + 1 < header_level:
                    append_child({'header': '', 'depth': block_stack[-1]['depth'] + 1, 'lines': [], 'children': []})

            lines = []
            append_child({'header': header_text, 'depth': header_level, 'lines': lines, 'children': []})

        return root_block

    @staticmethod
    def traverse_blocks(blocks):
        yield blocks
        for block in blocks['children']:
            for child in markdown.traverse_blocks(block):
                yield child

    @staticmethod
    def to_markdown(blocks):
        result = ''
        for block in markdown.traverse_blocks(blocks):
            if block['header']:
                if result:
                    result += '\n'

                result += f"{'#' * block['depth']} {block['header']}\n"
            for line in block['lines']:
                result += f"{line['markdown']}\n"

        return result


def list_assets(session, repo, query):
    per_page = 100
    issues = []
    for page in itertools.count(1):
        response = session.get(
            f'https://api.github.com/repos/{repo}/issues',
            params={**query, 'per_page': per_page, 'page': page},
            headers={'Accept': 'application/vnd.github.v3+json'}
        )
        response.raise_for_status()

        fetche_issues = [
            {
                'url': issue['url'],
                'number': issue['number'],
                'title': issue['title'],
                'labels': {label['name']: label['description'] for label in issue['labels']},
                'body': issue['body'],
                'updated_at': issue['updated_at'],
            } for issue in json.loads(response.text)
        ]
        issues += fetche_issues

        if len(fetche_issues) < per_page:
            break

    issues.reverse()

    assets = []
    for issue in issues:
        blocks = markdown.parse(issue['body'])

        tags = {
            label: tag for label, tag in issue['labels'].items()
            if label not in [
                'duplicate',
                'enhancement',
                'invalid',
                'question',
            ] and (not label.startswith('type='))
        }

        types = [
            label[len('type='):] for label, tag in issue['labels'].items()
            if label.startswith('type=')
        ]

        if len(types) != 1:
            print(f"WARN: invalid len(type)={len(types)}, number={issue['number']}", file=sys.stderr)

        asset = {
            'id': f"{issue['number']:05d}",
            'type': types[0],
            'url': issue['url'],
            'name': issue['title'],
            'tags': tags,
            'updated_at': issue['updated_at'],
        }

        for block in markdown.traverse_blocks(blocks):
            if block['header'] == 'aliases':
                asset['aliases'] = {
                    line['language']: line['representation']
                    for line in block['lines']
                    if line['type'] == 'alias'
                }
            elif block['header']:
                line = block['lines'][0]
                asset[block['header']] = line['url'] if line['type'] == 'image' else '\n'.join([line['markdown'] for line in block['lines']])

        assets.append(asset)

    return {
        'format': 'blender_mmd_assets:2',
        'description': 'This file is a release asset of blender_mmd_assets',
        'license': 'CC-BY-4.0 License',
        'created_at': datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        'asset_count': len(assets),
        'assets': assets,
    }


if __name__ == '__main__':
    if len(sys.argv) not in {2, 3}:
        print(f'ERROR: invalid arguments: {[a for a in sys.argv]}', file=sys.stderr)
        print('USAGE: python cat_asset_json.py REPO_USER/REPO_PATH [QUERY]')
        exit(1)

    token = os.environ.get('GITHUB_TOKEN')
    repo = sys.argv[1]

    if len(sys.argv) == 3:
        query = ast.literal_eval(sys.argv[2])
    else:
        query = {'state': 'open', 'labels': 'Official'}

    session = requests.Session()
    session.auth = (None, token)
    print(json.dumps(list_assets(session, repo, query), indent=2, ensure_ascii=False))
