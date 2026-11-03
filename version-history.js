/* One catalogue tile per version; runs remain separate and newest first. */
function versionGroups(){
 const groups=new Map(),families={clearleaf:['clearleaf','Clearleaf'],'clearleaf-sixty':['clearleaf','Clearleaf'],'v5-parameterized':['task-v5','Task V5'],'v5-seventy':['task-v5','Task V5'],'rag-fifteen':['rag','RAG'],'rag-hundred':['rag','RAG']};
 for(const e of window.MATHPDF_EXPERIMENTS.experiments){
  const [id,label]=families[e.id]||[e.id,e.id==='wildflower'?'Wildflower':e.title];
  if(!groups.has(id))groups.set(id,{id,title:label,method:e.method,runs:[]});
  groups.get(id).runs.push({...e,sequence:e.number,href:`experiment.html?id=${e.id}`});
 }
 groups.set('briefleaf',{id:'briefleaf',title:'Briefleaf',method:'baseline',runs:window.ACADENCE_VERSION_RUNS.map(r=>({...r,href:`experiments/${r.id}/cards.md`,evidence:`experiments/${r.id}/result.json`,briefleaf:true}))});
 for(const v of db.versions.filter(v=>historyTitles[v.id])){
  const rows=db.records.filter(r=>r.version===v.id);
  groups.set(v.id,{id:v.id,title:`${v.id} · ${historical(v,'title')}`,method:'history',runs:[{id:v.id,title:historical(v,'title'),date:v.date,sequence:0,finding:historical(v,'notes'),cards:sum(rows),href:`experiment.html?id=cards-${encodeURIComponent(v.id)}`,historical:true}]});
 }
 const compare=(a,b)=>String(b.date).localeCompare(String(a.date))||(b.sequence||0)-(a.sequence||0);
 for(const g of groups.values())g.runs.sort(compare);
 return [...groups.values()].sort((a,b)=>compare(a.runs[0],b.runs[0]));
}
function versionHref(id){return `experiment.html?family=${encodeURIComponent(id)}`}
function renderVersionHub(){
 const groups=versionGroups(),labels={...methods,history:'Historical flashcards'};
 document.title='Versions · Acadence Metrics';
 $('main').innerHTML=title('VERSION NOTEBOOK','Versions','One version, one place. Latest activity first.')+`<div class="research-intro"><a class="tag" href="${versionHref('wildflower')}">Primary: Wildflower</a><a class="text-button" href="#comparison">Compare results →</a></div><div class="filters"><label>Method <select id="method-filter"><option value="all">All methods</option>${Object.entries(labels).map(([k,v])=>`<option value="${k}">${esc(v)}</option>`).join('')}</select></label><span id="experiment-count" class="count"></span></div><div id="experiment-grid" class="experiment-grid"></div>`;
 function draw(){
  const rows=groups.filter(g=>$('method-filter').value==='all'||g.method===$('method-filter').value);
  $('experiment-count').textContent=`${rows.length} versions`;
  $('experiment-grid').innerHTML=rows.map(g=>{const r=g.runs[0];return `<article class="panel experiment-card version-card" data-version="${esc(g.id)}"><div class="experiment-meta"><span class="eyebrow">${esc(r.date)}</span><span class="tag neutral">${esc(labels[g.method])}</span></div><h2><a href="${versionHref(g.id)}">${esc(g.title)}</a></h2>${g.id==='wildflower'?'<span class="tag">Primary for flashcards</span>':''}<p class="small-label">${g.runs.length} recorded ${g.runs.length===1?'run':'runs'} · latest: ${esc(r.title)}</p><p class="experiment-finding">${esc(r.finding||'Historical evaluation and original records.')}</p><div class="experiment-footer"><span class="small-label">Newest → oldest</span><a class="text-button" href="${versionHref(g.id)}">Open version →</a></div></article>`}).join('');
 }
 $('method-filter').onchange=draw;draw();
}
function runMetrics(r){
 if(!r.metrics)return r.briefleaf?'<p class="hint">Generation and local inspection only. No model evaluator was run.</p>':'';
 return `<div class="table-scroll"><table><thead><tr><th>Self-contained</th><th>Source faithfulness</th><th>One target</th><th>Duplicate signal ↓</th></tr></thead><tbody><tr>${['pct_self_contained','avg_faithfulness','pct_atomic','duplicate_rate'].map(k=>`<td>${pct(r.metrics[k])}</td>`).join('')}</tr></tbody></table></div><p class="hint">Original judge signals, not mathematical correctness.</p>`;
}
async function renderVersionHistory(id){
 const rev=++detailRevision,g=versionGroups().find(x=>x.id===id);
 if(!g)return renderMissing();
 document.title=`${g.title} · Acadence Metrics`;
 $('main').innerHTML=`<a class="text-button back-link" href="index.html#reviews">← All versions</a>`+title('VERSION HISTORY',esc(g.title),'Runs are listed from newest to oldest. Each keeps its own sample and evidence.')+`<div class="version-timeline">${g.runs.map((r,i)=>`<details class="panel study-section version-run" data-run="${esc(r.id)}" ${i===0?'open':''}><summary><span><span class="eyebrow">${esc(r.date)}${i===0?' · LATEST':''}</span><strong>${esc(r.title)}</strong></span><span class="tag neutral">${r.cards?r.cards+' cards':'Recorded study'}</span></summary><div class="version-run-body"><p>${esc(r.finding||'Historical source and evaluation records.')}</p>${runMetrics(r)}${r.series?experimentChart(r):''}<p class="small-label">${r.cost_usd!==undefined?'Recorded API cost '+money(r.cost_usd):'Historical sample'}${r.briefleaf?' · generator: gpt-4.1-mini':''}</p><p><a class="text-button" href="${r.href}">${r.briefleaf?'Original cards & notes ↗':'Full study & original items →'}</a>${r.evidence?` · <a class="text-button" href="${r.evidence}">Evidence JSON ↗</a>`:''}${r.briefleaf?` · <a class="text-button" href="experiments/${r.id}/flashcards.md">Prompt ↗</a>`:''}</p>${r.briefleaf?`<div id="run-cards-${r.id}"><p class="hint">Loading cards…</p></div>`:''}</div></details>`).join('')}</div>`;
 if(g.id!=='briefleaf')return;
 try{
  const data=await loadBundle('briefleaf-runs-data.js');
  if(rev!==detailRevision||view!=='reviews')return;
  for(const r of g.runs){const d=data[r.id],slot=$(`run-cards-${r.id}`);
   slot.innerHTML=`<details><summary>Local findings</summary><ul>${d.findings.map(x=>`<li>${esc(x)}</li>`).join('')}</ul></details>${d.sets.map((s,si)=>`<h3>${esc(s.topic)}</h3>${s.items.map((c,ci)=>`<details class="task-evidence"><summary>${ci+1}. ${esc(c.question.join(' '))}</summary><div class="task-body"><p class="hint">Source page ${c.formula.page} · ${esc(c.skill)}</p><strong>From notes</strong><div id="${r.id}-${si}-${ci}-source"></div><strong>Explanation</strong><div id="${r.id}-${si}-${ci}-explanation"></div></div></details>`).join('')}`).join('')}`;
   d.sets.forEach((s,si)=>s.items.forEach((c,ci)=>{
    for(const [key,blocks] of [['source',[...(c.formula.latex?[c.formula]:[]),...(c.from_notes||[])]],['explanation',c.explanation||[]]]){
     const target=$(`${r.id}-${si}-${ci}-${key}`);
     if(blocks.length)MathPDF.renderBlocks(target,versionNativeBlocks(blocks),{editable:false,linkSources:false});else target.textContent='No additional content.';
    }
   }));
  }
 }catch(error){if(rev===detailRevision)document.querySelectorAll('[id^="run-cards-"]').forEach(x=>{x.textContent='Cards could not load. Use the original cards link above.'})}
}

function versionNativeBlocks(blocks){
 return blocks.map(b=>b.latex?{kind:'math',latex:b.latex,display:true,source:{page:b.page}}:{kind:'text',text:(b.parts||[]).map(p=>typeof p==='string'?p:'\\('+p.math+'\\)').join('')});
}
