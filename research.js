/* Lightweight catalogue; a detail page loads only its selected evidence bundle. */
const methods={llm:'Model review',templates:'Controlled templates',symbolic:'Symbolic checks',rag:'Retrieval + compilation'};
const bundles={
 'reviews-data.js':'MATHPDF_REVIEWS','comparison-data.js':'MATHPDF_COMPARISON',
 'cycle-data.js':'MATHPDF_CYCLE','parameterized-data.js':'MATHPDF_PARAMETERIZED',
 'seventy-data.js':'MATHPDF_SEVENTY','symbolic-data.js':'MATHPDF_SYMBOLIC',
 'rag-data.js':'MATHPDF_RAG','hundred-data.js':'MATHPDF_HUNDRED'
};
const loadedBundles=new Map();
let detailRevision=0;
function loadBundle(path){
 if(!Object.hasOwn(bundles,path))return Promise.reject(Error('Unknown evidence bundle.'));
 if(!loadedBundles.has(path))loadedBundles.set(path,new Promise((resolve,reject)=>{const s=document.createElement('script');s.src=path;s.onload=()=>resolve(window[bundles[path]]);s.onerror=()=>{loadedBundles.delete(path);s.remove();reject(Error('Evidence could not be loaded. Please retry.'))};document.head.append(s)}));
 return loadedBundles.get(path);
}
function money(v){return `$${Number(v).toFixed(4)}`}
function experimentChart(e){return `<figure class="experiment-chart"><figcaption>${esc(e.chart_title)}</figcaption><div class="chart-bars">${e.series.map(s=>`<div class="chart-row"><div class="chart-label"><span>${esc(s.label)}</span><strong>${s.value} / ${s.total}${s.unit==='count'?' tasks':''}</strong></div><div class="chart-track"><div class="chart-fill tone-${s.tone}" style="width:${100*s.value/s.total}%"></div></div></div>`).join('')}</div><p class="chart-caption">${esc(e.chart_note)}</p></figure>`}
function renderHub(){
 detailRevision++;
 const all=window.MATHPDF_EXPERIMENTS.experiments;
 $('main').innerHTML=title('EXPERIMENT NOTEBOOK','Small tests. <em>Clearer decisions.</em>','Every attempt, its result and what the chart actually measures. Open a study for the tasks, checks and limitations.')+
 `<div class="research-intro"><span class="tag">${all.length} task experiments</span><span class="tag neutral">4 historical card versions</span><span class="tag neutral">No API calls from this site</span></div><div class="filters"><label>Method <select id="method-filter"><option value="all">All methods</option>${Object.entries(methods).map(([k,v])=>`<option value="${k}">${v}</option>`).join('')}</select></label><span id="experiment-count" class="count">${all.length} experiments</span></div><div id="experiment-grid" class="experiment-grid"></div><div class="section-head"><div><span class="eyebrow">A SEPARATE EVIDENCE TRACK</span><h2>Flashcards · v1–v4</h2></div><a class="text-button" href="#overview">Compare matching sets →</a></div><p class="subline">Historical LLM scores for cards. These samples differ and do not form a single accuracy trend.</p><div class="history-grid">${db.versions.filter(v=>historyTitles[v.id]).map(v=>{const rows=db.records.filter(r=>r.version===v.id);return `<a class="panel history-tile" href="experiment.html?id=cards-${encodeURIComponent(v.id)}"><span class="eyebrow">${esc(v.id)} · ${sum(rows)} cards</span><h3>${esc(historical(v,'title'))}</h3><p>${esc(historical(v,'notes'))}</p><span class="text-button">View study →</span></a>`}).join('')}</div><div class="callout">A model approval, a matching reference label, a symbolic result and a template check answer different questions. Their percentages should not be combined.</div>`;
 function draw(){const selected=$('method-filter').value;const rows=all.filter(e=>selected==='all'||e.method===selected);$('experiment-count').textContent=`${rows.length} experiments`;$('experiment-grid').innerHTML=rows.map(e=>`<article class="panel experiment-card"><div class="experiment-meta"><span class="eyebrow">ATTEMPT ${String(e.number).padStart(2,'0')}</span><span class="tag neutral">${methods[e.method]}</span></div><h2><a href="experiment.html?id=${e.id}">${esc(e.title)}</a></h2><p class="experiment-description">${esc(e.description)}</p>${experimentChart(e)}<p class="experiment-finding">${esc(e.finding)}</p><div class="experiment-footer"><span class="small-label">${esc(e.date)} · API ${money(e.cost_usd)}</span><a class="text-button" href="experiment.html?id=${e.id}">Read study →</a></div></article>`).join('')}
 $('method-filter').onchange=draw;draw();
}
const studyNotes={
 'review-four':[
 ['Method','Mini generated four tasks. GPT-4.1 independently solved them and then audited their statements, solutions, source support and formatting.'],
 ['The missed error','Task 2 simplifies (x²−1)/x as x+1−1/x. The correct expression is x−1/x. At x=2 the generated value is 5/2 instead of 3/2. All four tasks were nevertheless approved.'],
 ['Limit','Four tasks are a small diagnostic sample. A separate model call does not guarantee an independent or correct mathematical judgement.']],
 'review-mini-four':[
 ['Method','Separate mini calls generated four new tasks, solved them blindly and audited them. This is a new set, so it is not a controlled model comparison with attempt 01.'],
 ['What was missed','Task 3 declares f: Z→Z while using pairs in Z² as inputs. Task 4 was correctly flagged as not bijective, but the blind reviewer gave the wrong rational preimage for (1,0): it should be (3/5,−1/5), not (0,1/3).'],
 ['Limit','Three accepts and one revision are reviewer decisions. They are not three independently verified correct tasks.']],
 'compare-ten':[
 ['Method','Both models reviewed the same ten hand-authored controls: five valid solutions and five flawed ones. The schema, prompt and temperature were held fixed.'],
 ['Results','Mini matched 9/10 reference decisions and detected 4/5 flawed solutions. GPT-4.1 matched 10/10 decisions. Mini incorrectly accepted case 10, where one input has two outputs.'],
 ['Explanation quality','GPT-4.1 rejected case 1 correctly, but its explanation included false algebraic equalities. A correct verdict is not enough to trust the reasoning.']],
 'cycle-fifteen':[
 ['Method','Mini generated fifteen tasks. GPT-4.1 reviewed them; mini repaired the output; a fresh GPT-4.1 call reviewed the repaired version.'],
 ['No local mathematical gain','Model approval rose from 14/15 to 15/15. Local mathematical review remained 14/15. Task 9 was valid but unnecessarily changed. Task 13 still has an invalid codomain: for f(x)=2/x+1 into R excluding 2, f(2)=2 is forbidden, while 1 is unattainable.'],
 ['Formula structure regressed','Explicit structured math parts fell from 124 to zero; standalone rendered blocks fell from 25 to zero. Legacy recovery produced zero fallback errors, which hid the loss of structure. All fifteen serialized tasks changed; this does not mean fifteen useful fixes.']],
 'v5-parameterized':[
 ['Method','One mini call selected the ordering and titles of supported families. Code chose admissible parameters and constructed the statement, formulas and solution from one mathematical representation. No second model reviewed the tasks.'],
 ['Result','Ten variants passed family-specific checks; thirty-six math blocks rendered with zero fallbacks. A local title-length guard was relaxed from 80 to 120 characters, using the same paid response.'],
 ['Limit','The checks establish properties within prepared families. New structures or unsupported topics require an adapter or an explicit refusal.']],
 'v5-seventy':[
 ['Method','One mini call selected topic order only. Code generated seventy numeric variants across forty supported families, ten tasks in each of seven topics.'],
 ['Result','All seventy passed their family checks; 201 math blocks rendered with zero fallbacks. No model acted as a second reviewer.'],
 ['Limit','This expands controlled coverage. It does not demonstrate that an LLM can freely invent seventy correct problems or that finite spot checks prove an induction theorem.']],
 'sympy-55':[
 ['Method','The LLM generated actual statements, solutions and machine-readable formal records. The main sample contains forty close analogues and fifteen requested condition changes. Two exploratory pilots are preserved separately and excluded from the main fifty-five.'],
 ['Formal scope','SymPy confirmed 16 formal records, partially checked 30, refuted one encoding and could not support eight. Near case 7 has a correct textual factorial sum but a different encoded sum: the failed encoding is not a refutation of its prose.'],
 ['Local mathematical findings','Four actual mathematical errors were identified locally, separate from SymPy statuses: near 39 makes a false birthday pigeonhole claim; near 40 uses an invalid geometric bound; transfer 4 has a false factorial-sum identity; transfer 14 incorrectly denies that injectivity of a composition implies injectivity of the first map.'],
 ['Transfer limitations','Transfer 1 repeats near 3; transfer 11 does not deliver the requested extraneous-root scenario. A valid calculation alone does not verify novelty or goal fulfilment.'],
 ['Cost','The displayed total includes all four paid generation calls, including the two pilots. The main sample alone cost $0.0353724.']],
 'rag-fifteen':[
 ['Method','Fifteen manually authored theory-only goals were matched against a bank of forty curated families. Hard compatibility filters and BM25 retrieved three candidates; mini chose a family; code compiled and checked the numerical variant.'],
 ['Result','The expected family ranked first for 14/15 goals and appeared in the top three for all fifteen. The model selected a goal-matching family for every goal. Query 13 needed the second-ranked candidate. Three negative controls were refused.'],
 ['Correction and limits','Profile 5 required a negative dividend, but the initial local draw was positive. An explicit negative constraint fixed the draw offline without another model call. The profiles and bank share a source lineage, so this is not an independent unseen-course test.']],
 'rag-hundred':[
 ['Method','Targeted page searches in the updated notes and Book of Proof supported fifty goals across ten topics. Thirty-seven families were reused and thirteen added. The model planned family choices; code supplied the mathematics for two variants per goal.'],
 ['Initial failure retained','The expected family appeared in raw top-1 results for 44/50 profiles and top-3/top-5 for 49/50. Profile 14 selected the right congruence family outside the allowed retrieved context. The guard rejected its two variants, leaving 98/100 initially admitted.'],
 ['Retry and result','Generic plural/synonym normalization fixed retrieval. One short planning retry for profile 14 admitted the remaining two variants. All one hundred supported variants passed family checks; 294 math blocks rendered with zero fallbacks. There was no LLM reviewer.'],
 ['Source and coverage limits','Only selected pages were inspected: 34 unique pages accessed in the 74-page notes and 39 in the 380-page book, including preliminary navigation. Full PDFs were not uploaded or published. This validates supported families and controlled variants, not arbitrary new mathematics.']]
};
function ragAlgorithm(){return `<section class="panel study-section"><h2>Retrieval → admissible variant</h2><ol class="algorithm-list">${[
 ['Profile the theory','Record the topic, domain, prerequisites, available methods and exact source pages. Do not invent missing assumptions. Profiles in these prototypes were authored manually.'],
 ['Maintain a verified bank','Store each family with its exemplar, solution, domain, parameter constraints, verifier and version.'],
 ['Filter before ranking','Reject incompatible topics, domains and missing prerequisites. A real-valued example cannot silently replace an integer problem.'],
 ['Retrieve candidates','Rank compatible families with BM25. Top-k scores describe retrieval relevance, not mathematical correctness.'],
 ['Constrain the model choice','Send selected theory and retrieved exemplars. Accept only a family present in that context; otherwise refuse or retry. Reference test labels are hidden from the model.'],
 ['Compile from one representation','Draw admissible numbers and build the statement, formulas and answer together. Do not mark unsupported structures as verified.'],
 ['Keep three checks separate','Check goal alignment, mathematical constraints and rendering independently. Induction needs a valid base and transition, not only a few numerical cases.'],
 ['Record provenance or refuse','Retain source pages, retrieval, chosen family, parameters, checks, failures, retries and cost. Refuse when the bank cannot support the request.']
 ].map(([a,b])=>`<li><strong>${a}</strong><p>${b}</p></li>`).join('')}</ol></section>`}
