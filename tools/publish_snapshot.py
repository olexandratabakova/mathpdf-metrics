"""Validate a dashboard JSON backup, then write both public snapshot formats.

No network or provider requests. Use an exported backup as input, not data.js.
"""
import argparse
import json
import math
from pathlib import Path


def validate(data):
    if not isinstance(data, dict) or data.get('schema_version') != 1:
        raise ValueError('Expected Quality Lab schema_version 1.')
    groups = ('versions', 'records', 'cards', 'issues')
    if any(not isinstance(data.get(k), list) for k in groups):
        raise ValueError('Missing versions, records, cards or issues list.')
    for key in groups:
        ids = [r.get('id') for r in data[key]]
        if any(not isinstance(i, str) or not i.strip() for i in ids) or len(ids) != len(set(ids)):
            raise ValueError(f'{key} requires unique nonempty string IDs.')
    versions = {v['id'] for v in data['versions']}
    for key in ('records', 'cards', 'issues'):
        if any(r.get('version') not in versions for r in data[key]):
            raise ValueError(f'{key} references an unknown version.')
    for row in data['records']:
        if type(row.get('n')) is not int or row['n'] < 1 or not isinstance(row.get('topic'), str):
            raise ValueError('Invalid set topic or count.')
        for metric in ('sc', 'faith', 'atomic', 'coverage', 'dup', 'leaks', 'understanding', 'trivial'):
            value = row.get(metric)
            if value is not None and (type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= 1):
                raise ValueError(f'Invalid metric: {metric}')
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('backup', type=Path)
    args = parser.parse_args()
    data = validate(json.loads(args.backup.read_text(encoding='utf-8-sig')))
    root = Path(__file__).resolve().parents[1]
    pretty = json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + '\n'
    script = 'window.MATHPDF_DATA = ' + json.dumps(data, ensure_ascii=False, allow_nan=False).replace('<', '\\u003c') + ';\n'
    (root/'data/history.json').write_text(pretty, encoding='utf-8')
    (root/'data.js').write_text(script, encoding='utf-8')
    print(f"Snapshot saved: {len(data['versions'])} versions, {len(data['cards'])} cards.")


if __name__ == '__main__':
    main()
