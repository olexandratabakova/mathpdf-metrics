from pathlib import Path
import json
from tools.publish_snapshot import validate


def test_history_integrity():
    root = Path(__file__).resolve().parents[1]
    data = validate(json.loads((root/'data/history.json').read_text(encoding='utf-8')))
    assert len(data['records']) == 27
    assert len(data['cards']) == sum(r['n'] for r in data['records']) == 505
    assert {v: sum(r['n'] for r in data['records'] if r['version']==v) for v in ['v1','v2','v3','v4']} == {'v1':160,'v2':180,'v3':130,'v4':35}
    assert len(data['issues']) == 19
    script = (root/'data.js').read_text(encoding='utf-8')
    assert json.loads(script.removeprefix('window.MATHPDF_DATA = ').strip().removesuffix(';')) == data


def test_invalid_snapshot_cannot_publish():
    import pytest
    with pytest.raises(ValueError): validate({'schema_version':2})
    with pytest.raises(ValueError): validate({'schema_version':1,'versions':[{'id':'v1'},{'id':'v1'}],'records':[],'cards':[],'issues':[]})
