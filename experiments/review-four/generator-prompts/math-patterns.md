# Small serialization examples

These are illustrative containers, not source quotations or a task catalogue. Use actual selected ORIGINAL pages and the source's own notation. Never cite these illustrative page numbers without verifying the actual source.

## A complete generated input stays in the question

{"parts":["Let ",{"math":"f:\\mathbb{Z}^2\\to\\mathbb{Z}^2"}," be defined by the following rule."]}
{"latex":"f(m,n)=(m+n,m+2n)","page":3,"variant":null}
{"parts":["Determine whether the function is bijective and justify your answer."]}

These are consecutive entries of one question array. A separate formula: {"page":3} can cite a prose method on the answer side; it does not replace the question's input.

## A worked step uses a separate equation

{"parts":["Subtracting the first coordinate equation from the second gives the second input."]}
{"latex":"n=d-c", "page":3,"variant":null}
{"parts":["The recovered inputs are integers because both target coordinates are integers."]}

## Sets and a short system

{"latex":"A=\\{x,y\\}","page":5,"variant":null}
{"latex":"\\begin{aligned}m+n&=c\\\\m+2n&=d\\end{aligned}","page":3,"variant":null}

JSON keys stay outside strings. Never turn any example into {"parts":["latex"]}, a fenced code block, or a prose string containing the JSON object. Inline notation uses {"math":"..."} only inside parts; display notation uses latex/page/variant at the array level.
