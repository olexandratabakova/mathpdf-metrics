"""Build v5 evidence from the real one-call plan and deterministic artifacts."""
import hashlib,json
from pathlib import Path
from engine import verify_artifact
ROOT=Path(__file__).resolve().parent
def main():
    raw=json.loads((ROOT/'output/response.json').read_text(encoding='utf-8'))
    assert raw['status']=='completed' and len(raw['items'])==10
    for x in raw['items']:verify_artifact({k:v for k,v in x.items() if k!='id'})
    checks=ROOT/'rendering-checks.json'
    rendering=json.loads(checks.read_text()) if checks.exists() else {'status':'pending','math_blocks':sum(b['kind']=='math' for x in raw['items'] for b in x['question']+x['answer']),'fallbacks':None}
    run={'id':'problems-v5-2026-10-31','date':'2026-10-31','version':'v5','kind':'parameterized_problems',
      'summary':'Математика належить програмі: 10 числових варіантів підтримуваних типів. Формули й розв’язки побудовано детерміновано; друга модель не перевіряє.',
      'method':'Кураторський каталог із 10 типів на основі main (12).pdf, стор. 63–66. Mini одним запитом обрала порядок і назви, не отримувала права змінювати формули. Програма з фіксованим seed підставила допустимі числа, побудувала умови, кодомени та повні розв’язки. Виконано точні перевірки обмежень, коефіцієнтів, скінченних образів та оберненої цілої матриці. Контракт артефакту відхиляє зміни формул після побудови.',
      'limitations':'Це закриті, вручну підготовлені й переглянуті шаблони, а не довільні задачі з будь-якого PDF. Частина типів — спеціалізації або перекомбінації прикладів, не механічна заміна кожного числа. Складність і новизна не оцінювались. Програмні перевірки не є універсальним доведенням довільного тексту. Помилка в самому шаблоні можлива. MathPDF і його промпти не змінено; v5 існує тільки як експеримент на метриках.',
      'findings':'На відміну від попереднього циклу, LLM не може вивести формули у звичайний текст чи самовільно змінити кодомен: ці поля створює програма. Усі 10 артефактів пройшли перевірки підтримуваних сімейств. Це інша схема генерації, тому її 10/10 не можна напряму порівнювати з оцінками LLM або вважати доведеною загальною точністю.',
      'validation_summary':'Тести включають відмову для недопустимих параметрів, невідомих типів і навмисно змінених формул/кодоменів. Усі 10 фінальних задач переглянуто вручну; друга модель не викликалася.',
      'verified':10,'reviewer_calls':0,'generation_calls':1,'items':raw['items'],'rendering':rendering,
      **{k:raw[k] for k in ['cost_usd','model','usage','seed','plan','raw_output','prompt_sha256','catalog_sha256']},
      'source':{'name':'main (12).pdf','pages':[63,64,65,66],'sha256':hashlib.sha256(Path('C:/Users/kotya/Downloads/main (12).pdf').read_bytes()).hexdigest()},
      'engine_sha256':hashlib.sha256((ROOT/'engine.py').read_bytes()).hexdigest()}
    run['offline_validation_note']=raw.get('offline_validation_note','')
    run['manual_review']=json.loads((ROOT/'manual-review.json').read_text(encoding='utf-8'))
    (ROOT/'result.json').write_text(json.dumps(run,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (ROOT.parents[1]/'parameterized-data.js').write_text('window.MATHPDF_PARAMETERIZED = '+json.dumps(run,ensure_ascii=False).replace('<','\\u003c')+';\n',encoding='utf-8')
    print(json.dumps({'verified':10,'cost_usd':run['cost_usd'],'rendering':rendering}))
if __name__=='__main__':main()
