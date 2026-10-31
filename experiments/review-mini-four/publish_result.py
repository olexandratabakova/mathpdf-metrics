"""Sanitize the isolated mini experiment; no API requests."""
import json
from pathlib import Path
from fractions import Fraction
ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]
def main():
 stages={n:json.loads((ROOT/'output'/f'{n}.json').read_text(encoding='utf-8')) for n in ['generate','blind','audit']}
 ledger=json.loads((ROOT/'output/ledger.json').read_text())
 assert all(s['status']=='completed' for s in stages.values())
 run=json.loads((PROJECT/'experiments/review-four/result.json').read_text(encoding='utf-8'))
 run.update(id='review-mini-four-2026-10-31',date='2026-10-31',title='4 нові задачі · mini → окрема перевірка mini',
 summary='Mini прийняла 3 задачі й відправила 1 на доопрацювання. Помітила хибну бієктивність, проте пропустила суперечливу область визначення та сама помилилася в обґрунтуванні.',
 cost_usd=sum(c['cost_usd'] for c in ledger['calls']),calls=ledger['calls'],token_count_calls=ledger['token_count_calls'],
 problems=stages['generate']['expanded'],compact_generated=stages['generate']['parsed'],blind=stages['blind']['parsed'],audit=stages['audit']['parsed'],
 evidence_url='experiments/review-mini-four/result.json',
 manual_notes={'3':{'severity':'critical','text':r'Умова одночасно задає \(f:\mathbb Z\to\mathbb Z\) і область \(\mathbb Z^2\) для \(f(m,n)=m-2n\). Потрібно виправити тип функції. Для області пар сюр’єктивність правильна: прообраз будь-якого \(z\) — \((z,0)\). Аудит прийняв умову без зауважень. Сліпа перевірка позначила її false_claim, але в поясненні сама змінила «не сюр’єктивна» на «сюр’єктивна», не пояснивши суперечності області.'},
 '4':{'severity':'critical','text':r'Хибну вимогу довести бієктивність модель виявила правильно. Проте у сліпому обґрунтуванні для цілі \((1,0)\) вона дала \((0,1/3)\): цей вектор відображається в \((1/3,1)\). Правильний розв’язок над раціональними — \((3/5,-1/5)\), що також доводить недосяжність цілі в цілих. Аудит цю помилку попереднього розбору не виправив. Водночас оригінальний розв’язок генератора вже визнає відсутність сюр’єктивності, тому закид аудиту, ніби він ігнорує цілочисельність, неточний.'}},
 manual_review='Локально перевірено визначення, доказ ін’єктивності, конструктивний прообраз (z,0), визначник 5 і раціональний прообраз (3/5,-1/5). Перша задача — відтворення визначення, друга — проста зміна коефіцієнтів; бажана складність і новизна не забезпечені.',
 limitations='Новий набір, а не повторна оцінка попередніх задач: напряму порівнювати точність моделей не можна. Усі 3 етапи — GPT‑4.1 mini в окремих запитах; аудит бачить попередню сліпу перевірку. 4 задачі, без автоматичних виправлень; не статистична оцінка надійності.')
 run['source']={'name':stages['generate']['manifest']['source_name'],'pages':[63,64,65,66],'sha256':stages['generate']['manifest']['source_sha256']}
 for field,key in [('prompt_hashes','manifest'),('usage',None),('resolved_models','resolved_model')]:
  run[field]={n:(s['manifest']['prompt_hashes'] if field=='prompt_hashes' else s['usage'] if field=='usage' else s['resolved_model']) for n,s in stages.items()}
 run['production_prompt_hashes']=stages['generate']['manifest']['production_prompt_hashes']
 assert Fraction(3,5)*2-Fraction(1,5)==1
 assert Fraction(3,5)-3*Fraction(1,5)==0
 (ROOT/'result.json').write_text(json.dumps(run,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 runs=[json.loads(p.read_text(encoding='utf-8')) for p in sorted((PROJECT/'experiments').glob('*/result.json'))]
 (PROJECT/'reviews-data.js').write_text('window.MATHPDF_REVIEWS = '+json.dumps(runs,ensure_ascii=False).replace('<','\\u003c')+';\n',encoding='utf-8')
 print(run['cost_usd'])
if __name__=='__main__':main()
