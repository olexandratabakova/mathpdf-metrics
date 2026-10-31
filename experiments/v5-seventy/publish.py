"""Publish seventy program-built tasks without PDFs, private request data or secrets."""
from collections import Counter
import hashlib,json
from pathlib import Path
from engine import TOPICS,META,verify_artifact
ROOT=Path(__file__).resolve().parent
def main():
    raw=json.loads((ROOT/'output/response.json').read_text(encoding='utf-8'))
    assert raw['status']=='completed' and len(raw['items'])==70
    for x in raw['items']:verify_artifact(x)
    counts=Counter(x['topic'] for x in raw['items']);assert counts=={t:10 for t in TOPICS}
    checks=ROOT/'rendering-checks.json'
    rendering=json.loads(checks.read_text()) if checks.exists() else {'status':'pending','math_blocks':sum(b['kind']=='math' for x in raw['items'] for b in x['question']+x['answer']),'fallbacks':None}
    run={'id':'problems-v5-seventy-2026-10-31','date':'2026-10-31','version':'v5','kind':'multi_topic_parameterized',
      'summary':'70 числових варіантів у 7 темах: 40 підтримуваних сімейств, по 10 задач на тему. Математику будує й перевіряє програма; другої моделі немає.',
      'topics':[{'id':t,'name':TOPICS[t],'count':counts[t],'families':len({x['template_id'] for x in raw['items'] if x['topic']==t})} for t in raw['plan']['topic_order']],
      'verified':70,'families':40,'items':raw['items'],'rendering':rendering,'generation_calls':1,'reviewer_calls':0,
      **{k:raw[k] for k in ['cost_usd','model','usage','seed','plan','raw_output','prompt_sha256','input_sha256']},
      'method':'Кураторські шаблони з main (12).pdf: множини (5–7), індукція (14–17), числа (27–31), конгруенції (33–34), комбінаторика (38–43), принцип Діріхле (60–62), функції (63–66). Один виклик mini обрав лише порядок тем. Числа, формули, умови й повні розв’язки створено програмою, seed 50770. Для шести нових тем — по 5 сімейств і 2 числових варіанти, для функцій — 10 сімейств.',
      'validation':'Точна арифметика цілих і раціональних чисел; повний скінченний перебір множин, залишків, виборів і розподілів; незалежне множення поліномів; перевірка оберненої цілої матриці. Індукція: база та алгебраїчні сертифікати переходів, а не лише перші значення. Для принципу Діріхле — перевірені кураторські доведення, межі, екстремальні конструкції та обчислені свідки. Структура артефакту відхиляє сторонні зміни формул. Універсальний математичний текст не перевіряється.',
      'limitations':'70 варіантів — не 70 різних типів і не вимірювання точності довільної LLM-генерації. Шаблони підготовлено й переглянуто вручну; помилка у шаблоні все ще можлива. Це не формально перевірені Lean/Coq-доведення. Новизна, рівень складності й педагогічна якість не оцінювались. Непідтримувані типи відхиляються. MathPDF і його промпти не змінено.',
      'review_notes':'Переглянуто всі 40 сімейств, джерела й 70 наборів параметрів. Довгі списки залишків розбито на короткі формульні рядки. Виявлену неточність номера теореми факторизації виправлено локально до публікації; математичні відповіді не змінювалися й повторного API-виклику не було.',
      'source':{'name':'main (12).pdf','pages':sorted({x['source']['page'] for x in raw['items']}),'sha256':hashlib.sha256(Path('C:/Users/kotya/Downloads/main (12).pdf').read_bytes()).hexdigest()},
      'engine_sha256':hashlib.sha256((ROOT/'engine.py').read_bytes()).hexdigest(),
      'reused_engine_sha256':hashlib.sha256((ROOT.parent/'v5-parameterized/engine.py').read_bytes()).hexdigest()}
    (ROOT/'result.json').write_text(json.dumps(run,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (ROOT.parents[1]/'seventy-data.js').write_text('window.MATHPDF_SEVENTY = '+json.dumps(run,ensure_ascii=False).replace('<','\\u003c')+';\n',encoding='utf-8')
    print(json.dumps({'tasks':70,'families':40,'cost_usd':run['cost_usd'],'rendering':rendering}))
if __name__=='__main__':main()
