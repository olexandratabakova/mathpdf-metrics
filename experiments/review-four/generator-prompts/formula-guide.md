# Output contract: words stay words, mathematics stays mathematics

Use the response schema supplied by the application. Return the result envelope only. A completed result contains exactly the requested number of items; otherwise use insufficient_source with an actionable reason. Do not add schema keys, Markdown fences, HTML, code-language labels or placeholders.

## Three containers

1. Plain titles contain English words, not TeX. Flashcard questions contain exactly one self-contained plain-English string. Name the objects in words without revealing the answer; do not refer to hidden expressions.
2. A sentence on a problem or answer side uses a paragraph: {"parts":["For every ",{"math":"x\\in X"},", the image belongs to the codomain."]}. Mathematical fragments belong entirely inside math objects, including variable names and operators. Prose parts contain ordinary sentences with explicit spaces around inline fragments. Never split a TeX command across parts.
3. An equation, function definition, set, system or worked algebraic step uses a standalone object: {"latex":"f(x)=\\frac{2x+1}{x-1}","page":3,"variant":null}. Each such object needs the ORIGINAL selected primary page supporting the expression or solution method.

The words latex and math are JSON keys, not visible content. Never output "latex" as a question entry, an answer fragment or a substitute for an expression. Never put an object, serialized object, TeX command or Markdown math fence inside a prose string. Do not put delimiters such as dollar signs, backtick fences, or backslash-parenthesis wrappers around a latex or math value: the application supplies them.

## What each field means

Every item has title, formula, skill, question and answer. Choose a skill supported by the difficulty instructions before writing the question.

- formula is the source reference shown on the answer side. Use {"page":3} when the method or relevant definition is in prose. Otherwise copy a relevant expression actually printed on that selected page as a latex/page/variant object. Never invent a source quotation or a symbolic reference merely to fill this field.
- A problem's question must contain ALL its generated givens, domains, codomains, restrictions and requested task. A formula supplied only in formula or answer does not define the question. Put necessary inputs explicitly in question using paragraphs and standalone formula objects. Problem answer is a nonempty array of paragraphs and formulas containing the complete worked solution.
- A flashcard question is one complete English string. Put source-only material in from_notes and short AI-added context in explanation. Use answer: [] for new flashcards. The source formula is inserted automatically on the back; do not repeat it in these arrays.
- Independently generated problem inputs and derived steps cite the supporting method page and use variant: null. A deliberate direct edit of a printed expression requires variant.original copied exactly and variant.change describing the edit. Do not invent an original expression for a new construction.

## Reliable TeX

Encode valid JSON exactly once. After JSON decoding, TeX commands have one backslash; mathematical row separators have two. Thus JSON contains "\\frac{a}{b}", "\\{1,2\\}", or "\\begin{aligned}a&=b+c\\\\d&=e-f\\end{aligned}". Do not write a single JSON backslash before frac, text or begin, and do not escape already escaped JSON a second time.

Each math value is a complete independent expression. Balance braces, group every multi-character subscript/exponent, and keep each environment and matching delimiter pair in the same value. Prefer several short formula blocks for generated worked steps. Use aligned only for short related rows; each row break must be explicit. Do not put a whole proof or paragraph in a math value. Use text commands only for short labels or conditions. Do not use packages, custom macros, document commands, HTML, URLs or layout hacks.

Preserve the source's visible symbols, overbar scope, fonts, accents, fraction style and subset convention when quoting it. A source text layer may omit symbols; inspect the page image. Do not copy character codes or reconstruct an unreadable source expression by guessing. Choose a different readable reference or a page-only reference where the source actually states the method in prose. Do not replace source operators by different equivalent operators. Source exercises and proposed answers may be false: their presence does not establish truth.

Before returning, inspect the final serialized objects: no placeholder words; no bare mathematics in prose; no raw delimiters; complete question-side givens; readable independently valid TeX; actual selected source pages. This checks format, not mathematical correctness.
