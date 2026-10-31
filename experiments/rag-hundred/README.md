# One hundred bounded analogs using two topic-selected PDFs

2026-10-31. Sources: **main (13).pdf**, Yurii Malitskyi's updated 74-page notes, and **Main (10).pdf**, Richard Hammack's *Book of Proof*, third edition / edition 3.4 (380 PDF pages). Production MathPDF is unchanged.

## Scope and source access

The user's instruction was to search by topic and not analyze either whole PDF. Contents and bookmarks were inspected first; only selected topic pages were then extracted. No whole-document text extraction, whole-PDF index or full-PDF model upload occurred. Private model context contains bounded excerpts of selected pages and a deduplicated curated example bank. The public report lists exact page-access manifests; source page text/PDFs are not published.

- Notes: 28 target pages; 34 unique pages accessed including contents, title and initial inspection of the added section.
- Book: 23 target pages; 39 unique pages accessed including front matter and page-number calibration.

Physical Book PDF pages differ from printed numbering by 12 in the cited body chapters. References explicitly distinguish PDF/printed pages. Supporting definitions/methods must not be read as claims that an example was copied verbatim from the book.

## What generated the tasks

Fifty curated, program-supported families, two distinct variants each: **100 tasks across 10 topics**. Thirty-seven families reuse earlier bounded experiments; thirteen were added after targeted inspection: four logic, three relations, three partial-order, and three updated-notes function families (parity, weak/strict monotonicity, rational domain). The new notes' “World of functions” section is about those properties, not counting functions. No unsupported construction of arbitrary irrational powers was added.

Questions, mathematical data and full solutions are built by reviewed programs from one formal record. GPT-4.1 mini only selects a family from retrieved candidates and explains the match. It does not freely write the mathematics. Logical variants can change a supported Boolean form, not merely a coefficient; every Boolean assignment is enumerated. Numeric duplicates are deterministically redrawn and seeds recorded. These are not 100 distinct problem types, nor an assessment of unconstrained LLM proof-writing.

Profiles, domains, prerequisites and expected test-family labels are manual. The retriever filters topic/domain/prerequisites and uses BM25. Labels never enter either model request. Requests are shared across a batch; candidate examples are deduplicated to save tokens, but selection is checked against the candidate list of each individual request. No claim of automatic arbitrary-PDF syllabus extraction.

## Original retrieval failure and bounded retry

Initial raw lexical ranking: expected family at top-1 **44/50**, in top-3/top-5 **49/50**. The English goal about equal “remainders” did not match “remainder” and related vocabulary strongly enough; the required mod_compare family had zero score and was excluded. The model named it anyway, outside that request's allowed candidates. The context guard rejected this choice, so only **98/100 variants were initially eligible**. No mathematical task was approved from the invalid selection.

A general plural/synonym normalization pass was added as a separate retrieval version. Only the failed profile was sent in a short generation-plan retry with corrected retrieved candidates. The model again selected mod_compare, now in context. Original plan, original ranking/rejection, new ranking and retry are all preserved. Test labels did not choose the retry result. This is a retrieval repair, not a hidden LLM mathematical reviewer or a rewritten original score.

Final: **100/100 constructed variants pass supported-family program checks**, **294/294 formula blocks render** with zero math fallbacks. Two paid generation-plan calls total **$0.0273008** (main $0.0267056, retry $0.0005952), shared cap $0.05. No second LLM review, paid mathematical correction or further generation call.

## Mathematical checks and limits

Existing exact integer/Fraction checks, induction algebra certificates and inverse-matrix products remain in use. New families add complete Boolean tables and finite quantifier evaluation; exhaustive relation diagonal/reverse-pair/composable-triple checks; equivalence-class partition checks; finite poset axiom/extremum/bound checks; polynomial parity coefficient identities; affine monotonicity with a constant boundary case; and rational denominator-root restrictions. Tests distinguish minimal/maximal from least/greatest, an empty-set least element from no least element, and constant weak monotonicity from strict monotonicity.

These are program template checks, not a universal proof checker or Lean/Coq formalization. Template bugs remain possible. The book's other chapters, all possible new topics, arbitrary interval/domain changes and free-form analogies are not covered. Difficulty and novelty are not scored. Reusing a method with different numbers is intentional. This is a small curated retrieval-and-compilation experiment, not a blind large-scale benchmark.

## Reproduction and evidence

`engine.py` defines the 50 supported families and exact computations. `retrieval.py` defines topic goals, provenance, hard filters and both retrieval versions. `run.py` freezes evidence before one main paid call; `repair.py` has one separately reserved retry slot for the single out-of-context selection. Neither slot permits automatic repeats. `publish.py` recompiles from stored choices offline and publishes bank.json/result.json/hundred-data.js. Private output/ retains source excerpts and raw API artifacts and is ignored. No source PDF or credential is published.

Use the existing research environment with pypdf, OpenAI, Pydantic and dotenv. Core mathematical builders and most tests use Python's standard library. Optional independent spot checks use the isolated SymPy dependency from the earlier metrics experiment; no production environment is modified.

Browser checks cover all 100 tasks, 10 expandable topic groups, all 294 math blocks, zero JS errors, 320/390px widths, and preservation of earlier tests plus 505 historical flashcards. Representative logic, inclusion-order and new monotonicity screenshots were inspected. Zero rendering errors do not establish mathematical correctness.
