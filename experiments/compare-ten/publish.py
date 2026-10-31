"""Publish immutable inputs and both model outputs without API credentials."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def main():
 cases=json.loads((ROOT/'cases.json').read_text(encoding='utf-8'))
 results={k:json.loads((ROOT/'output'/f'{k}.json').read_text(encoding='utf-8')) for k in ['mini','full']}
 assert results['mini']['input_sha256']==results['full']['input_sha256']
 assert results['mini']['prompt_sha256']==results['full']['prompt_sha256']
 scores={}
 for arm,result in results.items():
  items=result['parsed']['items'];assert [x['id'] for x in items]==list(range(1,11))
  scores[arm]={'correct_decisions':sum(x['accept']==c['expected_accept'] for x,c in zip(items,cases)),
    'detected_invalid':sum(not x['accept'] and not c['expected_accept'] for x,c in zip(items,cases)),
    'false_accepts':sum(x['accept'] and not c['expected_accept'] for x,c in zip(items,cases)),
    'false_rejects':sum(not x['accept'] and c['expected_accept'] for x,c in zip(items,cases))}
 run={'id':'compare-ten-2026-10-31','date':'2026-10-31','cases':cases,'results':results,'scores':scores,
 'cost_usd':sum(x['cost_usd'] for x in results.values()),
 'explanation_notes':{'full:1':'Рішення відхилити правильне, але пояснення містить дві хибні альтернативи спрощення: x+1−1 і x−1+1/x. Правильно x−1/x. Наведена далі перевірка множенням правильна. Отже, 10/10 рішень не означає 10 безпомилкових пояснень.',
 'mini:10':'Хибне схвалення: модель стверджує, що кожний аргумент зустрічається рівно раз, хоча 0 має значення 1 та 2.'},
 'method':'10 вручну підготовлених контрольних задач за темою функцій із конспекту: 5 правильних і 5 з навмисними помилками. Еталон зафіксовано до запитів; моделі не отримували його чи частку помилок. Однакові умови, розв’язки, порядок, промпт і схема, temperature=0, ліміт 3000 output tokens. Один пакет із 10 задач на модель, 2 платні виклики, без повторів і виправлень. PDF не надсилався; відповідність джерелу та якість генерації не оцінювались.',
 'limitations':'Малий підібраний набір, один прогін, спільний контекст десяти задач. Це порівняння рішень на цьому наборі, не загальна точність і не доказ переваги на всіх задачах. Пояснення переглянуто вручну; автоматично оцінено лише булеві рішення. Попередні тести не змішані з цими результатами.'}
 raw=json.dumps(run,ensure_ascii=False,indent=2)+'\n'
 (ROOT/'result.json').write_text(raw,encoding='utf-8')
 (ROOT.parents[1]/'comparison-data.js').write_text('window.MATHPDF_COMPARISON = '+json.dumps(run,ensure_ascii=False).replace('<','\\u003c')+';\n',encoding='utf-8')
 print(json.dumps({'scores':scores,'cost_usd':run['cost_usd']}))
if __name__=='__main__':main()
