window.renderCycle = function () {
  const run = window.MATHPDF_CYCLE;
  if (!run) return;
  const verdict = x => x.accept ? 'Прийняти' : 'Виправити';
  const section = document.createElement('section');
  section.id = run.id;
  section.className = 'experiment-run';
  section.innerHTML = `<div class="panel experiment-intro"><div><span class="eyebrow">${esc(run.date)} · ГЕНЕРАЦІЯ → ПЕРЕВІРКА → ВИПРАВЛЕННЯ</span><h2>15 задач: до та після виправлення</h2><p>${esc(run.summary)}</p><div class="experiment-flow"><span>Mini <small>генерує 15</small></span><b>→</b><span>GPT‑4.1 <small>перевіряє</small></span><b>→</b><span>Mini <small>виправляє</small></span><b>→</b><span>GPT‑4.1 <small>новий контроль</small></span></div></div><div class="experiment-cost"><strong>$${run.cost_usd.toFixed(5)}</strong><span>4 виклики · один цикл</span><a href="experiments/cycle-fifteen/result.json" target="_blank" rel="noreferrer">JSON результатів ↗</a></div></div>
  <div class="summary-grid">${summary('Модель прийняла до', run.metrics.before_accepts+'/15', 'Висновок моделі, не еталон', true)}${summary('Модель прийняла після', run.metrics.after_accepts+'/15', 'Новий запит без попереднього звіту')}${summary('Змінено задач', String(run.metrics.changed), 'Порівняно повний вміст полів')}${summary('Локально коректних', run.metrics.local_before_correct+' → '+run.metrics.local_after_correct, 'Із 15 задач; помилка залишилася')}</div>
  <div class="note">${esc(run.method)} ${esc(run.limitations)}</div>
  <section class="panel"><div class="panel-heading"><h2>Порівняння кожної задачі</h2></div><div class="table-scroll"><table><thead><tr><th>№</th><th>ЗАДАЧА</th><th>ДО: МОДЕЛЬ</th><th>ПІСЛЯ: МОДЕЛЬ</th><th>ЗМІНЕНО</th></tr></thead><tbody>${run.before.map((x,i)=>`<tr><td>${i+1}</td><td>${esc(x.title)}</td><td><span class="tag ${run.review.items[i].accept?'':'warn'}">${verdict(run.review.items[i])}</span></td><td><span class="tag ${run.final.items[i].accept?'':'red'}">${verdict(run.final.items[i])}</span></td><td>${run.changed_ids.includes(i+1)?'Так':'Ні'}</td></tr>`).join('')}</tbody></table></div></section>
  <section class="panel"><div class="panel-heading"><h2>Окремий локальний аналіз</h2></div><div class="panel-body"><p>${esc(run.local_summary)}</p><p>${esc(run.rendering_summary)}</p></div></section>
  ${run.before.map((x,i)=>`<article class="panel experiment-problem cycle-problem"><span class="eyebrow">ЦИКЛ · ЗАДАЧА ${i+1}</span><h2>${esc(x.title)}</h2><details><summary>До: оригінальна умова та розв’язок</summary><div class="report-math" data-cycle="before:${i}:question"></div><div class="report-math" data-cycle="before:${i}:answer"></div></details><details><summary>Перша перевірка: ${verdict(run.review.items[i])}</summary><div class="review-prose" data-cycle-review="review:${i}:explanation"></div><div class="review-prose" data-cycle-review="review:${i}:suggested_fix"></div></details><details><summary>Після: ${run.changed_ids.includes(i+1)?'змінена':'незмінена'} умова та розв’язок</summary><div class="report-math" data-cycle="after:${i}:question"></div><div class="report-math" data-cycle="after:${i}:answer"></div></details><details><summary>Контроль після: ${verdict(run.final.items[i])}</summary><div class="review-prose" data-cycle-review="final:${i}:explanation"></div><div class="review-prose" data-cycle-review="final:${i}:suggested_fix"></div></details>${run.local_notes[String(i+1)]?`<div class="manual-finding"><strong>Локальний аналіз.</strong><div class="review-prose" data-cycle-local="${i+1}"></div></div>`:''}</article>`).join('')}
  <section class="panel"><div class="panel-heading"><h2>Витрати циклу</h2></div><div class="table-scroll"><table><thead><tr><th>ЕТАП</th><th>МОДЕЛЬ</th><th>INPUT</th><th>OUTPUT</th><th>USD</th></tr></thead><tbody>${run.calls.map(c=>`<tr><td>${esc({generate:'Генерація',review:'Перевірка',fix:'Виправлення',final:'Контроль'}[c.stage])}</td><td>${esc(c.model)}</td><td>${c.input_tokens}</td><td>${c.output_tokens}</td><td>$${c.cost_usd.toFixed(6)}</td></tr>`).join('')}</tbody></table></div></section>`;
  document.querySelector('main').prepend(section);
  const options={editable:false,linkSources:false,sourceLabel:ref=>`main (12).pdf · стор. ${ref.page}`};
  for(const node of section.querySelectorAll('[data-cycle]')) {
    const [side,index,field]=node.dataset.cycle.split(':');
    MathPDF.renderBlocks(node,run[side][Number(index)][field],options);
  }
  for(const node of section.querySelectorAll('[data-cycle-review]')) {
    const [stage,index,field]=node.dataset.cycleReview.split(':');
    MathPDF.renderBlocks(node,[{kind:'text',text:run[stage].items[Number(index)][field]}],options);
  }
  for(const node of section.querySelectorAll('[data-cycle-local]'))
    MathPDF.renderBlocks(node,[{kind:'text',text:run.local_notes[node.dataset.cycleLocal]}],options);
};