function taskShell(id,title,body,meta=''){return `<details class="task-evidence" data-task="${esc(id)}"><summary><span class="tag neutral">${esc(id)}</span> ${esc(title||'Task')}<span class="cell-meta">${esc(meta)}</span></summary><div class="task-body">${body}</div></details>`}
function mathSlot(blocks){const id=`math-${mathSlot.next++}`;mathSlot.queue.push([id,blocks]);return `<div class="report-math" id="${id}"></div>`}
mathSlot.next=0;mathSlot.queue=[];
function blocksFor(x){return Array.isArray(x)?x:[{kind:'text',text:String(x||'')}]}
function qa(p){return `<h4>Statement</h4>${mathSlot(blocksFor(p.question))}<h4>Solution</h4>${mathSlot(blocksFor(p.answer??p.solution))}`}
function decision(v){return v===true?'Accept':v===false?'Reject':String(v??'Not recorded')}
function tasksFor(e,a){
 mathSlot.queue=[];
 if(e.run_id)return a.problems.map((p,i)=>{const audit=a.audit.items.find(x=>String(x.problem_id)===String(i+1))||a.audit.items[i];return taskShell(i+1,p.title,`<p class="note">Reviewer decision: ${esc(decision(audit?.decision))}. Original model reasoning is preserved in the evidence JSON.</p>${qa(p)}`)}).join('');
 if(e.id==='compare-ten')return `<section class="panel table-scroll"><table><thead><tr><th>Case</th><th>Reference</th><th>Mini</th><th>GPT-4.1</th></tr></thead><tbody>${a.cases.map(c=>`<tr><td>${esc(c.id)}</td><td>${decision(c.expected_accept)}</td>${['mini','full'].map(k=>`<td>${decision(a.results[k].parsed.items.find(x=>String(x.id)===String(c.id))?.accept)}</td>`).join('')}</tr>`).join('')}</tbody></table></section>`+a.cases.map(c=>taskShell(c.id,'Control case',qa(c),`Reference: ${decision(c.expected_accept)}`)).join('');
 if(e.id==='cycle-fifteen')return a.before.map((p,i)=>taskShell(i+1,p.title,`<div class="before-after"><section><h3>Before repair</h3>${qa(p)}</section><section><h3>After repair</h3>${qa(a.after[i])}</section></div><p class="note">Local correctness: ${a.local_review?.items?.[i]?.before_correct?'pass':'fail'} before / ${a.local_review?.items?.[i]?.after_correct?'pass':'fail'} after. ${esc(a.local_review?.items?.[i]?.reason||'')}</p>`)).join('');
 if(e.id==='sympy-55')return a.groups.map(g=>`<h3>${g.id.startsWith('near')?'Close analogues · 40 tasks':'Changed conditions · 15 tasks'}</h3>`+g.items.map(({task:t,check:c})=>taskShell(`${g.id}-${t.id}`,t.title,`${qa(t)}<h4>Symbolic check · ${esc(c.status)}</h4><p>${esc(c.evidence)}</p><p>${esc(c.scope)}</p><h4>Requested condition change</h4><p>${esc(t.condition_change)}</p><details><summary>Formal record</summary><pre>${esc(JSON.stringify({kind:t.kind,parameters:t.params_json,answer:t.answer,steps:t.steps},null,2))}</pre></details>`,t.topic)).join('')).join('');
 const rows=e.id==='rag-fifteen'?a.rows:e.id==='rag-hundred'?a.tasks:a.items;
 return rows.map((r,i)=>{const p=r.artifact||r.item||r;const profile=e.id==='rag-hundred'?a.profiles.find(x=>x.id===r.profile_id):e.id==='rag-fifteen'?r:null;return taskShell(r.id??i+1,p.title,`${profile?`<h4>Learning goal</h4><p>${esc(profile.goal)}</p><p>Expected family: <code>${esc(profile.expected)}</code></p>`:''}${qa(p)}<h4>Program checks</h4><ul>${(p.checks||[]).map(c=>`<li>${esc(c)}</li>`).join('')}</ul><details><summary>Parameters and source references</summary><pre>${esc(JSON.stringify({family:p.template_id,parameters:p.parameters,source:p.source,support:r.source_support},null,2))}</pre></details>`,p.template_id)}).join('');
}
function renderHistoricalDetail(id){
 const v=db.versions.find(x=>x.id===id);if(!v)return renderMissing();
 const rows=db.records.filter(r=>r.version===id),bars=metrics.map(m=>({label:m.label+(m.high?' ↑':' ↓'),value:avg(rows,m.key)===null?null:Math.round(avg(rows,m.key)*1000)/10,total:100,tone:'sage'}));
 const e={chart_title:'Saved LLM evaluation scores',chart_note:'Card-count-weighted averages of available scores. These are source and learning-quality judgements, not verified mathematical correctness. Missing metrics remain missing.',series:bars.filter(b=>b.value!==null)};
 $('main').innerHTML=`<a class="text-button back-link" href="index.html#reviews">← All experiments</a>`+title(`FLASHCARD HISTORY · ${esc(v.id)}`,esc(historical(v,'title')),esc(historical(v,'notes')))+`<section class="panel study-section">${experimentChart(e)}<p>${sum(rows)} cards across ${rows.length} sets · ${esc(v.date)}</p><p>Exact historical generation prompts and all judge configurations were not retained. This study is separate from task V5.</p><a href="index.html?version=${encodeURIComponent(v.id)}#overview">Compare matching sets →</a> · <a href="index.html?version=${encodeURIComponent(v.id)}#cards">Browse original cards →</a> · <a href="data/history.json">Original history JSON ↗</a></section><section class="panel table-scroll"><table><thead><tr><th>Topic</th><th>Level</th><th>Source</th><th>Pages</th><th>Cards</th></tr></thead><tbody>${rows.map(r=>`<tr><td>${esc(name(r.topic))}</td><td>${esc(r.level)}</td><td>${esc(r.document)}</td><td>${esc(r.pages)}</td><td>${r.n}</td></tr>`).join('')}</tbody></table></section>`;
}
function renderMissing(){document.title='Study not found · MathPDF';$('main').innerHTML=title('EXPERIMENT NOTEBOOK','Study not found.','Choose an experiment from the catalogue.')+'<a class="primary" href="index.html#reviews">Back to experiments</a>'}
window.renderReviews=async function(){
 if(!location.pathname.endsWith('experiment.html'))return renderHub();
 const rev=++detailRevision,id=new URLSearchParams(location.search).get('id');
 if(id?.startsWith('cards-'))return renderHistoricalDetail(id.slice(6));
 const e=window.MATHPDF_EXPERIMENTS.experiments.find(e=>e.id===id);if(!e)return renderMissing();
 document.title=`${e.title} · MathPDF Quality Lab`;
 $('main').innerHTML=title('LOADING STUDY',esc(e.title),'Loading the selected evidence…');
 try{
  let a=await loadBundle(e.data_script);if(rev!==detailRevision||view!=='reviews')return;if(e.run_id)a=a.find(x=>x.id===e.run_id);
  $('main').innerHTML=`<a class="text-button back-link" href="index.html#reviews">← All experiments</a>`+title(`ATTEMPT ${String(e.number).padStart(2,'0')} · ${methods[e.method]}`,esc(e.title),esc(e.description))+`<div class="research-intro"><span class="tag">${esc(e.date)}</span><span class="tag neutral">Recorded API cost ${money(e.cost_usd)}</span><a class="text-button" href="${e.evidence}">Original evidence JSON ↗</a></div><div class="study-lead"><section class="panel study-section">${experimentChart(e)}</section><section class="panel study-section"><span class="eyebrow">WHAT WE LEARNED</span><h2>${esc(e.finding)}</h2><p class="subline">Read the scope of the checks before treating any count as a quality score.</p></section></div><section class="panel study-section"><h2>Method, findings and limitations</h2>${studyNotes[e.id].map(([h,t])=>`<h3>${esc(h)}</h3><p>${esc(t)}</p>`).join('')}</section>${e.method==='rag'?ragAlgorithm():''}<div class="section-head"><div><span class="eyebrow">PRIMARY EVIDENCE</span><h2>Tasks and checks</h2></div><button class="quiet" id="expand-tasks">Expand all tasks</button></div><p class="hint">Statements and solutions below preserve the generated evidence, including mistakes. Model verdicts are not endorsements. Original audit prose is available in the JSON in its original language.</p><div class="task-list">${tasksFor(e,a)}</div><div class="callout">${esc(e.chart_note)} <a href="${e.evidence}">Download the full original record →</a></div>`;
  mathSlot.queue.forEach(([id,blocks])=>MathPDF.renderBlocks($(id),blocks,{editable:false,linkSources:false,sourceLabel:ref=>`Source page ${ref.page}`}));
  $('expand-tasks').onclick=()=>{const open=$('expand-tasks').textContent.startsWith('Expand');document.querySelectorAll('.task-evidence').forEach(d=>d.open=open);$('expand-tasks').textContent=open?'Collapse all tasks':'Expand all tasks'};
 }catch(error){if(rev===detailRevision&&view==='reviews')$('main').innerHTML=title('EVIDENCE UNAVAILABLE',esc(e.title),esc(error.message))+`<a class="text-button" href="${e.evidence}">Open original evidence →</a> <button class="quiet" id="retry-study">Retry</button>`;const retry=$('retry-study');if(retry)retry.onclick=window.renderReviews}
};
