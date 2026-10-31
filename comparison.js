window.renderComparison = function () {
  const run = window.MATHPDF_COMPARISON;
  if (!run) return;
  const names = {mini: 'GPT‑4.1 mini', full: 'GPT‑4.1'};
  const arms = ['mini', 'full'];
  const money = n => '$' + Number(n).toFixed(6);
  const cell = (arm, index) => {
    const item = run.results[arm].parsed.items[index];
    const correct = item.accept === run.cases[index].expected_accept;
    return `<span class="tag ${correct ? '' : 'red'}">${item.accept ? 'Прийняти' : 'Відхилити'} · ${correct ? '✓' : '×'}</span>`;
  };
  const section = document.createElement('section');
  section.id = run.id;
  section.className = 'experiment-run';
  section.innerHTML = `<div class="panel experiment-intro"><div><span class="eyebrow">${esc(run.date)} · КОНТРОЛЬОВАНЕ ПОРІВНЯННЯ</span><h2>Ті самі 10 задач — дві моделі</h2><p>Mini: 9/10 правильних рішень. GPT‑4.1: 10/10, але з помилкою у власному поясненні.</p></div><div class="experiment-cost"><strong>${money(run.cost_usd)}</strong><span>2 виклики · 20 оцінок</span><a href="experiments/compare-ten/result.json" target="_blank" rel="noreferrer">JSON результатів ↗</a></div></div>
  <div class="note">${esc(run.method)}</div>
  <section class="panel"><div class="panel-heading"><h2>Підсумок на цьому наборі</h2></div><div class="table-scroll"><table><thead><tr><th>МОДЕЛЬ</th><th>ПРАВИЛЬНІ РІШЕННЯ</th><th>ЗНАЙДЕНО ПОМИЛКОВИХ</th><th>ХИБНО ПРИЙНЯТО</th><th>ХИБНО ВІДХИЛЕНО</th><th>ВАРТІСТЬ</th></tr></thead><tbody>${arms.map(a => `<tr><td>${names[a]}</td><td>${run.scores[a].correct_decisions}/10</td><td>${run.scores[a].detected_invalid}/5</td><td>${run.scores[a].false_accepts}</td><td>${run.scores[a].false_rejects}</td><td>${money(run.results[a].cost_usd)}</td></tr>`).join('')}</tbody></table></div></section>
  <section class="panel"><div class="panel-heading"><h2>Порівняльна таблиця задач</h2></div><div class="table-scroll"><table><thead><tr><th>№</th><th>ТЕМА</th><th>ЕТАЛОН</th><th>GPT‑4.1 MINI</th><th>GPT‑4.1</th></tr></thead><tbody>${run.cases.map((c,i) => `<tr><td>${c.id}</td><td>${esc(c.topic)}</td><td>${c.expected_accept ? 'Прийняти' : 'Відхилити'}</td><td>${cell('mini',i)}</td><td>${cell('full',i)}</td></tr>`).join('')}</tbody></table></div></section>
  <div class="note">${esc(run.limitations)} Знак ✓ означає лише збіг рішення з еталоном.</div>
  ${run.cases.map((c,i) => `<article class="panel experiment-problem"><span class="eyebrow">КОНТРОЛЬНА ЗАДАЧА ${c.id}</span><h2>${esc(c.topic)}</h2><p>${esc(c.question)}</p><details><summary>Поданий розв’язок та еталон</summary><p>${esc(c.solution)}</p><p><strong>Еталон: ${c.expected_accept ? 'Прийняти' : 'Відхилити'}.</strong> ${esc(c.truth)}</p></details>${arms.map(a => `<details><summary>${names[a]}: ${run.results[a].parsed.items[i].accept ? 'прийняти' : 'відхилити'}</summary><p>${esc(run.results[a].parsed.items[i].explanation)}</p>${run.explanation_notes[a+':'+c.id] ? `<div class="manual-finding">${esc(run.explanation_notes[a+':'+c.id])}</div>` : ''}</details>`).join('')}</article>`).join('')}
  <section class="panel"><div class="panel-body"><h3>Відтворюваність і витрати</h3>${arms.map(a=>`<p>${esc(run.results[a].model)}: input ${run.results[a].usage.input_tokens}, output ${run.results[a].usage.output_tokens}, ${money(run.results[a].cost_usd)}.</p>`).join('')}<p>Повні відповіді, usage, еталон і хеші однакових входів збережено в JSON. Ключ API не публікується. MathPDF не змінювався.</p></div></section>`;
  document.querySelector('main .page-title')?.after(section);
  if (!section.isConnected) document.querySelector('main').prepend(section);
};
