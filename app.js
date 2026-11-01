/* Buildless quality lab. No network calls, secrets or paid model requests. */
"use strict";
const $ = (id) => document.getElementById(id);
const esc = (value) =>
  String(value ?? "").replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        c
      ],
  );
const clone = (value) => JSON.parse(JSON.stringify(value));
const KEY = "mathpdf-quality-lab-v1";
let db = clone(window.MATHPDF_DATA),
  storageOK = true;
try {
  const stored = localStorage.getItem(KEY);
  if (stored) db = validate(JSON.parse(stored));
} catch {
  storageOK = false;
}
let view = "reviews",
  current = db.versions.at(-1)?.id || "v4",
  baseline = db.versions.at(-2)?.id || "v3",
  topic = "all",
  cardVersion = "all",
  query = "",
  onlyProblems = false,
  issueVersion = "v4",
  issueState = "open",
  cardPage = 0,
  editId = null,
  editOriginal = null;
const requestedVersion = new URLSearchParams(location.search).get('version');
if (db.versions.some(v => v.id === requestedVersion)) {
  current = cardVersion = issueVersion = requestedVersion;
}
const statuses = {
  draft: "Draft",
  review: "In review",
  accepted: "Accepted",
};
const topics = {
  Sets: "Sets",
  "Sets repeat B": "Sets · repeat B",
  "Mathematical Induction": "Mathematical induction",
  Proofs: "Proofs",
  Numbers: "Numbers",
};
const metrics = [
  {
    key: "sc",
    label: "Self-contained",
    hint: "Question understandable without the notes",
    high: true,
  },
  {
    key: "faith",
    label: "Source faithfulness",
    hint: "Claims supported by the source",
    high: true,
  },
  {
    key: "atomic",
    label: "Atomicity",
    hint: "One learning goal per card",
    high: true,
  },
  {
    key: "coverage",
    label: "Topic coverage",
    hint: "Share of key concepts in the set",
    high: true,
  },
  { key: "dup", label: "Duplicates", hint: "Lower is better", high: false },
  {
    key: "leaks",
    label: "Answer leakage",
    hint: "Lower is better",
    high: false,
  },
  {
    key: "understanding",
    label: "Understanding",
    hint: "Share of questions testing understanding",
    high: true,
  },
  {
    key: "trivial",
    label: "Trivial questions",
    hint: "Lower is better",
    high: false,
  },
];
function finite(v) {
  return typeof v === "number" && Number.isFinite(v);
}
function validate(data) {
  if (
    !data ||
    data.schema_version !== 1 ||
    !["versions", "records", "cards", "issues"].every((k) =>
      Array.isArray(data[k]),
    )
  )
    throw Error(
      "Unknown backup format. Expected Quality Lab schema_version: 1.",
    );
  for (const key of ["versions", "records", "cards", "issues"]) {
    const values = data[key].map((r) => r.id);
    if (
      values.some((id) => typeof id !== "string" || !id.trim()) ||
      new Set(values).size !== values.length
    )
      throw Error("Records must have unique IDs.");
  }
  const ids = new Set();
  for (const v of data.versions) {
    if (
      typeof v.id !== "string" ||
      !v.id.trim() ||
      ids.has(v.id) ||
      typeof v.title !== "string"
    )
      throw Error("Versions must have unique IDs and titles.");
    ids.add(v.id);
  }
  for (const r of data.records) {
    if (
      !ids.has(r.version) ||
      typeof r.topic !== "string" ||
      !Number.isInteger(r.n) ||
      r.n < 1
    )
      throw Error("Invalid result set.");
    for (const m of metricsSafe()) {
      if (r[m] != null && (!finite(r[m]) || r[m] < 0 || r[m] > 1))
        throw Error("Scores must be numbers between 0 and 1.");
    }
  }
  if (
    data.cards.some((c) => !ids.has(c.version)) ||
    data.issues.some((i) => !ids.has(i.version))
  )
    throw Error("A card or issue references an unknown version.");
  return data;
}
function metricsSafe() {
  return [
    "sc",
    "faith",
    "atomic",
    "coverage",
    "dup",
    "leaks",
    "understanding",
    "trivial",
  ];
}
function save() {
  try {
    localStorage.setItem(KEY, JSON.stringify(db));
    storageOK = true;
  } catch {
    storageOK = false;
    toast(
      "Browser storage failed. Export JSON to preserve your changes.",
    );
  }
  updateStorage();
}
function updateStorage() {
  $("storage-label").textContent = storageOK
    ? "Saved in this browser"
    : "Storage unavailable · export JSON";
}
function toast(message) {
  $("toast").textContent = message;
  $("toast").hidden = false;
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => ($("toast").hidden = true), 5000);
}
function pct(n) {
  return finite(n) ? `${(n * 100).toFixed(1)}%` : "—";
}
function fmt(n) {
  return finite(n) ? n.toFixed(1) : "—";
}
function name(t) {
  return topics[t] || t;
}
function versionOptions(selected, all = false) {
  return (
    (all ? '<option value="all">All versions</option>' : "") +
    db.versions
      .map(
        (v) =>
          `<option value="${esc(v.id)}" ${v.id === selected ? "selected" : ""}>${esc(v.id)}</option>`,
      )
      .join("")
  );
}
function topicOptions(selected) {
  return (
    '<option value="all">All topics</option>' +
    [...new Set(db.records.map((r) => r.topic))]
      .map(
        (t) =>
          `<option value="${esc(t)}" ${t === selected ? "selected" : ""}>${esc(name(t))}</option>`,
      )
      .join("")
  );
}
function selectedRecords(v) {
  return db.records.filter(
    (r) => r.version === v && (topic === "all" || r.topic === topic),
  );
}
function avg(rows, key) {
  const valid = rows.filter((r) => finite(r[key]));
  const n = valid.reduce((n, r) => n + r.n, 0);
  return n ? valid.reduce((sum, r) => sum + r[key] * r.n, 0) / n : null;
}
function sum(rows) {
  return rows.reduce((n, r) => n + r.n, 0);
}
function cohort(r) {
  return `${r.document || ""}|${r.topic}|${r.level || ""}|${(r.pages || "").replace(/[–—]/g, "-").replace(/\s/g, "")}`;
}
function matched(a, b) {
  const left = selectedRecords(a),
    right = selectedRecords(b);
  const unique = (rows, key) =>
    rows.filter((r) => cohort(r) === key).length === 1;
  const pairs = [];
  for (const r of right) {
    const k = cohort(r);
    const l = left.find((x) => cohort(x) === k);
    if (l && unique(left, k) && unique(right, k) && r.pages && r.document)
      pairs.push([l, r]);
  }
  return pairs;
}
function delta(a, b, high = true) {
  if (!finite(a) || !finite(b))
    return '<span class="neutral">no data</span>';
  const d = (b - a) * 100;
  const good = high ? d > 0 : d < 0;
  return `<span class="${Math.abs(d) < 0.05 ? "neutral" : good ? "good" : "bad"}">${d > 0 ? "+" : ""}${d.toFixed(1)} pp</span>`;
}
function summary(label, value, foot, accent = false) {
  return `<article class="summary-card ${accent ? "accent" : ""}"><span class="label">${label}</span><strong class="number">${value}</strong><span class="foot">${foot}</span></article>`;
}
function title(eyebrow, heading, description, extra = "") {
  return `<div class="heading"><div><span class="eyebrow">${eyebrow}</span><h1>${heading}</h1><p class="subline">${description}</p></div>${extra}</div>`;
}
function openVersion(id) {
  editId = id || null;
  const form = $("version-form");
  form.reset();
  const v = db.versions.find((v) => v.id === id) || {
    id: "",
    date: new Date().toLocaleDateString("en-CA"),
    title: "",
    status: "draft",
    notes: "",
    prompt: "",
  };
  editOriginal = clone(v);
  for (const key of ["id", "date", "title", "status", "notes", "prompt"])
    form.elements[key].value =
      (key === "title" || key === "notes" ? historical(v, key) : v[key]) || "";
  form.elements.id.readOnly = !!id;
  $("version-title").textContent = id ? `Edit ${id}` : "New version";
  $("form-error").hidden = true;
  renderScopes(db.records.filter((r) => r.version === id));
  $("version-dialog").showModal();
}
function renderScopes(rows) {
  $("set-scopes").innerHTML = rows.length
    ? "<h3>Sources for a fair comparison</h3>" +
      rows
        .map(
          (r, idx) =>
            `<div class=scope-row data-scope="${idx}"><strong>${esc(name(r.topic))} · ${esc(r.level || "No level")}</strong><div class=two-col><label>Source file<input name=document value="${esc(r.document || "")}" placeholder="main (9).pdf"></label><label>Pages<input name=pages value="${esc(r.pages || "")}" placeholder="4–7"></label></div></div>`,
        )
        .join("")
    : "";
}
$("version-form").elements.csv.onchange = async (e) => {
  try {
    const file = e.target.files[0];
    if (!file) return;
    if (file.size > 10000000) throw Error("CSV is too large.");
    renderScopes(
      fromCSV(await file.text(), $("version-form").elements.id.value.trim())
        .records,
    );
  } catch (error) {
    $("form-error").textContent = error.message;
    $("form-error").hidden = false;
  }
};
function parseCSV(text) {
  const rows = [];
  let row = [],
    value = "",
    quoted = false;
  text = text.replace(/^\uFEFF/, "");
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (c === '"') {
      if (quoted && text[i + 1] === '"') {
        value += '"';
        i++;
      } else quoted = !quoted;
    } else if (c === "," && !quoted) {
      row.push(value);
      value = "";
    } else if ((c === "\n" || c === "\r") && !quoted) {
      if (c === "\r" && text[i + 1] === "\n") i++;
      row.push(value);
      if (row.some(Boolean)) rows.push(row);
      row = [];
      value = "";
    } else value += c;
  }
  if (quoted) throw Error("CSV contains unclosed quotes.");
  if (value || row.length) {
    row.push(value);
    rows.push(row);
  }
  if (rows.length < 2) throw Error("CSV contains no cards.");
  const headers = rows.shift();
  if (
    ![
      "set_topic",
      "card_number",
      "front_preview",
      "self_contained_passes",
      "faithfulness_ratio",
    ].every((k) => headers.includes(k))
  )
    throw Error("Expected cards_*.csv from flashcard-evaluator.");
  return rows.map((r) =>
    Object.fromEntries(headers.map((h, i) => [h, r[i] ?? ""])),
  );
}
function fromCSV(text, version) {
  const map = {
    topic: "set_topic",
    level: "set_level",
    number: "card_number",
    front: "front_preview",
    sc: "self_contained_passes",
    missing: "whats_missing",
    blind: "blind_answer_matches",
    faith: "faithfulness_ratio",
    unsupported: "faithfulness_unsupported",
    contradicts: "faithfulness_contradicts",
    leaks: "front_leaks_answer",
    atomic: "atomic",
    type: "card_type",
    understanding: "understanding_vs_rote",
    trivial: "trivial",
    sentences: "back_length_sentences",
    difficulty: "difficulty",
    sc_note: "judge_self_contained_note",
    faith_note: "judge_faithfulness_note",
  };
  const cards = parseCSV(text).map((r, i) => ({
    id: `${version}-import-${i + 1}`,
    version,
    ...Object.fromEntries(Object.entries(map).map(([k, v]) => [k, r[v] ?? ""])),
  }));
  const groups = new Map();
  cards.forEach((c) => {
    if (!c.topic || !c.front) throw Error("CSV is missing a topic or question.");
    for (const k of ["sc", "faith", "atomic", "leaks", "trivial"])
      if (
        c[k] !== "" &&
        (!Number.isFinite(Number(c[k])) || Number(c[k]) < 0 || Number(c[k]) > 1)
      )
        throw Error("CSV contains an invalid score.");
    const key = `${c.topic}|${c.level}`;
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(c);
  });
  const records = [...groups.values()].map((rows, i) => {
    const mean = (k, p = (v) => Number(v)) => {
      const nums = rows.filter((c) => c[k] !== "").map((c) => p(c[k]));
      return nums.length ? nums.reduce((a, b) => a + b, 0) / nums.length : null;
    };
    return {
      id: `${version}-set-${i + 1}`,
      version,
      topic: rows[0].topic,
      level: rows[0].level,
      n: rows.length,
      pages: "",
      sc: mean("sc"),
      faith: mean("faith"),
      atomic: mean("atomic"),
      leaks: mean("leaks"),
      trivial: mean("trivial"),
      understanding: mean("understanding", (v) =>
        v === "understanding" ? 1 : 0,
      ),
      coverage: null,
      dup: null,
      kind: "flashcards",
      document: "",
      source:
        "Imported per-card CSV; pages, duplicate rate and coverage unavailable",
    };
  });
  return { cards, records };
}
function merge(incoming) {
  const next = clone(db);
  for (const key of ["versions", "records", "cards", "issues"]) {
    const entries = new Map(next[key].map((x) => [x.id, x]));
    incoming[key].forEach((x) => {
      if (typeof x.id !== "string") throw Error("Each record must have an ID.");
      entries.set(x.id, x);
    });
    next[key] = [...entries.values()];
  }
  return validate(next);
}
$("issue-form").onsubmit = (e) => {
  e.preventDefault();
  const form = e.target;
  const issue = Object.fromEntries(
    [
      "version",
      "topic",
      "location",
      "category",
      "description",
      "severity",
      "evidence",
      "next",
    ].map((k) => [k, form.elements[k].value.trim()]),
  );
  issue.id = "manual-" + crypto.randomUUID();
  issue.status = "open";
  db.issues.push(issue);
  save();
  issueVersion = issue.version;
  issueState = "open";
  $("issue-dialog").close();
  render();
  toast("Issue added.");
};
$("new-run").onclick = () => openVersion();
$("version-form").onsubmit = async (e) => {
  e.preventDefault();
  const form = e.target;
  const button = form.querySelector("[type=submit]");
  button.disabled = true;
  try {
    const id = form.elements.id.value.trim();
    if (!id || (!editId && db.versions.some((v) => v.id === id)))
      throw Error("This version ID already exists. Choose a new ID.");
    const version = Object.fromEntries(
      ["date", "title", "status", "notes", "prompt"].map((k) => [
        k,
        form.elements[k].value,
      ]),
    );
    // Editing status must not replace original evidence with a display translation.
    for (const key of ["title", "notes"])
      if (editId && version[key] === historical(editOriginal, key))
        version[key] = editOriginal[key];
    version.id = id;
    const file = form.elements.csv.files[0];
    if (file && file.size > 10_000_000)
      throw Error("CSV exceeds 10 MB.");
    const result = file ? fromCSV(await file.text(), id) : null;
    const next = clone(db);
    const pos = next.versions.findIndex((v) => v.id === id);
    if (pos >= 0) next.versions[pos] = version;
    else next.versions.push(version);
    if (result) {
      next.records = next.records
        .filter((r) => r.version !== id)
        .concat(result.records);
      next.cards = next.cards
        .filter((c) => c.version !== id)
        .concat(result.cards);
    }
    document.querySelectorAll("[data-scope]").forEach((group) => {
      const r = next.records.filter((r) => r.version === id)[
        Number(group.dataset.scope)
      ];
      if (r) {
        r.pages = group.querySelector("[name=pages]").value.trim();
        r.document = group.querySelector("[name=document]").value.trim();
      }
    });
    db = validate(next);
    save();
    current = id;
    $("version-dialog").close();
    location.hash = "versions";
    render();
    toast("Version saved. Export JSON for a backup.");
  } catch (error) {
    $("form-error").textContent = error.message;
    $("form-error").hidden = false;
  } finally {
    button.disabled = false;
  }
};
$("backup").onclick = () => {
  const blob = new Blob([JSON.stringify(db, null, 2)], {
    type: "application/json",
  });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `acadence-metrics-${new Date().toISOString().slice(0, 10)}.json`;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
  toast("Backup exported.");
};
$("import-backup").onclick = () => $("backup-file").click();
$("backup-file").onchange = async (e) => {
  try {
    const file = e.target.files[0];
    if (!file) return;
    if (file.size > 15_000_000) throw Error("JSON exceeds 15 MB.");
    db = merge(validate(JSON.parse(await file.text())));
    save();
    render();
    toast("Data merged by ID.");
  } catch (error) {
    toast(error.message);
  } finally {
    e.target.value = "";
  }
};
document
  .querySelectorAll("[data-close]")
  .forEach((b) => (b.onclick = () => b.closest("dialog").close()));
window.addEventListener("hashchange", () => {
  render();
  window.scrollTo({ top: 0 });
});
render();
