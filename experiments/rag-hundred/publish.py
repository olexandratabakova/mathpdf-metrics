"""Publish one hundred attempted variants with the original rejection preserved."""
from collections import Counter
import hashlib,json
from pathlib import Path
import engine as E
import retrieval as R
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'output'
def main():
    frozen=json.loads((OUT/'retrieval-before-model.json').read_text(encoding='utf-8'))
    raw=json.loads((OUT/'response.json').read_text(encoding='utf-8'))
    repair=json.loads((OUT/'repair-response.json').read_text(encoding='utf-8'))
    repair_ctx=json.loads((OUT/'repair-retrieval.json').read_text(encoding='utf-8'))
    assert raw['status']==repair['status']=='completed'
    profiles=[];tasks=[];first_accepted=0
    for context,original in zip(frozen['retrieval'],raw['plan']['items']):
        req=context['request'];initial=context['retrieved']['matches'];initial_ok=original['template_id'] in [m['id'] for m in initial]
        first_accepted+=initial_ok
        chosen=original;matches=initial;repaired=False
        if req['id']==repair['choice']['id']:
            assert not initial_ok
            chosen=repair['choice'];matches=repair_ctx['retrieved']['matches'];repaired=True
        accepted=chosen['template_id'] in [m['id'] for m in matches]
        goal_match=chosen['template_id'] in req['expected']
        def compact(ms):return [{'id':m['id'],'score':m['score'],'sources':m['doc']['sources']} for m in ms]
        profiles.append({'id':req['id'],'goal':req['goal'],'topic':req['topic'],'domain':req['domain'],'available':req['available'],
          'expected':req['expected'],'sources':req['sources'],'original_ranking':compact(initial),'final_ranking':compact(matches),
          'original_choice':original,'original_in_context':initial_ok,'final_choice':chosen,'accepted':accepted,'goal_match':goal_match,'repaired':repaired})
        if not accepted:
            for v in [0,1]:tasks.append({'id':2*(req['id']-1)+v+1,'profile_id':req['id'],'status':'blocked','artifact':None})
            continue
        artifacts,draws=R.compile_variants(chosen['template_id'],req['id'])
        for v,(artifact,draw) in enumerate(zip(artifacts,draws)):
            E.verify(artifact)
            tasks.append({'id':2*(req['id']-1)+v+1,'profile_id':req['id'],'variant':v,'status':'generated' if goal_match else 'goal_mismatch',
              'draw':draw,'artifact':artifact,'source_support':req['sources']})
    assert [x['id'] for x in tasks]==list(range(1,101))
    metrics={'profiles':50,'task_attempts':100,'first_pass_in_context_profiles':first_accepted,'first_pass_task_accepts':first_accepted*2,
      'initial_top1_hits':sum(p['original_ranking'][0]['id'] in p['expected'] for p in profiles),
      'initial_top3_hits':sum(any(d['id'] in p['expected'] for d in p['original_ranking'][:3]) for p in profiles),
      'initial_top5_hits':sum(any(d['id'] in p['expected'] for d in p['original_ranking']) for p in profiles),
      'final_goal_matches':sum(p['goal_match'] for p in profiles),'final_generated':sum(t['status']=='generated' for t in tasks),
      'program_verified':sum(t['artifact'] is not None and E.verify(t['artifact']) for t in tasks),
      'repaired_profiles':sum(p['repaired'] for p in profiles),'new_families':13,'reused_families':37}
    rendering_path=ROOT/'rendering-checks.json'
    run={'id':'rag-hundred-2026-10-31','date':'2026-10-31','kind':'two_document_retrieval_compilation',
      'summary':'100 варіантів із 50 підтримуваних сімейств у 10 темах. Нові PDF переглядалися лише за змістом і вибраними сторінками. Початковий збій пошуку й коротку повторну спробу збережено.',
      'metrics':metrics,'profiles':profiles,'tasks':tasks,'sources':frozen['sources'],'controls':frozen['controls'],
      'topics':[{'id':topic,'name':E.TOPICS[topic],'tasks':count} for topic,count in Counter(t['artifact']['topic'] for t in tasks if t['artifact']).items()],
      'cost_usd':raw['cost_usd']+repair['cost_usd'],'model':raw['model'],'reviewer_calls':0,'generation_plan_calls':2,
      'usage':{'main':raw['usage'],'repair':repair['usage']},'costs':{'main':raw['cost_usd'],'repair':repair['cost_usd']},
      'original_plan':raw['plan'],'repair_plan':repair['choice'],'raw_outputs':{'main':raw['raw_output'],'repair':repair['raw_output']},
      'expected_labels_sent':False,'full_pdf_uploaded':False,
      'method':'Пошук тем через зміст/закладки, потім тільки цільові сторінки main (13).pdf і Book of Proof (Main (10).pdf). Банк — 37 попередніх сімейств плюс 13 нових: логіка, відношення, часткові порядки, парність/монотонність/домен функцій. Профілі й передумови ручні. Фільтри теми/домену/передумов → BM25 top‑5 → модель обирає структуру → програма створює два різні допустимі варіанти з повними розв’язками. Математичний текст не пишеться вільною LLM.',
      'retrieval_note':'Перший пошук: очікуваний тип на першій позиції 44/50, у top‑3 і top‑5 — 49/50. Для одного запиту потрібний запис мав нульовий лексичний бал через словоформи й синоніми. Модель назвала його поза дозволеними кандидатами; перевірка відхилила 2 заплановані варіанти. Після загальної нормалізації словоформ/синонімів лише цей запит повторено з новим контекстом. Первинний результат не переписано.',
      'source_note':'Посилання Book of Proof часто підтверджують означення або метод, а не означають дослівну копію його вправи. Первинні 37 сімейств були кураторськими ще до цього тесту. Розширено новими сімействами за вибраними сторінками двох файлів; це не повністю автоматичне навчання на книзі. Текст сторінок і повні PDF не публікуються.',
      'limits':'100 варіантів — не 100 різних типів. Це обмежений RAG із програмним компілятором і ручними профілями, не перевірка довільних доведень. Програмні перевірки спираються на правильність шаблонів і власних адаптерів; вони не є Lean/Coq-сертифікатами. Автоматичне вилучення довільного нового сімейства, усі теми книги та всі матеріали конспекту не перевірені. MathPDF не змінено.',
      'rendering':json.loads(rendering_path.read_text()) if rendering_path.exists() else {'status':'pending'},
      'hashes':{'engine':hashlib.sha256((ROOT/'engine.py').read_bytes()).hexdigest(),'retrieval':hashlib.sha256((ROOT/'retrieval.py').read_bytes()).hexdigest(),'main_prompt':raw['prompt_sha256'],'repair_prompt':repair['prompt_sha256']}}
    bank=[{k:d[k] for k in ['id','topic','domain','requires','text','sources','revision','example']} for d in frozen['bank']]
    (ROOT/'bank.json').write_text(json.dumps(bank,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (ROOT/'result.json').write_text(json.dumps(run,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (ROOT.parents[1]/'hundred-data.js').write_text('window.MATHPDF_HUNDRED = '+json.dumps(run,ensure_ascii=False).replace('<','\\u003c')+';\n',encoding='utf-8')
    print(json.dumps({'metrics':metrics,'cost_usd':run['cost_usd']}))
if __name__=='__main__':main()
