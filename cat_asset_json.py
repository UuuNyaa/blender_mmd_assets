# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of blender_mmd_assets.

import json
import os
import sys
from enum import Enum

import requests
from marko.ast_renderer import ASTRenderer
from marko.parser import Parser


def list_assets(session, repo):
    response = session.get(
        f'https://api.github.com/repos/{repo}/issues',
        params={'state': 'open'},
        headers={'Accept': 'application/vnd.github.v3+json'}
    )
    response.raise_for_status()

    issues = reversed(json.loads(response.text))
    issue_parts = [
        {
            'url': issue['url'],
            'number': issue['number'],
            'title': issue['title'],
            'labels': {label['name']: label['description'] for label in issue['labels']},
            'body': issue['body'],
        } for issue in issues
    ]

    def find_child_element(element, element_type):
        for e in element['children']:
            if e['element'] == element_type:
                return e
        return None

    section = 'unknown'
    markdown_parser = Parser()
    ast_renderer = ASTRenderer()

    assets = []
    for issue_part in issue_parts:
        issue_body = issue_part['body']
        markdown_ast = ast_renderer.render(markdown_parser.parse(issue_body))

        tags = [
            tag for label, tag in issue_part['labels'].items()
            if label not in [
                'duplicate',
                'enhancement',
                'invalid',
                'question',
            ] and (not label.startswith('type='))
        ]

        types = [
            label[len('type='):] for label, tag in issue_part['labels'].items()
            if label.startswith('type=')
        ]

        if len(types) != 1:
            print(f"WARN: invalid len(type)={len(types)}, number={issue_part['number']}", file=sys.stderr)

        asset = {
            'id': issue_part['number'],
            'type': types[0],
            'url': issue_part['url'],
            'name': issue_part['title'],
            'tags': tags,
        }

        for element in markdown_ast['children']:
            element_type = element['element']
            if element_type == 'heading':
                section = find_child_element(element, 'raw_text')['children']
            elif element_type == 'paragraph':
                if section == 'thumbnail_url':
                    asset[section] = find_child_element(element, 'image')['dest']
                else:
                    asset[section] = find_child_element(element, 'raw_text')['children']

        if 'note' not in asset:
            asset['note'] = ''
        else:
            issule_body_lines = list(map(lambda l: l.rstrip(), issue_body.split('\n')))
            note_header_index = next(iter([
                index for index, line in enumerate(issule_body_lines)
                if line.startswith('#') and ' note' in line
            ]), None)
            if note_header_index is not None:
                asset['note'] = '\n'.join(issule_body_lines[note_header_index+1:])
            else:
                print(f"WARN: invalid note format, number={issue_part['number']}", file=sys.stderr)

        assets.append(asset)

    return {
        'format': 'blender_mmd_assets:1',
        'description': 'This file is release artifact of blender_mmd_assets',
        'license': 'CC-BY-4.0 License',
        'assets': assets,
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"ERROR: invalid arguments: {[a for a in sys.argv]}", file=sys.stderr)
        exit(1)

    token = os.environ.get('GITHUB_TOKEN')
    repo = sys.argv[1]

    session = requests.Session()
    session.auth = (None, token)
    print(json.dumps(list_assets(session, repo), indent=2, ensure_ascii=False))
