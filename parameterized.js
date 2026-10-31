window.renderParameterized = function () {
  const run = window.MATHPDF_PARAMETERIZED;
  if (!run) return;
  const section=document.createElement('section');
  section.id=run.id;section.className='experiment-run';
  section.innerHTML=`<div class="panel experiment-intro"><div><span class="eyebrow">${esc(run.date)} · ЗАДАЧІ V5 · ПАРАМЕТРИ ПІД КОНТРОЛЕМ ПРОГРАМИ</span><h2>10 задач із прикладів конспекту</h2><p>${esc(run.summary)}</p><div class="experiment-flow"><span>Mini <small>тип і назва</small></span><b>→</b><span>Програма <small>числа й розв’язок</small></span><b>→</b><span>Точні перевірки <small>без другої LLM</small></span></div></div><div class="experiment-cost"><strong>$${run.cost_usd.toFixed(6)}</strong><span>1 виклик mini · 0 перевіряльників LLM</span><a href="experiments/v5-parameterized/result.json" target="_blank" rel="noreferrer">JSON результатів ↗</a></div></div>
  <div class="summary-grid">${summary('Побудовано',run.items.length+'/10','10 підтримуваних типів',true)}${summary('Програмні перевірки',run.verified+'/10','У межах закритих шаблонів')}${summary('Формули',String(run.rendering.math_blocks),'Структуровані формульні блоки')}${summary('Помилки рендерингу',String(run.rendering.fallbacks),'Окрема перевірка KaTeX')}</div>
  <div class="note">${esc(run.method)}</div><div class="note">${esc(run.limitations)}</div>
  <section class="panel"><div class="panel-heading"><h2>Таблиця v5</h2></div><div class="table-scroll"><table><thead><tr><th>№</th><th>ЗАДАЧА</th><th>ОСНОВА З КОНСПЕКТУ</th><th>ПЕРЕВІРКА ПРОГРАМОЮ</th></tr></thead><tbody>${run.items.map(x=>`<tr><td>${x.id}</td><td>${esc(x.title)}</td><td>${esc(x.source.reference)} · ${x.source.page}</td><td><span class="tag">Пройдено</span></td></tr>`).join('')}</tbody></table></div></section>
  ${run.items.map(x=>`<article class="panel experiment-problem v5-problem"><span class="eyebrow">V5 · ЗАДАЧА ${x.id}</span><h2>${esc(x.title)}</h2><div class="report-math" data-v5="${x.id}:question"></div><details><summary>Розв’язок, обчислений програмою</summary><div class="report-math" data-v5="${x.id}:answer"></div></details><details><summary>Параметри та програмні перевірки</summary><p>Шаблон: ${esc(x.template_id)}. Основа: ${esc(x.source.reference)}, стор. ${x.source.page}.</p><pre style="white-space:pre-wrap;overflow-wrap:anywhere">${esc(JSON.stringify(x.parameters,null,2))}</pre><ul>${x.checks.map(c=>`<li>${esc(c)}</li>`).join('')}</ul></details></article>`).join('')}
  <section class="panel"><div class="panel-body"><h3>Що змінилося у v5</h3><p>${esc(run.findings)}</p><p>Модель: ${esc(run.model)}. Input: ${run.usage.input_tokens}, output: ${run.usage.output_tokens}. Seed: ${run.seed}. ${esc(run.validation_summary)}</p></div></section>`;
  document.querySelector('main').prepend(section);
  for(const node of section.querySelectorAll('[data-v5]')){
    const [id,field]=node.dataset.v5.split(':');
    MathPDF.renderBlocks(node,run.items.find(x=>x.id===Number(id))[field],{editable:false,linkSources:false,sourceLabel:s=>`main (12).pdf · стор. ${s.page}`});
  }
};
