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
    assert len(catalog['experiments']) == 12
    assert len({x['id'] for x in catalog['experiments']}) == 12
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


def test_comparison_baseline_uses_recorded_metrics_not_task_acceptance():
    catalog=json.loads((ROOT/'data/experiments.json').read_text(encoding='utf-8'))
    baseline=catalog['flashcard_baseline']
    raw=json.loads((ROOT/'experiments/wildflower/result.json').read_text(encoding='utf-8'))
    assert baseline['n']==raw['metrics']['cards_generated']==60
    assert baseline['scores']['sc']==raw['metrics']['cards']['pct_self_contained']==.8
    assert baseline['scores']['faith']==raw['metrics']['cards']['avg_faithfulness']
    assert baseline['scores']['sc']!=raw['metrics']['problem_decisions']['accept']/40
    assert sum(t['n'] for t in baseline['topics'])==60
    candidate=catalog['flashcard_candidates'][0]
    assert candidate['id']=='clearleaf' and candidate['n']==20
    assert candidate['scores']['sc']==.7  # Original rubric, not the revised .9 diagnostic.
    expanded=catalog['flashcard_candidates'][1]
    assert expanded['id']=='clearleaf-sixty' and expanded['n']==60
    assert expanded['scores']['sc']==47/60


def test_primary_choice_and_borrowing_notes_do_not_relabel_experiment_results():
    catalog=json.loads((ROOT/'data/experiments.json').read_text(encoding='utf-8'))
    assert catalog['primary_flashcard_version']=='wildflower'
    direction=catalog['flashcard_direction']
    assert direction['selected_by']=='user' and direction['primary']=='wildflower'
    assert direction['historical_scores']['v1']['dup']<.02
    assert direction['historical_scores']['v2']['coverage']>.87
    assert direction['historical_scores']['v3']['sc']>.93
    assert {x['source'] for x in direction['borrow_candidates']}=={'v1','v2','v3','v4','clearleaf-sixty'}
    assert 'separate candidate' in direction['decision']
    assert all(e['cost_usd']==json.loads((ROOT/e['evidence']).read_text(encoding='utf-8'))['cost_usd'] for e in catalog['experiments'])
