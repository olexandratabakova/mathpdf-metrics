"""
Self-contained HTML report generator.
Produces a single .html file with embedded CSS + JS — no server or internet required.

Uses str.replace() for data injection instead of str.format() to avoid collisions
with JavaScript template literal curly braces.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from .models import SetMetrics
from .llm_client import get_token_stats
from . import config

# ── Helpers ────────────────────────────────────────────────────────────────────

def _clean(s: str) -> str:
    """Remove lone surrogate code points that PyMuPDF sometimes leaves in PDF text."""
    if not s:
        return s
    return s.encode("utf-8", errors="surrogatepass").decode("utf-8", errors="replace")

# ── Thresholds for green / yellow / red colouring ─────────────────────────────
_GREEN  = {"self_contained": 0.80, "faithfulness": 0.85, "atomic": 0.70,
           "coverage": 0.60, "trivial_max": 0.10, "dup_max": 0.10,
           "understanding": 0.50}
_YELLOW = {"self_contained": 0.60, "faithfulness": 0.70, "atomic": 0.50,
           "coverage": 0.40, "trivial_max": 0.20, "dup_max": 0.20,
           "understanding": 0.30}


def _build_set_rows(set_results: list[SetMetrics]) -> list[dict]:
    rows = []
    for sm in set_results:
        rows.append({
            "topic": sm.topic,
            "level": sm.level or "—",
            "n_cards": len(sm.card_metrics),
            "self_contained": round(sm.pct_self_contained, 4),
            "faithfulness": round(sm.avg_faithfulness, 4),
            "atomic": round(sm.pct_atomic, 4),
            "understanding": round(sm.pct_understanding, 4),
            "trivial": round(sm.pct_trivial, 4),
            "dup_rate": round(sm.duplicate_rate, 4),
            "coverage": round(sm.coverage_ratio, 4),
            "material_type": sm.material_type or "—",
            "spearman": round(sm.difficulty_spearman, 3) if sm.difficulty_spearman is not None else None,
            "avg_back_sentences": round(sm.avg_back_length, 1),
            "card_type_dist": sm.card_type_distribution,
            "dup_pairs": [
                {"a": p.card_a, "b": p.card_b, "sim": round(p.similarity, 3)}
                for p in sm.duplicate_pairs
            ],
            "key_concepts": sm.coverage_key_concepts,
            "covered_concepts": sm.coverage_covered,
        })
    return rows


def _build_card_rows(set_results: list[SetMetrics]) -> list[dict]:
    rows = []
    for sm in set_results:
        for cm in sm.card_metrics:
            sc = cm.self_contained
            faith = cm.faithfulness

            sc_note = ""
            if sc and not sc.passes:
                sc_note = sc.whats_missing or ("not understandable" if not sc.understandable else "")

            bad_claims = []
            if faith:
                bad_claims = [
                    {"claim": c.claim[:100], "status": c.status, "quote": c.quote[:80]}
                    for c in faith.claims if c.status != "supported"
                ]

            rows.append({
                "topic": _clean(sm.topic),
                "level": sm.level or "—",
                "num": cm.card_number,
                "front": _clean(cm.front),
                "back": _clean(cm.back[:300]),
                "sc_passes": int(sc.passes) if sc else -1,
                "sc_note": _clean(sc_note),
                "blind_matches": int(sc.blind_answer_matches) if sc else -1,
                "faith_ratio": round(faith.ratio, 3) if faith else -1,
                "faith_unsupported": faith.unsupported if faith else 0,
                "faith_contradicts": faith.contradicts if faith else 0,
                "bad_claims": [
                    {"claim": _clean(bc["claim"]), "status": bc["status"], "quote": _clean(bc["quote"])}
                    for bc in bad_claims
                ],
                "leaks": int(cm.front_leaks_answer) if cm.front_leaks_answer is not None else -1,
                "atomic": int(cm.atomic) if cm.atomic is not None else -1,
                "card_type": cm.card_type_label,
                "u_v_r": cm.understanding_vs_rote,
                "trivial": int(cm.trivial) if cm.trivial is not None else -1,
                "back_sentences": cm.back_length_sentences,
                "difficulty": cm.difficulty or 0,
            })
    return rows


# ── HTML template — uses @@PLACEHOLDER@@ tokens for Python substitution ────────
# All JavaScript curly braces are left literal; Python never sees them via .format().
_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Flashcard Report — @@TITLE@@</title>
<style>
:root {
  --bg:#0f1117;--surface:#1a1d27;--surface2:#22263a;--border:#2e3250;
  --text:#e2e8f0;--muted:#8892b0;--green:#22c55e;--yellow:#f59e0b;
  --red:#ef4444;--blue:#60a5fa;--purple:#a78bfa;--accent:#38bdf8;
  font-family:'Segoe UI',system-ui,-apple-system,sans-serif;
}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--text);padding:24px;min-height:100vh}
h1{font-size:1.6rem;color:var(--accent);margin-bottom:4px}
h2{font-size:1.15rem;color:var(--blue);margin:28px 0 12px;border-bottom:1px solid var(--border);padding-bottom:6px}
h3{font-size:0.95rem;color:var(--purple);margin:16px 0 8px}
.meta{color:var(--muted);font-size:0.82rem;margin-bottom:20px}
.meta span{margin-right:24px}
.meta .cost{color:var(--green);font-weight:600}
.summary-wrap{overflow-x:auto}
table.summary{border-collapse:collapse;width:100%;font-size:0.82rem}
table.summary th{background:var(--surface2);color:var(--muted);padding:8px 10px;text-align:left;border-bottom:2px solid var(--border);white-space:nowrap}
table.summary td{padding:7px 10px;border-bottom:1px solid var(--border)}
table.summary tr:hover{background:var(--surface2)}
.cell-green{color:var(--green);font-weight:600}
.cell-yellow{color:var(--yellow);font-weight:600}
.cell-red{color:var(--red);font-weight:600}
.filter-bar{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:14px;align-items:center}
.filter-bar label{color:var(--muted);font-size:0.8rem}
.filter-bar input,.filter-bar select{background:var(--surface);border:1px solid var(--border);color:var(--text);padding:5px 10px;border-radius:6px;font-size:0.82rem;outline:none}
.filter-bar input:focus,.filter-bar select:focus{border-color:var(--accent)}
.btn{background:var(--surface2);border:1px solid var(--border);color:var(--accent);padding:5px 14px;border-radius:6px;cursor:pointer;font-size:0.82rem;transition:background 0.15s}
.btn:hover{background:var(--border)}
.btn.active{background:var(--accent);color:#000;border-color:var(--accent)}
.cards-wrap{overflow-x:auto;max-height:640px;overflow-y:auto}
table.cards{border-collapse:collapse;width:100%;font-size:0.78rem}
table.cards th{background:var(--surface2);color:var(--muted);padding:7px 8px;text-align:left;border-bottom:2px solid var(--border);white-space:nowrap;position:sticky;top:0;z-index:2;cursor:pointer;user-select:none}
table.cards th:hover{color:var(--accent)}
table.cards th::after{content:' \u21d5';opacity:0.4;font-size:0.7rem}
table.cards th.asc::after{content:' \u2191';opacity:1;color:var(--accent)}
table.cards th.desc::after{content:' \u2193';opacity:1;color:var(--accent)}
table.cards td{padding:6px 8px;border-bottom:1px solid var(--border);vertical-align:top}
table.cards tr:hover{background:var(--surface)}
table.cards tr.hidden{display:none}
.badge{display:inline-block;padding:2px 7px;border-radius:10px;font-size:0.72rem;font-weight:600}
.badge-pass{background:#14532d;color:var(--green)}
.badge-fail{background:#450a0a;color:var(--red)}
.badge-na{background:var(--surface2);color:var(--muted)}
.note{color:var(--yellow);font-size:0.74rem;margin-top:3px;font-style:italic}
.claim-bad{color:var(--red);font-size:0.73rem;margin-top:2px}
.claim-bad .ql{color:var(--muted);font-style:italic}
.front-text{max-width:260px;white-space:pre-wrap;word-break:break-word}
.back-text{max-width:220px;white-space:pre-wrap;word-break:break-word;color:var(--muted)}
td.num{text-align:center;color:var(--muted)}
.dist-grid{display:flex;flex-wrap:wrap;gap:20px;margin-top:10px}
.dist-box{background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:14px 18px;min-width:220px;flex:1}
.dist-row{display:flex;align-items:center;gap:8px;margin-bottom:6px;font-size:0.8rem}
.dist-bar-wrap{flex:1;background:var(--surface2);border-radius:4px;height:10px;overflow:hidden}
.dist-bar{height:100%;border-radius:4px;background:var(--blue);transition:width 0.3s}
.dist-label{width:140px;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.dist-pct{width:38px;text-align:right;color:var(--text);font-weight:500;font-size:0.76rem}
.concept-grid{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}
.concept-chip{padding:3px 10px;border-radius:12px;font-size:0.75rem}
.chip-covered{background:#14532d;color:var(--green)}
.chip-miss{background:#450a0a;color:var(--red)}
</style>
</head>
<body>
<h1>&#x1F4CA; Flashcard Evaluation Report</h1>
<div class="meta">
  <span>Generated: <strong>@@GENERATED@@</strong></span>
  <span>Model: <strong>@@MODEL@@</strong></span>
  <span>Tokens: <strong>@@TOTAL_TOKENS@@</strong></span>
  <span class="cost">Cost: <strong>$@@COST@@</strong></span>
</div>

<h2>Set-Level Summary</h2>
<div class="summary-wrap">
<table class="summary">
<thead><tr>
  <th>Topic</th><th>Level</th><th>N</th>
  <th>Self-Contained</th><th>Faithfulness</th><th>Atomic</th>
  <th>Understanding</th><th>Trivial</th><th>Duplicates</th>
  <th>Coverage</th><th>Material</th><th>Spearman r</th><th>Avg sent.</th>
</tr></thead>
<tbody id="summary-body"></tbody>
</table>
</div>

<h2>Card-Level Detail</h2>
<div class="filter-bar">
  <label>Search: <input type="text" id="search-box" placeholder="front / back text&hellip;" oninput="applyFilters()"></label>
  <label>Set: <select id="filter-set" onchange="applyFilters()"><option value="">All sets</option></select></label>
  <button class="btn" id="btn-failed"     onclick="toggleFilter('failed')"    >Only failed cards</button>
  <button class="btn" id="btn-sc-fail"    onclick="toggleFilter('sc-fail')"   >SC fails</button>
  <button class="btn" id="btn-faith-fail" onclick="toggleFilter('faith-fail')">Faith fails</button>
  <button class="btn" id="btn-trivial"    onclick="toggleFilter('trivial')"   >Trivial</button>
  <button class="btn" id="btn-leaks"      onclick="toggleFilter('leaks')"     >Leaks answer</button>
  <button class="btn" id="btn-dup"        onclick="toggleFilter('dup')"       >Duplicates</button>
  <button class="btn" onclick="clearFilters()">Clear</button>
  <span id="visible-count" style="color:var(--muted);font-size:0.8rem;margin-left:auto"></span>
</div>
<div class="cards-wrap">
<table class="cards" id="cards-table">
<thead><tr>
  <th onclick="sortTable(0)">#</th>
  <th onclick="sortTable(1)">Set</th>
  <th>Front</th><th>Back / Notes</th>
  <th onclick="sortTable(4)">SC</th>
  <th onclick="sortTable(5)">Faith%</th>
  <th onclick="sortTable(6)">Leaks</th>
  <th onclick="sortTable(7)">Atomic</th>
  <th onclick="sortTable(8)">Type</th>
  <th onclick="sortTable(9)">U/R</th>
  <th onclick="sortTable(10)">Trivial</th>
  <th onclick="sortTable(11)">Sent.</th>
  <th onclick="sortTable(12)">Diff.</th>
</tr></thead>
<tbody id="cards-body"></tbody>
</table>
</div>

<h2>Card-Type Distribution per Set</h2>
<div class="dist-grid" id="dist-grid"></div>

<h2>Coverage per Set</h2>
<div id="coverage-section"></div>

<script>
const SETS  = @@SETS_JSON@@;
const CARDS = @@CARDS_JSON@@;
const DUP_MAP = @@DUP_JSON@@;

// colour helpers
function pctColor(v,gT,yT,lowerBetter){
  if(lowerBetter){
    if(v<=gT) return 'cell-green';
    if(v<=yT) return 'cell-yellow';
    return 'cell-red';
  }
  if(v>=gT) return 'cell-green';
  if(v>=yT) return 'cell-yellow';
  return 'cell-red';
}
function pct(v){ return (v*100).toFixed(1)+'%'; }
function badge(val,ok,fail){
  if(val===1) return '<span class="badge badge-pass">'+ok+'</span>';
  if(val===0) return '<span class="badge badge-fail">'+fail+'</span>';
  return '<span class="badge badge-na">&mdash;</span>';
}
function escHtml(s){
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

// build summary
function buildSummary(){
  const tb=document.getElementById('summary-body');
  SETS.forEach(function(s){
    const tr=document.createElement('tr');
    tr.innerHTML=
      '<td>'+escHtml(s.topic)+'</td>'+
      '<td>'+escHtml(s.level)+'</td>'+
      '<td style="text-align:center">'+s.n_cards+'</td>'+
      '<td class="'+pctColor(s.self_contained,.8,.6,false)+'">'+pct(s.self_contained)+'</td>'+
      '<td class="'+pctColor(s.faithfulness,.85,.7,false)+'">'+pct(s.faithfulness)+'</td>'+
      '<td class="'+pctColor(s.atomic,.7,.5,false)+'">'+pct(s.atomic)+'</td>'+
      '<td class="'+pctColor(s.understanding,.5,.3,false)+'">'+pct(s.understanding)+'</td>'+
      '<td class="'+pctColor(s.trivial,.1,.2,true)+'">'+pct(s.trivial)+'</td>'+
      '<td class="'+pctColor(s.dup_rate,.1,.2,true)+'">'+pct(s.dup_rate)+'</td>'+
      '<td class="'+pctColor(s.coverage,.6,.4,false)+'">'+pct(s.coverage)+'</td>'+
      '<td>'+escHtml(s.material_type)+'</td>'+
      '<td>'+(s.spearman!==null?s.spearman.toFixed(3):'&mdash;')+'</td>'+
      '<td style="text-align:center">'+s.avg_back_sentences+'</td>';
    tb.appendChild(tr);
  });
}

// populate set filter dropdown
function buildSetFilter(){
  const sel=document.getElementById('filter-set');
  const seen=new Set();
  SETS.forEach(function(s){
    const k=s.topic+' '+s.level;
    if(!seen.has(k)){
      seen.add(k);
      const o=document.createElement('option');
      o.value=k; o.textContent=k;
      sel.appendChild(o);
    }
  });
}

// which cards are duplicates
const DUP_CARDS=new Set();
Object.values(DUP_MAP).forEach(function(pairs){
  pairs.forEach(function(p){ DUP_CARDS.add(p.a); DUP_CARDS.add(p.b); });
});

// build card rows
function buildCards(){
  const tb=document.getElementById('cards-body');
  CARDS.forEach(function(c){
    const isDup=DUP_CARDS.has(c.num);
    const isFailed=(c.sc_passes===0||c.faith_ratio<0.7||c.trivial===1||c.leaks===1||isDup);
    const faithColor=c.faith_ratio>=0.85?'#22c55e':c.faith_ratio>=0.7?'#f59e0b':'#ef4444';
    let claimsHtml='';
    if(c.bad_claims&&c.bad_claims.length){
      claimsHtml=c.bad_claims.map(function(cl){
        return '<div class="claim-bad">\u26a0 '+escHtml(cl.status)+': '+escHtml(cl.claim)+
          (cl.quote?'<span class="ql"> &mdash; &ldquo;'+escHtml(cl.quote)+'&rdquo;</span>':'')+
          '</div>';
      }).join('');
    }
    const tr=document.createElement('tr');
    tr.dataset.set=c.topic+' '+c.level;
    tr.dataset.failed=isFailed?'1':'0';
    tr.dataset.scfail=c.sc_passes===0?'1':'0';
    tr.dataset.faithfail=(c.faith_ratio>=0&&c.faith_ratio<0.85)?'1':'0';
    tr.dataset.trivial=c.trivial===1?'1':'0';
    tr.dataset.leaks=c.leaks===1?'1':'0';
    tr.dataset.dup=isDup?'1':'0';
    tr.dataset.fronttext=c.front.toLowerCase();
    tr.dataset.backtext=c.back.toLowerCase();
    tr.innerHTML=
      '<td class="num">'+c.num+'</td>'+
      '<td style="white-space:nowrap;color:var(--muted);font-size:0.74rem">'+escHtml(c.topic)+'<br>'+escHtml(c.level)+'</td>'+
      '<td><div class="front-text">'+escHtml(c.front)+'</div>'+
        (c.sc_note?'<div class="note">\u26a0 '+escHtml(c.sc_note)+'</div>':'')+
      '</td>'+
      '<td><div class="back-text">'+escHtml(c.back)+'</div>'+claimsHtml+'</td>'+
      '<td>'+badge(c.sc_passes,'\u2713','\u2717')+'</td>'+
      '<td style="color:'+faithColor+';font-weight:600">'+(c.faith_ratio>=0?pct(c.faith_ratio):'&mdash;')+'</td>'+
      '<td>'+badge(c.leaks===1?0:c.leaks===0?1:-1,'\u2713','!')+'</td>'+
      '<td>'+badge(c.atomic,'\u2713','\u2717')+'</td>'+
      '<td><span style="font-size:0.74rem;color:var(--purple)">'+escHtml(c.card_type||'&mdash;')+'</span></td>'+
      '<td><span style="font-size:0.74rem;color:'+(c.u_v_r==='understanding'?'var(--green)':'var(--yellow)')+'">'+escHtml(c.u_v_r||'&mdash;')+'</span></td>'+
      '<td>'+badge(c.trivial===1?0:c.trivial===0?1:-1,'\u2713','\uD83D\uDDD1')+'</td>'+
      '<td class="num">'+c.back_sentences+'</td>'+
      '<td class="num" style="color:var(--accent)">'+(c.difficulty||'&mdash;')+'</td>';
    tb.appendChild(tr);
  });
  updateCount();
}

// filtering
var activeFilters=new Set();
function toggleFilter(name){
  var btn=document.getElementById('btn-'+name);
  if(activeFilters.has(name)){activeFilters.delete(name);btn.classList.remove('active');}
  else{activeFilters.add(name);btn.classList.add('active');}
  applyFilters();
}
function clearFilters(){
  activeFilters.clear();
  document.querySelectorAll('.btn').forEach(function(b){b.classList.remove('active');});
  document.getElementById('search-box').value='';
  document.getElementById('filter-set').value='';
  applyFilters();
}
function applyFilters(){
  var search=document.getElementById('search-box').value.toLowerCase();
  var setFilter=document.getElementById('filter-set').value;
  document.querySelectorAll('#cards-body tr').forEach(function(tr){
    var show=true;
    if(search&&!tr.dataset.fronttext.includes(search)&&!tr.dataset.backtext.includes(search)) show=false;
    if(setFilter&&tr.dataset.set!==setFilter) show=false;
    if(activeFilters.has('failed')    &&tr.dataset.failed!=='1')    show=false;
    if(activeFilters.has('sc-fail')   &&tr.dataset.scfail!=='1')    show=false;
    if(activeFilters.has('faith-fail')&&tr.dataset.faithfail!=='1') show=false;
    if(activeFilters.has('trivial')   &&tr.dataset.trivial!=='1')   show=false;
    if(activeFilters.has('leaks')     &&tr.dataset.leaks!=='1')     show=false;
    if(activeFilters.has('dup')       &&tr.dataset.dup!=='1')       show=false;
    tr.classList.toggle('hidden',!show);
  });
  updateCount();
}
function updateCount(){
  var total=document.querySelectorAll('#cards-body tr').length;
  var visible=document.querySelectorAll('#cards-body tr:not(.hidden)').length;
  document.getElementById('visible-count').textContent='Showing '+visible+' / '+total+' cards';
}

// sorting
var sortCol=-1,sortAsc=true;
function sortTable(col){
  var ths=document.querySelectorAll('#cards-table thead th');
  ths.forEach(function(th){th.classList.remove('asc','desc');});
  if(sortCol===col) sortAsc=!sortAsc; else{sortCol=col;sortAsc=true;}
  ths[col].classList.add(sortAsc?'asc':'desc');
  var tb=document.getElementById('cards-body');
  var rows=Array.from(tb.querySelectorAll('tr'));
  rows.sort(function(a,b){
    var av=a.cells[col]?a.cells[col].textContent.trim():'';
    var bv=b.cells[col]?b.cells[col].textContent.trim():'';
    var an=parseFloat(av),bn=parseFloat(bv);
    var cmp=isNaN(an)||isNaN(bn)?av.localeCompare(bv):an-bn;
    return sortAsc?cmp:-cmp;
  });
  rows.forEach(function(r){tb.appendChild(r);});
}

// card-type distribution bars
function buildDist(){
  var grid=document.getElementById('dist-grid');
  SETS.forEach(function(s){
    if(!s.card_type_dist||!Object.keys(s.card_type_dist).length) return;
    var box=document.createElement('div');
    box.className='dist-box';
    var title=document.createElement('h3');
    title.textContent=s.topic+(s.level!=='—'?' \u00b7 '+s.level:'');
    box.appendChild(title);
    var sub=document.createElement('div');
    sub.style.cssText='color:var(--muted);font-size:0.75rem;margin-bottom:10px';
    sub.textContent='Material: '+s.material_type;
    box.appendChild(sub);
    Object.entries(s.card_type_dist).sort(function(a,b){return b[1]-a[1];}).forEach(function(entry){
      var type=entry[0],frac=entry[1];
      var row=document.createElement('div');
      row.className='dist-row';
      row.innerHTML='<div class="dist-label" title="'+escHtml(type)+'">'+escHtml(type)+'</div>'+
        '<div class="dist-bar-wrap"><div class="dist-bar" style="width:'+(frac*100).toFixed(1)+'%"></div></div>'+
        '<div class="dist-pct">'+(frac*100).toFixed(0)+'%</div>';
      box.appendChild(row);
    });
    grid.appendChild(box);
  });
}

// coverage chips
function buildCoverage(){
  var section=document.getElementById('coverage-section');
  SETS.forEach(function(s){
    if(!s.key_concepts||!s.key_concepts.length) return;
    var covSet=new Set(s.covered_concepts);
    var div=document.createElement('div');
    div.style.marginBottom='20px';
    var h=document.createElement('h3');
    h.textContent=s.topic+(s.level!=='—'?' \u00b7 '+s.level:'')+
      '  ('+s.covered_concepts.length+'/'+s.key_concepts.length+')';
    div.appendChild(h);
    var chipGrid=document.createElement('div');
    chipGrid.className='concept-grid';
    s.key_concepts.forEach(function(c){
      var chip=document.createElement('span');
      chip.className='concept-chip '+(covSet.has(c)?'chip-covered':'chip-miss');
      chip.textContent=(covSet.has(c)?'\u2713 ':'\u2717 ')+c;
      chipGrid.appendChild(chip);
    });
    div.appendChild(chipGrid);
    section.appendChild(div);
  });
}

buildSummary();
buildSetFilter();
buildCards();
buildDist();
buildCoverage();
applyFilters();
</script>
</body>
</html>
"""


