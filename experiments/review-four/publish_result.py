"""Publish sanitized experiment evidence into the static metrics dashboard.

No API calls. Does not publish PDFs, credentials or the input file payload.
"""
from fractions import Fraction
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]


def main():
    stages={name:json.loads((ROOT/'output'/f'{name}.json').read_text(encoding='utf-8')) for name in ['generate','blind','audit']}
    ledger=json.loads((ROOT/'output/ledger.json').read_text())
    assert all(s['status']=='completed' and 'parsed' in s for s in stages.values())
    assert len(stages['generate']['expanded'])==4
    # Reproducible narrow checks, not a universal mathematics verifier.
    assert [2*x+1 for x in [1,2,3,4]]==[3,5,7,9]
    left=Fraction(2**2-1,2)
    wrong=2+1-Fraction(1,2)
    correct=2-Fraction(1,2)
    assert left==correct and left!=wrong
    assert 2-1 != left  # Blind reviewer incorrectly said the common-domain values coincide.
    assert Fraction(1,3).denominator!=1  # Target (1,0) for the fourth map.
    checks={'kind':'narrow deterministic local checks, supplemented by manual review',
        'finite_range':[3,5,7,9],
        'problem_2_at_x_2':{'actual_value':'3/2','generated_simplification':'5/2','correct_simplification':'x - 1/x','blind_common_domain_equality':False},
        'problem_4_target':[1,0],'problem_4_required_input':['1/3','1/3'],
        'limits':'These checks establish the specific displayed counterexample; they do not establish universal validator coverage or statistical reviewer accuracy.'}
    (ROOT/'manual-checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    run={'id':'review-four-2026-10-30','date':'2026-10-30','title':'4 задачі · mini → незалежна перевірка GPT‑4.1',
        'summary':'Перевіряльник прийняв усі 4 задачі, але пропустив алгебраїчну помилку в задачі 2. Збережено оригінали, рішення моделі та окреме локальне спростування.',
        'cost_usd':sum(x['cost_usd'] for x in ledger['calls']),'difficulty':3,
        'source':{'name':stages['generate']['manifest']['source_name'],'pages':stages['generate']['manifest']['pages'],'sha256':stages['generate']['manifest']['source_sha256']},
        'calls':ledger['calls'],'token_count_calls':ledger['token_count_calls'],
        'problems':stages['generate']['expanded'],'compact_generated':stages['generate']['parsed'],
        'blind':stages['blind']['parsed'],'audit':stages['audit']['parsed'],
        'manual_notes':{'2':{'severity':'critical','text':'Локальна перевірка виявила пропущену помилку. Правильно: \\(\\frac{x^2-1}{x}=x-\\frac1x\\). Генератор додав зайву одиницю. При \\(x=2\\) зліва \\(3/2\\), а в його спрощенні \\(5/2\\). GPT‑4.1 помилково схвалила цей крок. У сліпому розборі перевіряльник також помилково стверджував, що функції збігаються на спільній області; при \\(x=2\\) їх значення дорівнюють \\(1\\) і \\(3/2\\). Висновок про нерівність функцій правильний, проте обидва пояснення містять помилки.'}},
        'manual_review':'Перевірено обчислення скінченного образу; задачу 2 спростовано точною раціональною підстановкою; для задачі 3 перевірено простий аргумент ін’єктивності; для задачі 4 — цілочисельний прообраз і недосяжну ціль (1,0). Новизна не підтверджена: оцінювач назвав зміну множини/правила змістовною, хоча цього недостатньо за умовами промпту.',
        'limitations':'Один набір із 4 задач, без автоматичних виправлень. Два етапи виконані тією самою GPT‑4.1 у різних запитах. Це не оцінка надійності всіх моделей і не доказ правильності прийнятих відповідей.',
        'evidence_url':'experiments/review-four/result.json',
        'prompt_hashes':{name:stage['manifest']['prompt_hashes'] for name,stage in stages.items()},
        'usage':{name:stage['usage'] for name,stage in stages.items()},
        'resolved_models':{name:stage['resolved_model'] for name,stage in stages.items()},
        'production_prompt_hashes':stages['generate']['manifest']['production_prompt_hashes'],
        'prices_source':['https://developers.openai.com/api/docs/models/gpt-4.1-mini','https://developers.openai.com/api/docs/models/gpt-4.1']}
    (ROOT/'result.json').write_text(json.dumps(run,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    # Preserve other published experiments. Browser-local benchmark history is untouched.
    runs=[json.loads(p.read_text(encoding='utf-8')) for p in sorted((PROJECT/'experiments').glob('*/result.json'))]
    runs=[r for r in runs if 'problems' in r and 'audit' in r]
    (PROJECT/'reviews-data.js').write_text('window.MATHPDF_REVIEWS = '+json.dumps(runs,ensure_ascii=False).replace('<','\\u003c')+';\n',encoding='utf-8')
    print(json.dumps({'published_run':run['id'],'tasks':len(run['problems']),'reviewer_accepts':sum(x['decision']=='accept' for x in run['audit']['items']),'local_critical_findings':1,'cost_usd':run['cost_usd']},ensure_ascii=False))


if __name__=='__main__':main()
