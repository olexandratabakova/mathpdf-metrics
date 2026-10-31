"""Sanitized original LLM tasks + unchanged SymPy results + separate local findings."""
from collections import Counter
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def main():
    checks=json.loads((ROOT/'output/checks.json').read_text(encoding='utf-8'))
    ledger=json.loads((ROOT/'output/ledger.json').read_text())
    raw={g:json.loads((ROOT/'output'/f'{g}.json').read_text(encoding='utf-8')) for g in ['near','transfer','near2','transfer2']}
    assert len(checks['near2'])==40 and len(checks['transfer2'])==15
    for group,items in checks.items():assert [x['task'] for x in items]==raw[group]['parsed']['items']
    rendering_path=ROOT/'rendering-checks.json'
    run={'id':'sympy-55-2026-10-31','date':'2026-10-31','kind':'symbolic_library_experiment','library':'SymPy 1.14.0',
      'groups':[{'id':g,'name':name,'items':checks[g],'counts':dict(Counter(x['check']['status'] for x in checks[g]))} for g,name in [('near2','40 близьких аналогів — вихід моделі'),('transfer2','15 запитаних змін умов — вихід моделі')]],
      'counts':dict(Counter(x['check']['status'] for items in checks.values() for x in items)),
      'summary':'Реальна LLM-генерація 40+15 задач. SymPy підтверджує частину формальних обчислень, але не гарантує правильності тексту, формалізації чи загальних доведень.',
      'cost_usd':sum(c['cost_usd'] for c in ledger['calls']),'main_cost_usd':sum(c['cost_usd'] for c in ledger['calls'] if c['group'].endswith('2')),
      'calls':ledger['calls'],'reviewer_calls':0,'model':raw['near2']['model'],
      'manual_notes':json.loads((ROOT/'manual-notes.json').read_text(encoding='utf-8')),
      'local_checks':json.loads((ROOT/'local-checks.json').read_text()),
      'rendering':json.loads(rendering_path.read_text()) if rendering_path.exists() else {'status':'pending'},
      'method':'Цього разу модель сама створила умови, числові дані, формули, розв’язки та окрему формалізацію. Це НЕ попередні детерміновані шаблони v5. Генератор отримав текстові уривки конспекту, а не готові відповіді. Для основних 40 задано типи перевірок; для 15 задано сценарії змін умов. SymPy через обмежені адаптери перерахував формальні записи. Загальні докази не передавалися другій LLM.',
      'scope':'confirmed означає лише підтверджене формальне обчислення і придатні для розбору надані рівності. partial — підтверджено лише арифметику, тотожність або частину кроків. refuted — спростовано саме формальний запис, який може не відповідати тексту. unsupported — чесної перевірки немає: непідтримуваний тип, неправильний формат, нерозв’язаний випадок або ліміт часу. Жоден статус сам по собі не підтверджує весь розв’язок природною мовою.',
      'limitations':'Малий відібраний набір; адаптери не охоплюють усі можливості SymPy. Відповідність тексту формальному запису та джерелу автоматично не доводиться. Є копії прикладів, невиконані зміни умов і неправильні посилання. У 15 запитаних змінах принаймні дві не виконано належним чином: повтор задачі й відсутність потрібного сценарію стороннього кореня. Висновки не є загальною точністю SymPy чи генератора. MathPDF не змінено.',
      'pilot_note':'Два початкові пілотні запити (40+15) часто копіювали конспект і порушували формат. Їх збережено окремо, не змішано з основними 55 задачами. Після уточнення контракту виконано ще два генераційні запити. Усі 4 оплачені запити входять у загальну вартість; бюджет $0.12, без платних перевірок або виправлень.',
      'citation_warnings':{g:raw[g].get('citation_warnings',[]) for g in ['near2','transfer2']},
      'usage':{g:raw[g]['usage'] for g in raw},'prompt_hashes':{g:raw[g]['prompt_sha256'] for g in raw},
      'source':{'name':raw['near2']['source_name'],'pages':raw['near2']['source_pages'],'sha256':raw['near2']['source_sha256']},
      'verifier_sha256':hashlib.sha256((ROOT/'verifier.py').read_bytes()).hexdigest(),
      'reference_docs':['https://docs.sympy.org/latest/guides/solving/solving-guidance.html','https://docs.sympy.org/latest/modules/solvers/solveset.html']}
    pilots={g:{k:raw[g][k] for k in ['group','model','cost_usd','usage','raw_output','parsed','prompt_sha256']} for g in ['near','transfer']}
    (ROOT/'pilots.json').write_text(json.dumps(pilots,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (ROOT/'result.json').write_text(json.dumps(run,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (ROOT.parents[1]/'symbolic-data.js').write_text('window.MATHPDF_SYMBOLIC = '+json.dumps(run,ensure_ascii=False).replace('<','\\u003c')+';\n',encoding='utf-8')
    print(json.dumps({'counts':run['counts'],'cost_usd':run['cost_usd']}))
if __name__=='__main__':main()