def write_report(
    set_results: list[SetMetrics],
    output_dir: Path,
    timestamp: str,
) -> Path:
    """
    Generate a self-contained HTML report.  Returns path to results/report.html.
    """
    results_dir = config.RESULTS_DIR
    results_dir.mkdir(parents=True, exist_ok=True)
    report_path = results_dir / "report.html"

    stats = get_token_stats()
    set_rows  = _build_set_rows(set_results)
    card_rows = _build_card_rows(set_results)

    dup_map: dict[str, list] = {}
    for sm in set_results:
        key = f"{sm.topic} {sm.level or '—'}"
        dup_map[key] = [
            {"a": p.card_a, "b": p.card_b, "sim": round(p.similarity, 3)}
            for p in sm.duplicate_pairs
        ]

    # Use simple token replacement — avoids conflicts with JS curly braces
    html = _HTML_TEMPLATE
    html = html.replace("@@TITLE@@",        timestamp)
    html = html.replace("@@GENERATED@@",    datetime.now().strftime("%Y-%m-%d %H:%M"))
    html = html.replace("@@MODEL@@",        config.JUDGE_MODEL)
    html = html.replace("@@TOTAL_TOKENS@@", f"{stats['total_tokens']:,}")
    html = html.replace("@@COST@@",         f"{stats['estimated_cost_usd']:.4f}")
    html = html.replace("@@SETS_JSON@@",    json.dumps(set_rows,  ensure_ascii=False))
    html = html.replace("@@CARDS_JSON@@",   json.dumps(card_rows, ensure_ascii=False))
    html = html.replace("@@DUP_JSON@@",     json.dumps(dup_map,   ensure_ascii=False))

    # Sanitize surrogate code points that PyMuPDF can leave in PDF-extracted text
    html_bytes = html.encode("utf-8", errors="surrogatepass")
    html_clean = html_bytes.decode("utf-8", errors="replace")
    report_path.write_text(html_clean, encoding="utf-8")
    return report_path
