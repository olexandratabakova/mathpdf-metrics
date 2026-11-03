Create exactly $count distinct source-supported flashcards using the existing schema and full technical formula guide. Keep answer: []. Do not copy serialized JSON into content. Silently select distinct targets across the selected pages before writing; never pad the count.

ONE TARGET
Each card has one independently assessable learning target. Do not combine union and intersection, injectivity/surjectivity/bijectivity definitions, or a catalogue of image/preimage laws. Select one. A single definition includes its necessary qualifications; a proof can have several dependent steps for one conclusion. A comparison targets one distinction, not two separate definition lists. Remove semantic repeats: if the same expected explanation answers two fronts, replace one with an uncovered target.

FRONT
Ask one short direct question, normally at most 25 words; essential assumptions take priority over length. State all objects, domains and givens needed without the PDF or back. Never refer to an unseen formula, previous step, example number or source-local object. Do not reveal the requested answer. Use words for front mathematics: “one divided by n squared”, “two to the power n”, never “1/n 2” or “two n”. Preserve powers, signs, quantifiers and boundary cases. Choose another target when words cannot express it faithfully. Keep titles short, plain English, without notation or TeX.

BACK: DIRECT ANSWER, THEN USEFUL REASON
from_notes is the shortest relevant source statement, verbatim or near-verbatim, with all necessary qualifications. It normally supplies the direct answer in 1–2 sentences. Use a page-only reference for prose; a central formula must be actually printed on that exact page and is displayed automatically, so do not repeat it. Never present an inference, invented example, interpretation or correction as source text. If the source has no direct answer, keep only the supporting statement here, or leave this field empty, and begin explanation with the derived answer.

explanation adds only what the first block lacks. For a definition, leave it empty unless a distinction genuinely needs clarification. For a why/proof/error/application target, supply the actual short argument, decisive counterexample or worked steps; a description of a proof is not the proof. Normally use 1–3 sentences, but never truncate necessary reasoning. Do not repeat or paraphrase the first block. Example: after a quoted definition of injectivity, “different inputs have different outputs” is redundant. For a composition proof, show equal composite outputs imply equal intermediate values, then equal inputs. Keep the initial answer easy to find; do not add general surveys or unrelated examples.

MATHEMATICAL AND SERIALIZATION CHECK
Use typed math objects for every back-side expression, including inside quotations; ordinary parts contain words only. Keep punctuation and prose outside math objects. A math object must contain only valid mathematics, never sentences, JSON fragments or repeated generated text. Preserve source symbols from the PDF image rather than copying broken extracted glyphs. Do not put TeX in titles or prose parts. Check each fragment independently. Verify exact citation pages and source/added-content roles.

Do not turn failure of one attempted proof into an impossibility theorem. For example, an induction estimate that fails to close only shows that this estimate is insufficient; explain its missing bound or give the stronger invariant. Test added claims against simple cases. Supply a precise construction when asked how to construct something, not “choose appropriately”.

LEVEL 3
For each five-card set, at least two cards must actually require conditions, application or error diagnosis; at most one may be recall. A definition question is recall even if labelled meaning. Meaning interprets a concept; application uses specified givens; error diagnosis identifies and corrects a stated error. A why question must require a reason. Other allowed skills: why_justification, counterexample, comparison. Choose skill before question and audit the actual reasoning, not the label. Order easier to harder without increasing verbosity. Return insufficient_source if distinct source-supported targets cannot meet the count and level.

Final silent audit: one target, independent front, direct answer, complete nonredundant reasoning, faithful mathematics, valid typed fields, exact page, no repeated target. Return only the schema result.

Attachment page -> ORIGINAL document page: $page_mapping.
