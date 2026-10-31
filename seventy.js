window.renderSeventy=function(){
  const run=window.MATHPDF_SEVENTY;if(!run)return;
  const section=document.createElement('section');section.id=run.id;section.className='experiment-run';
  section.innerHTML=`<div class="panel experiment-intro"><div><span class="eyebrow">${esc(run.date)} · V5 · СІМ ТЕМ КОНСПЕКТУ</span><h2>70 задач із програмними перевірками</h2><p>${esc(run.summary)}</p></div><div class="experiment-cost"><strong>$${run.cost_usd.toFixed(7)}</strong><span>1 виклик mini · 0 LLM-перевіряльників</span><a href="experiments/v5-seventy/result.json" target="_blank" rel="noreferrer">JSON результатів ↗</a></div></div>
  <div class="summary-grid">${summary('Побудовано',run.items.length+'/70','По 10 у кожній темі',true)}${summary('Програмні перевірки',run.verified+'/70','Лише підтримувані сімейства')}${summary('Сімейств',String(run.families),'Числові варіанти дозволені')}${summary('Помилки рендерингу',String(run.rendering.fallbacks),'Формульних блоків: '+run.rendering.math_blocks)}</div>
  <div class="note">${esc(run.method)}</div><div class="note">${esc(run.limitations)}</div>
  <section class="panel"><div class="panel-heading"><h2>Результати за темами</h2></div><div class="table-scroll"><table><thead><tr><th>ТЕМА</th><th>ЗАДАЧ</th><th>СІМЕЙСТВ</th><th>ПРОГРАМНІ ПЕРЕВІРКИ</th></tr></thead><tbody>${run.topics.map(t=>`<tr><td>${esc(t.name)}</td><td>${t.count}</td><td>${t.families}</td><td><span class="tag">${t.count}/${t.count} пройдено</span></td></tr>`).join('')}</tbody></table></div></section>
  <section class="panel"><div class="panel-body"><h3>Що саме перевірено</h3><p>${esc(run.validation)}</p><p>${esc(run.review_notes)}</p></div></section>
  ${run.topics.map(t=>`<details class="panel seventy-topic" data-seventy-topic="${esc(t.id)}"><summary style="padding:20px;font-weight:600">${esc(t.name)} · ${t.count} задач</summary>${run.items.filter(x=>x.topic===t.id).map(x=>`<article class="experiment-problem seventy-problem" style="padding:20px"><span class="eyebrow">V5 · ЗАДАЧА ${x.id} · СТОР. ${x.source.page}</span><h2>${esc(x.title)}</h2><div class="report-math" data-seventy="${x.id}:question"></div><details><summary>Повний програмний розв’язок</summary><div class="report-math" data-seventy="${x.id}:answer"></div></details><details><summary>Параметри, джерело і перевірки</summary><p>${esc(x.source.reference)} · стор. ${x.source.page}. Шаблон: ${esc(x.template_id)}.</p><pre style="white-space:pre-wrap;overflow-wrap:anywhere">${esc(JSON.stringify(x.parameters,null,2))}</pre><ul>${x.checks.map(c=>`<li>${esc(c)}</li>`).join('')}</ul></details></article>`).join('')}</details>`).join('')}
  <section class="panel"><div class="panel-body"><p>Модель виконувала лише впорядкування тем: ${esc(run.model)}. Input ${run.usage.input_tokens}, output ${run.usage.output_tokens}. Seed ${run.seed}. Математичної генерації чи перевірки другою моделлю не було.</p></div></section>`;
  document.querySelector('main').prepend(section);
  const lookup=new Map(run.items.map(x=>[x.id,x]));
  for(const node of section.querySelectorAll('[data-seventy]')){
    const [id,field]=node.dataset.seventy.split(':');
    MathPDF.renderBlocks(node,lookup.get(Number(id))[field],{editable:false,linkSources:false,sourceLabel:s=>`main (12).pdf · стор. ${s.page}`});
  }
};
