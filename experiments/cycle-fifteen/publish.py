"""Publish the real four-stage cycle without source PDFs or credentials."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def main():
    stages={n:json.loads((ROOT/'output'/f'{n}.json').read_text(encoding='utf-8')) for n in ['generate','review','fix','final']}
    ledger=json.loads((ROOT/'output/ledger.json').read_text())
    assert all(s['status']=='completed' and 'parsed' in s for s in stages.values())
    before=stages['generate']['parsed']['result']['items'];after=stages['fix']['parsed']['result']['items']
    assert len(before)==len(after)==15
    review=stages['review']['parsed'];final=stages['final']['parsed']
    assert [x['id'] for x in review['items']]==[x['id'] for x in final['items']]==list(range(1,16))
    def count_objects(items):
        def walk(x):
            if isinstance(x,dict):return int('math' in x or 'latex' in x)+sum(walk(v) for v in x.values())
            if isinstance(x,list):return sum(walk(v) for v in x)
            return 0
        return walk(items)
    local=json.loads((ROOT/'local-review.json').read_text(encoding='utf-8'))
    changed=[i for i,(a,b) in enumerate(zip(before,after),1) if a!=b]
    run={'id':'cycle-fifteen-2026-10-31','date':'2026-10-31','kind':'repair_cycle',
      'summary':'Модельне схвалення зросло з 14/15 до 15/15. Локальна перевірка: математично коректних залишилося 14/15 — помилковий кодомен не виправлено. Правильну задачу 9 замінили через хибну критику.',
      'cost_usd':sum(x['cost_usd'] for x in ledger['calls']),'calls':ledger['calls'],
      'before':stages['generate']['expanded'],'after':stages['fix']['expanded'],
      'compact_before':before,'compact_after':after,'review':review,'final':final,'changed_ids':changed,
      'metrics':{'before_accepts':sum(x['accept'] for x in review['items']),'after_accepts':sum(x['accept'] for x in final['items']),
       'changed':len(changed),'before_formula_issues':sum(x['formula_issue'] for x in review['items']),
       'after_formula_issues':sum(x['formula_issue'] for x in final['items']),
       'local_before_correct':sum(x['before_correct'] for x in local['items']),
       'local_after_correct':sum(x['after_correct'] for x in local['items']),
       'structured_math_before':count_objects(before),'structured_math_after':count_objects(after)},
      'local_review':local,
      'local_summary':'Усі 15 задач переглянуто локально. До: 14 математично коректних, 1 хибна. Після: ті самі 14/15. У задачі 13 h(2)=2 суперечить кодомену R без 2; ціль 1 недосяжна. Обидві перевірки помилково схвалили її. Задача 9 спочатку мала правильний доказ, але перевіряльник відхилив його без справжнього контрприкладу; mini замінила її прикладом із конспекту.',
      'local_notes':{
       '9':r'Оригінальна функція \((2m+n,m+3n)\) ін’єктивна: з рівності виходів випливає \(5n=5b\), отже \(n=b\) і \(m=a\). Перевіряльник помилково відхилив це доведення; наведені ним виходи \((2,6)\) і \((1,-2)\) різні й не спростовують ін’єктивність. Mini замінила правильний приклад на \((m+n,m+2n)\) із джерела. Це не виправлення математичної помилки.',
       '13':r'Не виправлено. Заявлено \(h:\mathbb R\setminus\{0\}\to\mathbb R\setminus\{2\}\), \(h(x)=2/x+1\), але \(h(2)=2\) — вихід поза кодоменом. Також \(1\) належить заявленому кодомену, але не має прообразу. Припущення \(y\ne1\) у розв’язку не випливає з \(y\ne2\). Обидва звіти прийняли помилку. Локальне можливе виправлення — кодомен R без 1; воно НЕ застосоване до модельного результату.'},
      'rendering_summary':'Явні math/latex-об’єкти: 124 → 0; окремі формульні блоки в рендерері: 25 → 0. Після ремонту модель перетворила їх на текстові рядки, тому рендерер відновлює TeX евристично. До й після — 0 технічних math-fallback, але це не підтверджує покращення формул. Формати й окремі рядки переглянуто в браузері; покращення запису не встановлено.',
      'method':'Конспект main (12).pdf, оригінальні стор. 63–66, 15 задач, рівень 3. Заморожений кандидат промптів. Mini генерує; GPT‑4.1 перевіряє оригінали; mini отримує оригінали й звіт для одного ремонту; GPT‑4.1 перевіряє фінал новим запитом з тим самим промптом і PDF, без оригіналів та попередньої критики. Локальні знахідки не передавалися моделям.',
      'limitations':'Один набір і один цикл, без повторних платних спроб. Контроль виконує та сама модель в окремому контексті, тому помилки можуть повторюватися. Це не вимірювання загальної точності. Новизна, різноманітність і рівень набору не підтверджені; частина задач повторює конспект. MathPDF не змінено.',
      'source':{'name':stages['generate']['manifest']['source_name'],'pages':[63,64,65,66],'sha256':stages['generate']['manifest']['source_sha256']},
      'usage':{n:s['usage'] for n,s in stages.items()},'models':{n:s['resolved_model'] for n,s in stages.items()},
      'prompt_hashes':{n:s['manifest']['prompt_hashes'] for n,s in stages.items()},
      'production_prompt_hashes':stages['generate']['manifest']['production_prompt_hashes'],
      'stage_tasks':{n:s['manifest']['task'] for n,s in stages.items()},
      'review_prompt_identical':stages['review']['manifest']['instructions']==stages['final']['manifest']['instructions'],
      'rendering_checks':json.loads((ROOT/'rendering-checks.json').read_text())}
    (ROOT/'result.json').write_text(json.dumps(run,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (ROOT.parents[1]/'cycle-data.js').write_text('window.MATHPDF_CYCLE = '+json.dumps(run,ensure_ascii=False).replace('<','\\u003c')+';\n',encoding='utf-8')
    print(json.dumps({'cost_usd':run['cost_usd'],'metrics':run['metrics']}))
if __name__=='__main__':main()
