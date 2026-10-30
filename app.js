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
let view = "overview",
  current = db.versions.at(-1)?.id || "v4",
  baseline = db.versions.at(-2)?.id || "v3",
  topic = "all",
  cardVersion = "all",
  query = "",
  onlyProblems = false,
  issueVersion = "v4",
  issueState = "open",
  cardPage = 0,
  editId = null;
const statuses = {
  draft: "Чернетка",
  review: "На перевірці",
  accepted: "Прийнято",
};
const topics = {
  Sets: "Множини",
  "Sets repeat B": "Множини · повтор B",
  "Mathematical Induction": "Математична індукція",
  Proofs: "Доведення",
  Numbers: "Числа",
};
const metrics = [
  {
    key: "sc",
    label: "Самодостатність",
    hint: "Чи зрозуміле питання без конспекту",
    high: true,
  },
  {
    key: "faith",
    label: "Відповідність джерелу",
    hint: "Підтримані джерелом твердження",
    high: true,
  },
  {
    key: "atomic",
    label: "Один факт на картку",
    hint: "Атомарність навчальної цілі",
    high: true,
  },
  {
    key: "coverage",
    label: "Покриття теми",
    hint: "Частка ключових понять у наборі",
    high: true,
  },
  { key: "dup", label: "Дублікати", hint: "Менше — краще", high: false },
  {
    key: "leaks",
    label: "Підказки у питанні",
    hint: "Менше — краще",
    high: false,
  },
  {
    key: "understanding",
    label: "На розуміння",
    hint: "Частка питань на розуміння",
    high: true,
  },
  {
    key: "trivial",
    label: "Тривіальні питання",
    hint: "Менше — краще",
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
      "Невідомий формат резервної копії. Потрібен експорт Quality Lab schema_version: 1.",
    );
  for (const key of ["versions", "records", "cards", "issues"]) {
    const values = data[key].map((r) => r.id);
    if (
      values.some((id) => typeof id !== "string" || !id.trim()) ||
      new Set(values).size !== values.length
    )
      throw Error("Записи повинні мати унікальні ID.");
  }
  const ids = new Set();
  for (const v of data.versions) {
    if (
      typeof v.id !== "string" ||
      !v.id.trim() ||
      ids.has(v.id) ||
      typeof v.title !== "string"
    )
      throw Error("Версії повинні мати унікальні назви й заголовки.");
    ids.add(v.id);
  }
  for (const r of data.records) {
    if (
      !ids.has(r.version) ||
      typeof r.topic !== "string" ||
      !Number.isInteger(r.n) ||
      r.n < 1
    )
      throw Error("Некоректний набір результатів.");
    for (const m of metricsSafe()) {
      if (r[m] != null && (!finite(r[m]) || r[m] < 0 || r[m] > 1))
        throw Error("Оцінки повинні бути числами від 0 до 1.");
    }
  }
  if (
    data.cards.some((c) => !ids.has(c.version)) ||
    data.issues.some((i) => !ids.has(i.version))
  )
    throw Error("Картка або зауваження посилається на невідому версію.");
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
      "Не вдалося зберегти у браузері. Експортуйте JSON, щоб не втратити зміни.",
    );
  }
  updateStorage();
}
function updateStorage() {
  $("storage-label").textContent = storageOK
    ? "Дані у цьому браузері"
    : "Збереження недоступне · експортуйте JSON";
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
    (all ? '<option value="all">Усі версії</option>' : "") +
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
    '<option value="all">Усі теми</option>' +
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
    return '<span class="neutral">немає даних</span>';
  const d = (b - a) * 100;
  const good = high ? d > 0 : d < 0;
  return `<span class="${Math.abs(d) < 0.05 ? "neutral" : good ? "good" : "bad"}">${d > 0 ? "+" : ""}${d.toFixed(1)} в.п.</span>`;
}
function summary(label, value, foot, accent = false) {
  return `<article class="summary-card ${accent ? "accent" : ""}"><span class="label">${label}</span><strong class="number">${value}</strong><span class="foot">${foot}</span></article>`;
}
function title(eyebrow, heading, description, extra = "") {
  return `<div class="heading"><div><span class="eyebrow">${eyebrow}</span><h1>${heading}</h1><p class="subline">${description}</p></div>${extra}</div>`;
}
function comparison() {
  const pairs = matched(baseline, current),
    left = pairs.map((p) => p[0]),
    right = pairs.map((p) => p[1]);
  return `<section class="panel"><div class="panel-heading"><div><h2>Що змінилося?</h2><p>Однакові теми, рівні та сторінки джерела</p></div><div class="comparison-controls"><select id="baseline" aria-label="Базова версія">${versionOptions(baseline)}</select><span class="small-label">→</span><select id="current" aria-label="Поточна версія">${versionOptions(current)}</select></div></div><div class="panel-body"><div class="legend"><span>${esc(baseline)} · база</span><span>${esc(current)} · порівняння</span></div>${
    pairs.length
      ? metrics
          .slice(0, 5)
          .map((m) => {
            const a = avg(left, m.key),
              b = avg(right, m.key);
            return `<div class="metric-bar"><div class="bar-heading"><span>${m.label}${!m.high ? " ↓" : ""}</span><span class="diff">${pct(a)} → ${pct(b)} &nbsp; ${delta(a, b, m.high)}</span></div><div class="bar-pair"><div class="track"><div class="fill" style="width:${(a || 0) * 100}%"></div></div><div class="track"><div class="fill current" style="width:${(b || 0) * 100}%"></div></div></div></div>`;
          })
          .join("")
      : '<div class="empty">Немає зіставних наборів.<br>Оберіть версії з однаковою темою, рівнем і сторінками.</div>'
  }<div class="note compare-foot">${pairs.length ? `Зіставлено ${pairs.length} ${pairs.length === 1 ? "набір" : "набори"} · ${sum(left)} карток у ${esc(baseline)} та ${sum(right)} у ${esc(current)}. ${pairs.map((p) => esc(name(p[1].topic)) + " · " + esc(p[1].level || "без рівня") + " · стор. " + esc(p[1].pages)).join("; ")}. ` : ""}Різні вибірки не змішуємо. Зміни показані у відсоткових пунктах; це оцінки LLM, а не доказ математичної правильності.</div></div></section>`;
}
function overview() {
  const rows = selectedRecords(current),
    open = db.issues.filter(
      (i) => i.version === current && i.status !== "resolved",
    );
  $("main").innerHTML =
    title(
      "ЕКСПЕРИМЕНТИ, ЯКІ МОЖНА ПОРІВНЯТИ",
      "Якість у <em>деталях.</em>",
      "Усі версії, результати й висновки — в одному спокійному просторі.",
      `<span class="tag">Історичні оцінки · 29.10.2026</span>`,
    ) +
    `<div class="filters"><label>Тема <select id="topic">${topicOptions(topic)}</select></label><span class="count">${db.versions.length} версії · ${db.cards.length} карток в історії</span></div><div class="summary-grid">${summary("Вибрана версія", esc(current), `${rows.length} набори · ${sum(rows)} карток`, true)}${summary("Відповідність джерелу", pct(avg(rows, "faith")), "Зважено за кількістю карток")}${summary("Самодостатність", pct(avg(rows, "sc")), "Питання зрозумілі без конспекту")}${summary("Відкриті зауваження", String(open.length), "Ручна перевірка · картки та задачі")}</div><div class="split">${comparison()}<section class="panel"><div class="panel-heading"><div><span class="eyebrow">НА ЩО ЗВЕРНУТИ УВАГУ</span><h2 style="margin-top:8px">Наступний крок</h2></div><span class="mini-arrow">↗</span></div><div class="panel-body">${
      open
        .slice(0, 3)
        .map(
          (i) =>
            `<article class="focus-card"><span class="tag ${i.severity === "Критична" ? "red" : "warn"}">${esc(i.category)}</span><h3>${esc(i.topic)}</h3><p>${esc(i.description)}</p></article>`,
        )
        .join("") ||
      '<div class="empty">Для цієї версії немає відкритих зауважень. Це не означає, що її вже перевірено вручну.</div>'
    }<button class="text-button" data-go="issues" style="margin-top:16px">Відкрити ручну перевірку →</button></div></section></div><div class="section-head"><h2>Результати за темами <span class="muted">/ ${esc(current)}</span></h2><button class="text-button" data-go="versions">Уся історія →</button></div><section class="panel table-scroll"><table><thead><tr><th>ТЕМА / РІВЕНЬ</th><th>КАРТОК</th><th>ДЖЕРЕЛО</th><th>САМОСТІЙНІСТЬ</th><th>АТОМАРНІСТЬ</th><th>ПОКРИТТЯ</th><th>ДУБЛІКАТИ ↓</th></tr></thead><tbody>${rows.map((r) => `<tr><td><span class="table-title">${esc(name(r.topic))}</span><span class="cell-meta">${esc(r.level || "Рівень не зазначено")} · стор. ${esc(r.pages || "не зазначено")}</span></td><td>${r.n}</td><td>${pct(r.faith)}</td><td>${pct(r.sc)}</td><td>${pct(r.atomic)}</td><td>${pct(r.coverage)}</td><td>${pct(r.dup)}</td></tr>`).join("")}</tbody></table>${!rows.length ? '<div class="empty">Для цього фільтра ще немає оцінених наборів.</div>' : ""}</section><div class="callout">Версія може покращити один показник і погіршити інший. Перевіряйте конкретні картки та задачі перед тим, як позначити її «Прийнято».</div>`;
  $("baseline").onchange = (e) => {
    baseline = e.target.value;
    render();
  };
  $("current").onchange = (e) => {
    current = e.target.value;
    render();
  };
  $("topic").onchange = (e) => {
    topic = e.target.value;
    render();
  };
}
function versions() {
  $("main").innerHTML =
    title(
      "ВІД ГІПОТЕЗИ ДО РЕЗУЛЬТАТУ",
      "Історія <em>версій.</em>",
      "Фіксуйте точний промпт, зміни та висновки після кожного експерименту.",
    ) +
    `<div class="version-list">${[...db.versions]
      .reverse()
      .map((v) => {
        const rows = db.records.filter((r) => r.version === v.id);
        return `<article class="panel version-entry"><div class="version-id">${esc(v.id)}</div><div><span class="eyebrow">${esc(v.date || "Дата не вказана")}</span><h2>${esc(v.title)}</h2><p>${esc(v.notes || "Додайте гіпотезу та висновки після тесту.")}</p><div class="stats"><span>${rows.length} наборів / ${sum(rows)} карток</span><span>Джерело: ${pct(avg(rows, "faith"))}</span><span>Атомарність: ${pct(avg(rows, "atomic"))}</span></div><details><summary>${v.prompt ? "Знімок промпту" : "Знімок промпту не збережено"}</summary><pre>${esc(v.prompt || "Історичний результат не містить точного промпту. Поточні файли prompts/ — промпти оцінювача, а не підтверджені промпти генерації цієї версії.")}</pre></details></div><div class="actions"><span class="tag ${v.status === "accepted" ? "" : v.status === "draft" ? "neutral" : "warn"}">${esc(statuses[v.status] || "На перевірці")}</span><button class="quiet" data-edit="${esc(v.id)}">Редагувати</button><button class="text-button" data-select="${esc(v.id)}">Переглянути метрики →</button></div></article>`;
      })
      .join("")}</div>`;
  document
    .querySelectorAll("[data-edit]")
    .forEach((b) => (b.onclick = () => openVersion(b.dataset.edit)));
  document.querySelectorAll("[data-select]").forEach(
    (b) =>
      (b.onclick = () => {
        current = b.dataset.select;
        if (baseline === current)
          baseline = db.versions.find((v) => v.id !== current)?.id || current;
        location.hash = "overview";
      }),
  );
}
function hasProblem(c) {
  return (
    c.sc === "0" ||
    Number(c.faith) < 0.8 ||
    c.leaks === "1" ||
    c.atomic === "0" ||
    c.trivial === "1"
  );
}
function cards() {
  const rows = db.cards.filter(
    (c) =>
      (cardVersion === "all" || c.version === cardVersion) &&
      (!onlyProblems || hasProblem(c)) &&
      `${c.front} ${c.topic} ${c.missing}`
        .toLowerCase()
        .includes(query.toLowerCase()),
  );
  const size = 25;
  cardPage = Math.min(cardPage, Math.max(0, Math.ceil(rows.length / size) - 1));
  $("main").innerHTML =
    title(
      "ДИВІТЬСЯ НА САМІ ПИТАННЯ",
      "Картки під <em>лупою.</em>",
      "Знаходьте слабкі місця та дивіться, що саме вплинуло на оцінку.",
    ) +
    `<div class="filters"><input id="search" type="search" placeholder="Пошук у питаннях і темах…" aria-label="Пошук карток" value="${esc(query)}"><select id="card-version" aria-label="Версія карток">${versionOptions(cardVersion, true)}</select><label><input id="only-problems" type="checkbox" ${onlyProblems ? "checked" : ""}> Лише з сигналами проблем</label><span class="count">Знайдено ${rows.length} карток</span></div><section class="panel table-scroll"><table><thead><tr><th>ВЕРСІЯ / ТЕМА</th><th>ПИТАННЯ</th><th>ДЖЕРЕЛО</th><th>САМОСТІЙНІСТЬ</th><th>АТОМАРНІСТЬ</th><th></th></tr></thead><tbody>${rows
      .slice(cardPage * size, (cardPage + 1) * size)
      .map(
        (c) =>
          `<tr><td>${esc(c.version)} · #${esc(c.number)}<span class="cell-meta">${esc(name(c.topic))} · ${esc(c.level)}</span></td><td class="card-front">${esc(c.front)}</td><td>${pct(Number.isFinite(Number(c.faith)) && c.faith !== "" ? Number(c.faith) : null)}</td><td>${c.sc === "1" ? '<span class="good">Так</span>' : c.sc === "0" ? '<span class="bad">Ні</span>' : "—"}</td><td>${c.atomic === "1" ? "Так" : c.atomic === "0" ? "Ні" : "—"}</td><td><button class="text-button" data-card="${esc(c.id)}">Деталі ↗</button></td></tr>`,
      )
      .join(
        "",
      )}</tbody></table>${!rows.length ? '<div class="empty">Карток за цими фільтрами немає.</div>' : ""}<div class="pagination"><button id="prev" ${cardPage === 0 ? "disabled" : ""}>← Назад</button><span>${cardPage + 1} / ${Math.max(1, Math.ceil(rows.length / size))}</span><button id="next" ${(cardPage + 1) * size >= rows.length ? "disabled" : ""}>Далі →</button></div></section><p class="hint" style="margin-top:18px">Показані питання та збережені оцінки. Повних відповідей немає в історичному CSV. «Відповідність джерелу» не дорівнює математичній правильності.</p>`;
  $("search").oninput = (e) => {
    const pos = e.target.selectionStart;
    query = e.target.value;
    cardPage = 0;
    cards();
    $("search").focus();
    $("search").setSelectionRange(pos, pos);
  };
  $("card-version").onchange = (e) => {
    cardVersion = e.target.value;
    cardPage = 0;
    render();
  };
  $("only-problems").onchange = (e) => {
    onlyProblems = e.target.checked;
    cardPage = 0;
    render();
  };
  $("prev").onclick = () => {
    cardPage--;
    render();
  };
  $("next").onclick = () => {
    cardPage++;
    render();
  };
  document
    .querySelectorAll("[data-card]")
    .forEach((b) => (b.onclick = () => showCard(b.dataset.card)));
}
function showCard(id) {
  const c = db.cards.find((c) => c.id === id);
  $("card-title").textContent = `${c.version} · картка ${c.number}`;
  $("card-detail").innerHTML =
    `<span class="eyebrow">${esc(name(c.topic))} · ${esc(c.level)}</span><p class="detail-block">${esc(c.front)}</p><div class="note">${esc(c.missing || "Оцінювач не вказав відсутнього контексту.")}</div><div class="two-col"><p>Джерело: <strong>${pct(Number(c.faith))}</strong></p><p>Тип: <strong>${esc(c.type || "—")}</strong></p></div><h3>Коментарі оцінювача</h3><p class="detail-block">${esc([c.sc_note, c.faith_note].filter(Boolean).join("\n\n") || "Без додаткових коментарів.")}</p>`;
  $("card-dialog").showModal();
}
function issues() {
  const rows = db.issues.filter(
    (i) =>
      (issueVersion === "all" || i.version === issueVersion) &&
      (issueState === "all" || i.status === issueState),
  );
  $("main").innerHTML =
    title(
      "ЛЮДСЬКА ПЕРЕВІРКА МАЄ ЗНАЧЕННЯ",
      "Що ще <em>не працює.</em>",
      "Математичні помилки, форматування й висновки з ручного аудиту.",
    ) +
    `<div class="filters"><select id="issue-version" aria-label="Версія аудиту">${versionOptions(issueVersion, true)}</select><select id="issue-state" aria-label="Статус зауважень"><option value="open" ${issueState === "open" ? "selected" : ""}>Відкриті</option><option value="retest" ${issueState === "retest" ? "selected" : ""}>Потрібен повторний тест</option><option value="resolved" ${issueState === "resolved" ? "selected" : ""}>Перевірено виправлення</option><option value="all" ${issueState === "all" ? "selected" : ""}>Усі статуси</option></select><span class="count">${rows.length} зауважень</span><button id="new-issue" class="quiet">＋ Зауваження</button></div>${rows.map((i) => `<article class="panel issue-card"><div class="issue-top"><span class="tag neutral">${esc(i.version)}</span><span class="tag ${i.severity === "Критична" ? "red" : "warn"}">${esc(i.severity)}</span><span class="small-label">${esc(i.location)}</span><select aria-label="Статус ${esc(i.id)}" data-issue="${esc(i.id)}"><option value="open" ${i.status === "open" ? "selected" : ""}>Відкрито</option><option value="retest" ${i.status === "retest" ? "selected" : ""}>Повторний тест</option><option value="resolved" ${i.status === "resolved" ? "selected" : ""}>Виправлення перевірено</option></select></div><h2>${esc(i.topic)} · ${esc(i.category)}</h2><p>${esc(i.description)}</p><details><summary>Докази й наступний крок</summary><p>${esc(i.evidence)}</p><div class="note">${esc(i.next)}</div></details></article>`).join("") || '<div class="panel empty">За цими фільтрами немає зауважень.</div>'}`;
  $("new-issue").onclick = () => {
    $("issue-form").reset();
    $("issue-form").elements.version.innerHTML = versionOptions(
      issueVersion === "all" ? current : issueVersion,
    );
    $("issue-dialog").showModal();
  };
  $("issue-version").onchange = (e) => {
    issueVersion = e.target.value;
    render();
  };
  $("issue-state").onchange = (e) => {
    issueState = e.target.value;
    render();
  };
  document.querySelectorAll("[data-issue]").forEach(
    (s) =>
      (s.onchange = () => {
        db.issues.find((i) => i.id === s.dataset.issue).status = s.value;
        save();
        render();
        toast("Статус збережено у цьому браузері.");
      }),
  );
}
function guide() {
  $("main").innerHTML =
    title(
      "МЕНШЕ ШУМУ. БІЛЬШЕ ДОКАЗІВ.",
      "Ваша лабораторія <em>якості.</em>",
      "Простий цикл: зафіксувати версію → оцінити → порівняти → перевірити вручну.",
    ) +
    `<div class="guide-grid"><article class="panel"><h2>Додати наступну версію</h2><ol><li>Згенеруйте матеріали окремо від робочого MathPDF.</li><li>Запустіть evaluate для цієї вибірки.</li><li>Натисніть «Нова версія», вставте точний промпт і додайте cards_*.csv.</li><li>Порівняйте показники та перевірте задачі вручну.</li><li>Збережіть висновок і експортуйте JSON.</li></ol></article><article class="panel"><h2>Де зберігаються зміни</h2><p>Нові версії, промпти та статуси зберігаються лише у вашому браузері. Вони не завантажуються в GitHub автоматично.</p><p>«Експорт JSON» створює повну резервну копію. «Імпорт» об’єднує записи за ID; однакові ID замінюються імпортованими. Для публікації нового знімка: <code>python tools/publish_snapshot.py backup.json</code>, потім commit і push.</p></article><article class="panel"><h2>Чесне порівняння</h2><p>Порівнюємо лише однакові тему, рівень і сторінки джерела. Повторні набори з однаковим ключем виключені як неоднозначні. Ваги метрик — кількість карток; покриття також показане як зважене середнє наборів.</p><p>Одна генерація не доводить покращення. Збережіть PDF, модель, налаштування та точний промпт для повторних запусків.</p></article><article class="panel"><h2>Що є в історії</h2><p>v1: 160 карток; v2: 180; v3: 130; v4: 35. Різні вибірки не можна трактувати як єдиний чистий експеримент. Повтор Sets у v3 збережено окремо.</p><p>Знімки промптів історичних версій не були підтверджені. Нові PDF з функціями, обговорені пізніше, не оцінені цим набором метрик і не додані як «v5».</p></article></div><div class="section-head"><h2>Що означають показники</h2></div><section class="panel">${metrics.map((m) => `<div class="glossary-row"><strong>${m.label} ${m.high ? "↑" : "↓"}</strong><span>${m.hint}. ${m.high ? "Більше — краще." : "Менше — краще."}</span></div>`).join("")}<div class="glossary-row"><strong>LLM-оцінка ≠ істина</strong><span>Відповідність джерелу не перевіряє математичну правильність. Дублікати та покриття залежать від оцінювача. Ручні зауваження до задач не перетворюються на відсоткові метрики.</span></div></section>`;
}
function render() {
  view = ["overview", "versions", "cards", "issues", "guide"].includes(
    location.hash.slice(1),
  )
    ? location.hash.slice(1)
    : "overview";
  document.querySelectorAll("[data-view]").forEach((a) => {
    a.classList.toggle("active", a.dataset.view === view);
    if (a.dataset.view === view) a.setAttribute("aria-current", "page");
    else a.removeAttribute("aria-current");
  });
  $("breadcrumb").textContent = {
    overview: "Огляд якості",
    versions: "Версії та промпти",
    cards: "Картки",
    issues: "Ручна перевірка",
    guide: "Як це працює",
  }[view];
  $("issue-count").textContent = db.issues.filter(
    (i) => i.status !== "resolved",
  ).length;
  ({ overview, versions, cards, issues, guide })[view]();
  document
    .querySelectorAll("[data-go]")
    .forEach((b) => (b.onclick = () => (location.hash = b.dataset.go)));
  updateStorage();
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
  for (const key of ["id", "date", "title", "status", "notes", "prompt"])
    form.elements[key].value = v[key] || "";
  form.elements.id.readOnly = !!id;
  $("version-title").textContent = id ? `Редагувати ${id}` : "Нова версія";
  $("form-error").hidden = true;
  renderScopes(db.records.filter((r) => r.version === id));
  $("version-dialog").showModal();
}
function renderScopes(rows) {
  $("set-scopes").innerHTML = rows.length
    ? "<h3>Джерела для чесного порівняння</h3>" +
      rows
        .map(
          (r, idx) =>
            `<div class=scope-row data-scope="${idx}"><strong>${esc(name(r.topic))} · ${esc(r.level || "Без рівня")}</strong><div class=two-col><label>Файл джерела<input name=document value="${esc(r.document || "")}" placeholder="main (9).pdf"></label><label>Сторінки<input name=pages value="${esc(r.pages || "")}" placeholder="4–7"></label></div></div>`,
        )
        .join("")
    : "";
}
$("version-form").elements.csv.onchange = async (e) => {
  try {
    const file = e.target.files[0];
    if (!file) return;
    if (file.size > 10000000) throw Error("CSV завеликий.");
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
  if (quoted) throw Error("CSV має незакриті лапки.");
  if (value || row.length) {
    row.push(value);
    rows.push(row);
  }
  if (rows.length < 2) throw Error("CSV не містить карток.");
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
    throw Error("Потрібен cards_*.csv із flashcard-evaluator.");
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
    if (!c.topic || !c.front) throw Error("У CSV відсутні тема або питання.");
    for (const k of ["sc", "faith", "atomic", "leaks", "trivial"])
      if (
        c[k] !== "" &&
        (!Number.isFinite(Number(c[k])) || Number(c[k]) < 0 || Number(c[k]) > 1)
      )
        throw Error("CSV містить некоректну оцінку.");
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
      if (typeof x.id !== "string") throw Error("Кожен запис має мати ID.");
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
  toast("Зауваження додано.");
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
      throw Error("Версія з такою назвою вже існує. Оберіть нову назву.");
    const version = Object.fromEntries(
      ["date", "title", "status", "notes", "prompt"].map((k) => [
        k,
        form.elements[k].value,
      ]),
    );
    version.id = id;
    const file = form.elements.csv.files[0];
    if (file && file.size > 10_000_000)
      throw Error("CSV завеликий: максимум 10 MB.");
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
    toast("Версію збережено. Експортуйте JSON для резервної копії.");
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
  a.download = `mathpdf-metrics-${new Date().toISOString().slice(0, 10)}.json`;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
  toast("Резервну копію експортовано.");
};
$("import-backup").onclick = () => $("backup-file").click();
$("backup-file").onchange = async (e) => {
  try {
    const file = e.target.files[0];
    if (!file) return;
    if (file.size > 15_000_000) throw Error("JSON завеликий: максимум 15 MB.");
    db = merge(validate(JSON.parse(await file.text())));
    save();
    render();
    toast("Дані об’єднано за ID.");
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
