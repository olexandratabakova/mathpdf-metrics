/* Published experiment evidence is separate from browser-local flashcard data. */
window.renderReviews = function () {
  const runs = window.MATHPDF_REVIEWS || [];
  const money = (value) => `$${Number(value).toFixed(5)}`;
  const stageNames = {
    generate: "Генерація",
    blind: "Незалежна перевірка умов",
    audit: "Перевірка розв’язків",
  };
  const verdicts = {
    accept: "Прийняти",
    revise: "Доопрацювати",
    reject: "Відхилити",
  };
  const statementNames = {
    well_posed: "Коректна умова",
    false_claim: "Хибне твердження",
    ambiguous: "Неоднозначна умова",
    not_supported: "Недостатня підтримка джерела",
  };
  $("main").innerHTML =
    title(
      "ОКРЕМИЙ ГЕНЕРАТОР І ПЕРЕВІРЯЛЬНИК",
      "Спочатку <em>перевірити.</em>",
      "Реальні API-експерименти: оригінальні задачі, незалежні висновки та прозорі витрати.",
    ) +
    (runs.length
      ? runs
          .map((run) => {
            const accepted = run.audit.items.filter(
              (x) => x.decision === "accept",
            ).length;
            return `<section class="experiment-run" id="${esc(run.id)}"><div class="panel experiment-intro"><div><span class="eyebrow">${esc(run.date)} · ${esc(run.id)}</span><h2>${esc(run.title)}</h2><p>${esc(run.summary)}</p><div class="experiment-flow"><span>GPT‑4.1 mini <small>4 задачі</small></span><b>→</b><span>GPT‑4.1 <small>лише умови</small></span><b>→</b><span>GPT‑4.1 <small>аудит розв’язків</small></span></div></div><div class="experiment-cost"><strong>${money(run.cost_usd)}</strong><span>3 виклики моделі · без повторів</span><a href="${esc(run.evidence_url)}" target="_blank" rel="noreferrer">JSON результатів ↗</a></div></div>
      <div class="summary-grid">${summary("Згенеровано", "4", "Оригінальні задачі збережено", true)}${summary("Перевіряльник: прийняти", String(accepted), "Рішення моделі, не гарантія істини")}${summary("Локальна перевірка: помилки", String(Object.values(run.manual_notes || {}).filter((x) => x.severity === "critical").length), "Пропущені перевіряльником дефекти")}${summary("Загальна вартість", money(run.cost_usd), "За usage і тарифами API")}</div>
      <div class="note">Джерело: ${esc(run.source.name)}, стор. ${run.source.pages.join(", ")}. Рівень ${run.difficulty}. Перевірка умов виконана без відповідей генератора. ${esc(run.limitations)}</div>
      <div class="section-head"><h2>Чотири задачі та висновки</h2><span class="small-label">Розв’язки й докази розгортаються окремо</span></div>
      ${run.problems
        .map((item, index) => {
          const id = index + 1,
            blind = run.blind.items.find((x) => x.problem_id === id),
            audit = run.audit.items.find((x) => x.problem_id === id);
          return `<article class="panel experiment-problem"><div class="experiment-problem-heading"><span class="eyebrow">ЗАДАЧА ${id}</span><span class="tag ${audit.decision === "reject" ? "red" : audit.decision === "revise" ? "warn" : ""}">Модель: ${esc(verdicts[audit.decision])}</span></div><h2>${esc(item.title)}</h2><div class="report-math" data-problem-question="${esc(run.id)}:${index}"></div>
      <div class="review-result"><h3>Незалежна перевірка умови</h3><span class="tag ${blind.statement_status === "well_posed" ? "" : "warn"}">${esc(statementNames[blind.statement_status])}</span><div class="review-prose" data-review-result="${esc(run.id)}:${index}"></div><details><summary>Незалежне обґрунтування</summary><div class="review-prose" data-review-evidence="${esc(run.id)}:${index}"></div></details></div>
      <div class="review-result"><h3>Аудит згенерованого розв’язку</h3><div class="review-checks"><span>${audit.statement_correct ? "✓" : "×"} Умова</span><span>${audit.solution_correct ? "✓" : "×"} Розв’язок</span><span>${audit.source_supported ? "✓" : "×"} Метод у конспекті</span><span>Новизна: ${esc({ substantive: "змістовна", cosmetic: "косметична", copied: "копія", uncertain: "невизначена" }[audit.novelty])}</span></div><div class="review-prose" data-audit-explanation="${esc(run.id)}:${index}"></div>${audit.issues.length ? `<ul class="review-issues">${audit.issues.map((x) => `<li>${esc(x)}</li>`).join("")}</ul>` : ""}${audit.suggested_fix ? `<details><summary>Пропозиція перевіряльника — не застосована</summary><div class="review-prose" data-audit-fix="${esc(run.id)}:${index}"></div></details>` : ""}</div>
      ${run.manual_notes?.[String(id)] ? `<div class="manual-finding"><span class="tag red">Локальна перевірка: пропущена помилка</span><div class="review-prose" data-manual-finding="${esc(run.id)}:${index}"></div></div>` : ""}<details class="original-solution"><summary>Оригінальний розв’язок GPT‑4.1 mini</summary><div class="report-math" data-problem-answer="${esc(run.id)}:${index}"></div></details></article>`;
        })
        .join("")}
      <section class="panel"><div class="panel-heading"><h2>Витрати й умови тесту</h2></div><div class="table-scroll"><table><thead><tr><th>ЕТАП</th><th>МОДЕЛЬ</th><th>INPUT</th><th>OUTPUT</th><th>USD</th></tr></thead><tbody>${run.calls.map((x) => `<tr><td>${esc(stageNames[x.stage])}</td><td>${esc(x.model)}</td><td>${x.input_tokens}</td><td>${x.output_tokens}</td><td>${money(x.cost_usd)}</td></tr>`).join("")}</tbody></table></div><div class="panel-body"><p class="hint">${esc(run.manual_review)}</p><details class="provenance"><summary>Походження та обмеження</summary><p>SHA‑256 конспекту: <code>${esc(run.source.sha256)}</code></p><p>JSON зберігає повні згенеровані блоки, обидві перевірки, назви моделей, usage та хеші промптів. Вихідний PDF та ключ API не публікуються. Дані v1–v4 і ваші локальні записи не перезаписані.</p><p><a href="https://developers.openai.com/api/docs/models/gpt-4.1" target="_blank" rel="noreferrer">Тариф GPT‑4.1 ↗</a> · <a href="https://developers.openai.com/api/docs/models/gpt-4.1-mini" target="_blank" rel="noreferrer">Тариф mini ↗</a></p></details></div></section></section>`;
          })
          .join("")
      : '<div class="panel empty">Ще немає опублікованих експериментів.</div>');
  const lookup = (token) => {
    const [id, index] = token.split(":");
    const run = runs.find((x) => x.id === id);
    return { run, index: Number(index), item: run.problems[Number(index)] };
  };
  const options = {
    editable: false,
    linkSources: false,
    sourceLabel: (ref) => `main (12).pdf · стор. ${ref.page}`,
  };
  for (const node of document.querySelectorAll("[data-problem-question]")) {
    const { item } = lookup(node.dataset.problemQuestion);
    MathPDF.renderBlocks(node, item.question, options);
  }
  for (const node of document.querySelectorAll("[data-problem-answer]")) {
    const { item } = lookup(node.dataset.problemAnswer);
    MathPDF.renderBlocks(node, item.answer, options);
  }
  for (const [attribute, getText] of [
    ["data-review-result", (r, i) => r.blind.items[i].independent_result],
    ["data-review-evidence", (r, i) => r.blind.items[i].evidence.join("\n\n")],
    ["data-audit-explanation", (r, i) => r.audit.items[i].explanation],
    ["data-audit-fix", (r, i) => r.audit.items[i].suggested_fix],
    ["data-manual-finding", (r, i) => r.manual_notes[String(i + 1)].text],
  ])
    for (const node of document.querySelectorAll(`[${attribute}]`)) {
      const { run, index } = lookup(node.getAttribute(attribute));
      MathPDF.renderBlocks(
        node,
        [{ kind: "text", text: getText(run, index) }],
        options,
      );
    }
};
