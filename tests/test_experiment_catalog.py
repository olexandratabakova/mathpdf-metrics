"""Keep public summaries tied to their evidence and unlike metrics distinguishable."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_catalog_is_reproducible_and_all_detail_targets_exist():
    spec=importlib.util.spec_from_file_location('catalog_builder', ROOT/'tools/build_experiment_catalog.py')
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    catalog=json.loads((ROOT/'data/experiments.json').read_text(encoding='utf-8'))
    assert catalog == module.build()
    script=(ROOT/'experiments-catalog.js').read_text(encoding='utf-8')
    assert json.loads(script.removeprefix('window.MATHPDF_EXPERIMENTS = ').strip().removesuffix(';')) == catalog
    assert len(catalog['experiments']) == 9
    assert len({x['id'] for x in catalog['experiments']}) == 9
    for study in catalog['experiments']:
        raw=json.loads((ROOT/study['evidence']).read_text(encoding='utf-8'))
        assert study['cost_usd'] == raw['cost_usd']
        assert study['date'] == raw['date']
        assert (ROOT/study['data_script']).is_file()
        assert study['chart_note']
        assert all(0 <= s['value'] <= s['total'] for s in study['series'])


def test_charts_do_not_hide_failed_first_pass_or_turn_coverage_into_accuracy():
    rows={e['id']:e for e in json.loads((ROOT/'data/experiments.json').read_text(encoding='utf-8'))['experiments']}
    assert [s['value'] for s in rows['rag-hundred']['series']] == [98,100,100]
    assert 'not mathematics' in rows['rag-hundred']['chart_note']
    assert [s['value'] for s in rows['cycle-fifteen']['series']] == [14,15,14,14]
    assert 'not task accuracy' in rows['sympy-55']['chart_note']
    assert 'overlap' in rows['review-four']['chart_note']
    assert all(s['unit']=='count' for s in rows['v5-seventy']['series'])


def test_home_shell_does_not_eagerly_load_experiment_payloads():
    for filename in ['index.html','experiment.html']:
        shell=(ROOT/filename).read_text(encoding='utf-8')
        assert '<html lang="en">' in shell
        assert '-data.js' not in shell
        assert 'experiments-catalog.js' in shell
    assert (ROOT/'experiment.html').is_file()
