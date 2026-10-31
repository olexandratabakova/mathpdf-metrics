import copy,importlib.util,json
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'experiments/rag-fifteen'
spec=importlib.util.spec_from_file_location('rag_pipeline_test',PATH/'pipeline.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
def test_ranked_retrieval_on_frozen_handwritten_requests():
    reqs=json.loads((PATH/'requests.json').read_text(encoding='utf-8'));docs=p.bank()
    assert len(reqs)==15 and len(docs)==40
    top1=top3=0
    for r in reqs:
        found=p.retrieve(r,docs)['matches']
        top1+=found[0]['id'] in r['expected']
        top3+=any(m['id'] in r['expected'] for m in found)
        for m in found:
            assert m['doc']['domain']==r['domain']
            assert set(m['doc']['requires'])<=set(p.CONCEPTS[r['topic']])
    assert top1==14 and top3==15
def test_missing_topic_prerequisites_and_domain_refuse_generation():
    assert all(c['status']=='no_coverage' for c in p.controls())
    r={'id':1,'topic':'functions','goal':'reciprocal function','domain':'integer_pairs','available':['real_arithmetic']}
    assert p.retrieve(r,p.bank())['matches']==[]
def test_unsupported_templates_and_corrupted_generated_formulas_rejected():
    with pytest.raises(Exception):p.build_item('not_in_bank',1)
    item=p.build_item('ind_squares',3);bad=copy.deepcopy(item)
    bad['question'][-1]['latex']+=' + 1'
    with pytest.raises(ValueError):p.E.verify_artifact(bad)

def test_requested_parameter_restrictions_survive_generation():
    item=p.build_item('int_division',5,{'negative_dividend':True})
    assert item['parameters']['a']<0
    assert p.E.verify_artifact(item)
    with pytest.raises(ValueError):p.build_item('ind_squares',5,{'negative_dividend':True})

def test_public_rag_evidence_preserves_real_selection_and_limits():
    run=json.loads((PATH/'result.json').read_text(encoding='utf-8'))
    assert run['metrics']=={'requests':15,'top1_hits':14,'top3_hits':15,'model_goal_matches':15,'generated':15,'program_checks_passed':15,'negative_controls_refused':3}
    assert not run['expected_labels_sent'] and run['reviewer_calls']==0
    assert len(run['rows'])==15 and run['generation_calls']==1
    assert json.loads(run['raw_output'])==run['plan']
    for r in run['rows']:
        assert r['choice']['template_id'] in [d['id'] for d in r['retrieval']['matches']]
        assert r['different_from_exemplar'] and p.E.verify_artifact(r['item'])
        assert r['theory']['text'] and not p.re.search(r'\b(?:Example|Exercise)\s*\d',r['theory']['text'])
    assert run['rows'][4]['item']['parameters']['a']<0
    assert run['rows'][12]['retrieval']['matches'][0]['id']=='reciprocal_not_onto'
    assert run['rows'][12]['choice']['template_id']=='reciprocal_bijection'
    assert run['rendering']['status']=='passed' and run['rendering']['fallbacks']==0
    assert run['rendering']['rendered_math_blocks']==50
    assert 0<run['cost_usd']<.02
    raw=(ROOT/'rag-data.js').read_text(encoding='utf-8')
    assert json.loads(raw.removeprefix('window.MATHPDF_RAG = ').strip().removesuffix(';'))==run
    assert 'file_data' not in raw and 'base64,' not in raw and 'OPENAI_API_KEY' not in raw
