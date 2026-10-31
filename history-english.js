/* Display translations only. Original evidence and browser edits are never rewritten. */
const issueEnglish = [
 ['Sets, level 4','Answers 1–3','Formula rendering','The PDF displays 85, 87 and 7B/7D instead of membership symbols and braces.','Manual review','Visible rendering defect, not just text extraction.','The paragraph decoding restriction was removed; a fresh generation is needed.'],
 ['Induction, cards','Answers 1–2','Formula rendering','P(n+1) expressions are broken and inequality signs in the text are corrupted.','Manual review','Visible rendering defect.','Use structured math blocks and preserve Unicode and operators.'],
 ['Induction, tasks','Answer 3','Completeness','The induction step ends by asking for simplification rather than completing the derivation.','Manual review','Confirmed by reading the answer.','Require the complete chain of equalities.'],
 ['Induction, tasks','Answer 5','Correctness','After the base case fails, the solution changes the problem itself.','Manual review','The statement cannot be changed during its proof.','Solve and check each candidate before finalizing the statement.'],
 ['Proofs, tasks','Task 10, PDF pages 2 and 7','False statement','From a|b and even b, even a does not follow: a=3, b=6 is a counterexample.','Manual review','Mathematically refuted.','Check simple counterexamples before generating a proof.'],
 ['Proofs, tasks','Answer 13','Algebra','10k+5=2(5k)+1 is false. The correct odd form is 2(5k+2)+1.','Manual review','Mathematically refuted.','Verify every algebraic step and integer witness.'],
 ['Proofs, tasks','Tasks 1–4','Novelty','These repeat examples 4.1–4.4 in the notes rather than providing new analogues.','Manual review','Compared with page 20 of the notes.','Retain the requirement to transfer the method to a new task.'],
 ['Numbers, tasks','Answer 2','Completeness','The requested proof that the square root of three is irrational is replaced with a claim that it can be shown.','Manual review','The requested proof is missing.','Do not accept “can be shown” in place of the proof.'],
 ['Sets, levels 4–5','Opening questions','Difficulty','Definitions and notation dominate the opening questions despite the high level in the title.','Manual review','Descriptive audit; the title does not establish that difficulty quotas were met.','Check actual reasoning demands rather than the skill label.'],
 ['Induction, tasks','6','False premise','The claim that every n≥12 has a representation n=4a+7b fails for 13 and 17. The equality 13=4+7 is also false.','Critical','For 13, b is 0 or 1; neither 13 nor 6 is divisible by 4. The correct general threshold is 18.','The revised statement is still false; the issue is unresolved.'],
 ['Proofs, tasks','15','Invalid counterexample','The solution takes a=2, b=3, c=6 and claims 3∤6 although 3|6. It does not refute the disjunction.','Critical','A valid example is a=3, b=4, c=6: 3|6, 3∤4, 4∤6.','The false theorem in v3 was replaced by another error.'],
 ['Induction, tasks','5','Invalid step','The solution includes S(n+1)<1+0<1, then switches to another argument.','Significant','1+0<1 is false. Present the stronger induction argument without the invalid draft.','Self-correction remains inside the final answer.'],
 ['Induction, tasks','2–3','Incomplete justification','The cube-sum step leaves simplification to the reader; the divisibility proof ends by asking for more parity analysis.','Significant','The second increment 4n³+6n²+2n=2n(n+1)(2n+1) is divisible by 4.','Complete solution steps are still needed.'],
 ['Proofs, tasks','1–6','Insufficient novelty','Examples from pages 20–21 are repeated; the first four statements are unchanged.','Significant','Compared with examples 4.1–4.6 in the original notes.','The requirement for new analogous tasks was not met.'],
 ['Proofs, tasks','7, PDF page 4','Raw LaTeX','The irrationality proof displays text, sqrt, frac and line-break commands instead of formulas.','Formatting','Confirmed on the rendered PDF, not just extracted text.','Most symbols improved, but some blocks remain broken.'],
 ['Both task sets','Titles','Raw math delimiters','Titles display literal LaTeX delimiters around n and formulas.','Formatting','PDF inspection: titles should use ordinary words.','Residual rendering defect.'],
 ['Sets, cards','3 and 19','Semantic duplicate','Both cards test the difference between the empty set and a set containing the empty set.','Significant','The learning fact is the same; asking to explain a mistake does not make it independent.','Duplicates remain: 10% according to the evaluator.'],
 ['Sets, cards','19, PDF page 8','Local formula defect','An extra backslash appears before a closing brace in an empty-set comparison.','Formatting','Confirmed on the rendered PDF.','Generally more readable than v3, with residual defects.'],
 ['Both card sets','Level 4','Insufficient difficulty','Sets: 16 of 20 cards are classified as definitions. Recall dominates over application and justification.','Significant','Automatic card type is not a skill label; exact skill quotas could not be checked without the JSON.','The level-4 claim is not established by the title alone.']
];
function englishIssue(issue){
 const idx=window.MATHPDF_DATA.issues.findIndex(i=>i.id===issue.id);
 if(idx<0)return issue;
 const out={...issue},keys=['topic','location','category','description','severity','evidence','next'];
 keys.forEach((k,j)=>{if(issue[k]===window.MATHPDF_DATA.issues[idx][k])out[k]=issueEnglish[idx][j]});return out;
}
