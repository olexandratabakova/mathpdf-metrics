"""Reproducible numerical compilation of a real retrieved-context model plan."""
import hashlib,json
from pathlib import Path
import pipeline as P
ROOT=Path(__file__).resolve().parent
def main():
    raw=json.loads((ROOT/'output/response.json').read_text(encoding='utf-8'))
    frozen=json.loads((ROOT/'output/retrieval-before-model.json').read_text(encoding='utf-8'))
    assert raw['status']=='completed' and not raw['expected_labels_sent']
    constraints={r['id']:r.get('parameter_constraints',{}) for r in json.loads((ROOT/'requests.json').read_text(encoding='utf-8'))}
    rows=[]
    for choice,context in zip(raw['plan']['items'],frozen['requests']):
        req=context['request'];matches=context['retrieval']['matches'];assert choice['id']==req['id']
        selected=next((m for m in matches if m['id']==choice['template_id']),None)
        row={'id':req['id'],'goal':req['goal'],'topic':req['topic'],'theory':context['theory'],'expected':req['expected'],
          'top1_hit':matches[0]['id'] in req['expected'] if matches else False,'top3_hit':any(m['id'] in req['expected'] for m in matches),
          'retrieval':context['retrieval'],'choice':choice,'goal_match':choice['template_id'] in req['expected'],'parameter_constraints':constraints[req['id']]}
        if selected is None:
            row.update(status='no_coverage' if choice['template_id']=='NO_COVERAGE' else 'invalid_selection',item=None)
        else:
            # A new deterministic draw if the first candidate repeats the exact
            # exemplar question. Never overwrite the retrieved example or model plan.
            for attempt in range(100):
                seed_index=req['id']+attempt*1000
                item=P.build_item(choice['template_id'],seed_index,constraints[req['id']]);item['id']=req['id']
                P.E.verify_artifact(item)
                if item['question']!=selected['doc']['example']['question']:break
            else:raise ValueError('Could not create a new numerical variant')
            row.update(status='generated' if row['goal_match'] else 'goal_mismatch',item=item,generation_seed=P.SEED+seed_index,
              different_from_exemplar=True,exemplar_parameters=selected['doc']['example']['parameters'])
        rows.append(row)
    metrics={'requests':15,'top1_hits':sum(r['top1_hit'] for r in rows),'top3_hits':sum(r['top3_hit'] for r in rows),
      'model_goal_matches':sum(r['goal_match'] for r in rows),'generated':sum(r['status']=='generated' for r in rows),
      'program_checks_passed':sum(r['item'] is not None and P.E.verify_artifact(r['item']) for r in rows),
      'negative_controls_refused':sum(c['status']=='no_coverage' for c in frozen['controls'])}
    rendering_file=ROOT/'rendering-checks.json'
    run={'id':'rag-fifteen-2026-10-31','date':'2026-10-31','kind':'retrieval_backed_constrained_generation',
      'summary':'Теорія без прикладів → пошук у банку 40 сімейств → вибір моделі → нові числові варіанти → програмні перевірки. Повний слід для 15 задач.',
      'rows':rows,'metrics':metrics,'controls':frozen['controls'],'cost_usd':raw['cost_usd'],'usage':raw['usage'],'model':raw['model'],
      'plan':raw['plan'],'raw_output':raw['raw_output'],'expected_labels_sent':False,'reviewer_calls':0,'generation_calls':1,
      'method':'Реально виділені фрагменти визначень/теорем із PDF без розв’язаних прикладів. 15 цілей, тем, передумов і очікуваних сімейств кураторські. Окремий банк із 40 раніше перевірених сімейств. Жорсткі фільтри теми, домену й передумов, потім локальний BM25 top‑3. Mini бачить теорію й знайдені приклади з розв’язками та обирає структуру. Математику й числа будує перевірювана програма; LLM не переписує умови або розв’язки.',
      'limitations':'Це пошук із контрольованою генерацією на невеликому кураторському банку, а не вільна RAG-генерація математики. Банк і теорія походять з того самого конспекту; приклади прибрано лише з вхідних фрагментів. Немає тесту на незалежному невідомому курсі. Профілі й цілі задано вручну, англомовний пошук не тестувався на перефразуваннях. У двох запитах фільтри залишили єдиного кандидата. 15/15 не є загальною точністю RAG чи гарантією відсутності помилок у шаблонах. MathPDF не змінено.',
      'profile_fix':'Після вибору моделі вимогу «negative dividend», яка вже була в замороженій цілі запиту 5, додано як явне програмне обмеження. Перший локальний параметр був додатним; фінальний компілятор примусово зберігає від’ємність. Запит, очікуваний тип, пошук і вибір моделі не змінювалися; нового API-виклику не було.',
      'rendering':json.loads(rendering_file.read_text()) if rendering_file.exists() else {'status':'pending'},
      'bank_sha256':frozen['bank_sha256'],'frozen_requests_sha256':frozen['requests_sha256'],
      'current_requests_sha256':P.hashjson(json.loads((ROOT/'requests.json').read_text(encoding='utf-8'))),
      'prompt_sha256':raw['prompt_sha256'],'model_input_sha256':raw['model_input_sha256'],
      'pipeline_sha256':hashlib.sha256((ROOT/'pipeline.py').read_bytes()).hexdigest(),
      'source':{'name':'main (12).pdf','sha256':hashlib.sha256(Path('C:/Users/kotya/Downloads/main (12).pdf').read_bytes()).hexdigest()},
      'algorithm_steps':[
       {'title':'Профіль конспекту','text':'Виділити теорію, тему, доступні методи, області чисел, припущення й оригінальні сторінки. Не домислювати передумови. У прототипі профілі ручні, фрагменти реально виділено з PDF.'},
       {'title':'Окремий банк прикладів','text':'Зберігати перевірені умови, розв’язки, домени, передумови, допустимі зміни чисел, перевіряльник і версію. Зараз банк має 40 сімейств.'},
       {'title':'Жорстка сумісність','text':'Спочатку відсікти неправильну тему, домен або відсутні передумови. Приклад над R не заміняє задачу над Z.'},
       {'title':'Пошук top‑3','text':'Серед сумісних кандидатів ранжувати за ціллю й методом. У тесті BM25 без embeddings. Бал пошуку не означає правильність.'},
       {'title':'Вибір структури моделлю','text':'Передати теорію й знайдені приклади, а не весь PDF. Модель обирає лише серед знайдених або відмовляється; очікувані тестові відповіді приховані.'},
       {'title':'Одна формальна основа','text':'Програма обирає допустимі числа та з одного запису будує умову, формули й відповідь. Зберігає всі обмеження; поза підтримуваним типом не ставить «перевірено».'},
       {'title':'Три окремі перевірки','text':'Оцінити відповідність цілі, математичні обмеження та рендеринг. Для індукції перевіряти базу й перехід, а не лише перші числа.'},
       {'title':'Походження й чесна відмова','text':'Зберігати сторінки теорії, знайдений приклад, причину вибору, змінені числа, перевірки й витрати. Якщо немає покриття — не вигадувати підтверджену задачу.'}]}
    (ROOT/'bank.json').write_text(json.dumps(P.bank(),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (ROOT/'result.json').write_text(json.dumps(run,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (ROOT.parents[1]/'rag-data.js').write_text('window.MATHPDF_RAG = '+json.dumps(run,ensure_ascii=False).replace('<','\\u003c')+';\n',encoding='utf-8')
    print(json.dumps({'metrics':metrics,'cost_usd':run['cost_usd']}))
if __name__=='__main__':main()
