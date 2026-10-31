Create exactly $count distinct flashcards supported by the selected primary pages. Keep the existing schema. The question array contains one plain-English string; answer is []; the back is assembled from formula, from_notes and explanation.

PLAN SILENTLY
Inventory the important learning targets across the selected pages. Select distinct targets at the requested difficulty before writing cards. Each card tests one definition, condition, distinction, method or justified conclusion. Avoid two fronts that can be answered by the same explanation. Favor uncovered concepts over paraphrases of an earlier card. Do not output the inventory. Use insufficient_source rather than pad the count.

FRONT: COMPLETE QUESTION, HIDDEN ANSWER
State enough to identify the mathematical objects and task without the PDF, title or back. Never say “this formula”, “the proof”, “the example”, “the last step” or “sets mentioned above” unless the necessary information is supplied. Name the theorem or describe its actual assertion when asking about its proof. General recall questions may ask for a definition or conditions without revealing those answers first: “Under what conditions does a function have an inverse?” is a complete question.

Use words to express any essential mathematical givens because the front accepts plain English only. Preserve every exponent, sign, domain, inequality, quantifier and boundary condition. Say “two to the power n by two to the power n”, never “two n by two n”; say “the reciprocal of the square of k”, never “one slash k two”. Do not drop powers or operators while translating notation into prose. If a formula cannot be stated clearly in words without revealing the requested answer, choose a different learning target. Do not ask to prove an identity while leaving the identity only on the back. Do not add a condition that silently changes the source theorem.

The front asks, rather than answers. Do not include the requested definition, final formula, sufficient condition, worked steps or parenthetical solution hints. Do not add formula objects, inline TeX or numbered source references to the question array. A proof or comparison must have one focused conclusion, not a catalogue of unrelated facts.

BACK: SOURCE FIRST, REASONING ONLY WHEN NEEDED
formula is a reference to the source: use {"page": original_page} for prose-based facts. Use a central mathematical formula only if that exact expression is printed on the selected page and directly supports the target. Never invent symbolic notation merely to decorate a prose definition.

from_notes contains only the relevant source statement, verbatim or near-verbatim, with all qualifications and mathematical objects preserved. Do not present a generated example, inference, proof or correction as a quotation. Keep math inside typed formula objects or paragraph math parts as specified in the unchanged formula guide. Do not copy an entire paragraph of unrelated facts. The central formula is inserted automatically on the back; do not repeat it.

explanation is optional. Leave it empty when it would merely paraphrase the source answer. Otherwise give a short valid argument or clarification needed for this exact target, separate from quoted content. Keep the necessary reasoning; never replace it by “can be shown” or “simplifying gives the result”. Do not add unsourced generalizations, historical details or minimality claims. A sufficient bound need not be a minimum. One fact must not grow into a survey of related facts on the back.

FINAL SILENT AUDIT
For each candidate, compare the front in words, the source statement and the back. Verify they refer to the same mathematical claim with the same assumptions. Check simple boundary cases and counterexamples to added claims. Ask whether the learner can identify the task from the front alone, without being given the answer. Remove semantic duplicates by learning target, not wording. Replace a candidate that cannot be expressed faithfully and clearly; do not knowingly return a false or incomplete card. Keep title plain English without raw math delimiters.

Attachment page -> ORIGINAL document page: $page_mapping.
