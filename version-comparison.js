/* Cross-study synthesis. Descriptive scores are never treated as paired gains. */
function comparisonRows(){
 const rows=db.versions.map(v=>{
  const records=db.records.filter(r=>r.version===v.id);
  return {id:v.id,title:historical(v,'title'),n:sum(records),scores:Object.fromEntries(metrics.map(m=>[m.key,avg(records,m.key)])),
   scope:records.length?`${records.length} sets · ${[...new Set(records.map(r=>name(r.topic)))].join(', ')}`:'No evaluated sets',
   note:historyTitles[v.id]?'Historical judge settings not fully retained. Different levels and page ranges.':'Browser-local version; inspect its own source metadata.',
   href:historyTitles[v.id]?`experiment.html?id=cards-${encodeURIComponent(v.id)}`:'#versions'};
 });
 const w=window.MATHPDF_EXPERIMENTS.flashcard_baseline;
 if(w)rows.push({...w,scope:`4 topics · level ${w.difficulty} · ${w.source}`,note:`Judge: ${w.judge}. Fresh sample, not a matched historical rerun.`,href:'experiment.html?id=wildflower'});
 for(const c of window.MATHPDF_EXPERIMENTS.flashcard_candidates||[])rows.push({...c,scope:`4 topics · level ${c.difficulty} · ${c.source}`,note:c.n===60?'60-card continuation. Same original rubric; batching and prior-card context differ from Wildflower.':'20-card pilot. Original rubric only; revised diagnostic is separate.',href:`experiment.html?id=${c.id}`});
 return rows;
}
const studyScopes={
 'review-four':'4 new tasks; GPT-4.1 blind solve + audit. Separate local algebra check.',
 'review-mini-four':'4 different tasks; mini blind solve + audit. Not the same inputs as attempt 01.',
 'compare-ten':'The same 10 labelled controls: mini 9/10 vs GPT-4.1 10/10 decisions. Explanation errors remain.',
 'cycle-fifteen':'15 tasks before/after repair: model 14→15 approved; local mathematical assessment 14→14.',
 'v5-parameterized':'10 curated families. The model plans; code owns parameters, formulas and answers.',
 'v5-seventy':'70 variants, 40 supported families, 7 topics. Code-generated mathematics.',
 'sympy-55':'55 actual LLM tasks: 16 confirmed formal records, 30 partial, 1 refuted encoding, 8 unsupported.',
 'rag-fifteen':'15 manual goals: expected top-1 14/15, top-3 15/15. Shared source lineage.',
 'rag-hundred':'50 profiles, 100 variants: 98 initially admitted, 100 after retrieval repair; supported-family checks only.',
 'wildflower':'60 cards + 40 tasks. Judge accepts 36/40 tasks; local findings contradict approval.',
 'clearleaf':'20 cards: original self-containment 14/20, revised diagnostic 18/20; local atomicity 15/20.',
 'clearleaf-sixty':'60 vs 60: faithfulness 84.7→90.8%; atomicity 96.7→88.3%. Same original evaluator; batching differs.'
};
function renderComparisonPage(){
 const rows=comparisonRows(),studies=window.MATHPDF_EXPERIMENTS.experiments;
 $('main').innerHTML=title('COMPARISON','Versions & results','Different samples and judges: descriptive scores, not a ranking.')+
 `<section class="panel study-section"><h2>Priority: formula fidelity and reliable evaluation</h2><p>Fix mathematical meaning and hidden context in card fronts. Calibrate the judge before using approval as a quality gate. Controlled task families remain a separate supported route.</p><a class="text-button" href="#reviews">All experiments →</a> · <a class="text-button" href="#overview">Matched historical sets →</a></section>
 <div class="section-head"><h2>Flashcards</h2></div><section class="panel table-scroll"><table id="version-comparison"><thead><tr><th>Version / cards</th>${metrics.map(m=>`<th>${esc(m.label)} ${m.high?'↑':'↓'}</th>`).join('')}</tr></thead><tbody>${rows.map(r=>`<tr><td><a href="${r.href}"><strong>${esc(r.id)}</strong></a><span class="cell-meta">${r.n} cards</span></td>${metrics.map(m=>`<td>${pct(r.scores[m.key])}</td>`).join('')}</tr>`).join('')}</tbody></table></section>
 <section class="panel study-section"><label>Metric <select id="comparison-metric">${metrics.map(m=>`<option value="${m.key}">${esc(m.label)} ${m.high?'↑':'↓'}</option>`).join('')}</select></label><figure class="experiment-chart"><figcaption id="comparison-chart-title"></figcaption><div id="comparison-bars" class="chart-bars"></div><p class="chart-caption">Each bar uses its own sample. A higher bar is not evidence of improvement between versions.</p></figure><details><summary>Samples & comparability</summary>${rows.map(r=>`<p><strong>${esc(r.id)}</strong> · ${esc(r.scope)}<br>${esc(r.note)}</p>`).join('')}<p>Available scores are weighted by card count. Missing values stay missing. Historical judge settings are incomplete; newer samples are not paired historical reruns.</p></details></section>
 <div class="section-head"><h2>Experiments</h2></div><section class="panel table-scroll"><table id="method-comparison"><thead><tr><th>Study</th><th>Measured result</th><th>Finding</th><th>API cost</th></tr></thead><tbody>${studies.map(e=>`<tr><td><a href="experiment.html?id=${e.id}"><strong>${String(e.number).padStart(2,'0')} · ${esc(e.title)}</strong></a></td><td>${esc(studyScopes[e.id]||e.description)}</td><td>${esc(e.finding)}</td><td>${money(e.cost_usd)}</td></tr>`).join('')}</tbody></table></section><p class="hint">Model approval, formal coverage and supported-family checks measure different things. Costs cover different work and sample sizes.</p>
 <section class="panel study-section"><h2>Next decision</h2><p>The 60-card comparison shows higher source faithfulness but lower atomicity. Keep the candidate experimental; narrow the learning targets and validate on held-out material before changing MathPDF.</p></section>`;
 function draw(){const key=$('comparison-metric').value,m=metrics.find(m=>m.key===key);$('comparison-chart-title').textContent=`${m.label} · ${m.high?'higher':'lower'} is better`;$('comparison-bars').innerHTML=rows.map(r=>`<div class="chart-row"><div class="chart-label"><span>${esc(r.id)} · ${r.n} cards</span><strong>${pct(r.scores[key])}</strong></div><div class="chart-track"><div class="chart-fill ${r.id==='wildflower'?'tone-ink':'tone-muted'}" style="width:${finite(r.scores[key])?r.scores[key]*100:0}%"></div></div></div>`).join('')}
 $('comparison-metric').onchange=draw;draw();
}
