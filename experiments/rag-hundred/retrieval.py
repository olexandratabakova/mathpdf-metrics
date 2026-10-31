"""Topic-selected source packets and a curated 50-family retrieval bank.

Does NOT read or embed either complete PDF. Source excerpts stay private.
"""
import hashlib,importlib.util,json
from pathlib import Path
import engine as E
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('prior_rag',ROOT.parent/'rag-fifteen/pipeline.py')
P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)
PATHS={'notes':Path('C:/Users/kotya/Downloads/main (13).pdf'),'book':Path('C:/Users/kotya/Downloads/Main (10).pdf')}
INITIAL_READ={'notes':[1,2,3,4,45,51,52,54,71,72,73,74],
 'book':[1,2,3,4,5,6,13,14,20,27,30,32,51,52,53,60,62,65,71,73,79,90,97,102,104,108,109,116,143,194,195,217,218,222,227,233,240,241,242]}
GOALS={
 'sets_ops':'Find union, overlap and elements present in one finite set but not another.',
 'sets_complement':'Find what remains outside a subset relative to an explicitly bounded universe.',
 'sets_product':'Enumerate ordered pairs in a Cartesian product of finite integer collections.',
 'sets_power':'List every subset of a small finite set and count its power set.',
 'ind_squares':'Induction identity for a weighted sum of integer squares.',
 'ind_odd':'Induction proof summing a scaled progression of odd numbers.',
 'ind_factorial':'Induction proof for a weighted factorial sum with a complete base and transition.',
 'ind_divisible':'Prove cubic divisibility for every positive integer by induction and parity.',
 'ind_harmonic':'Establish a reciprocal-square sum upper bound using induction.',
 'int_division':'Compute the division quotient and nonnegative remainder, including negative dividends.',
 'int_gcd':'Run the Euclidean algorithm to determine greatest common divisor.',
 'int_bezout':'Find exact Bezout coefficients expressing the gcd as a linear combination.',
 'int_factor':'Recover the prime factorization of a specific composite number.',
 'mod_compare':'Decide whether two integers have equal remainders under a modulus.',
 'mod_power':'Compute the remainder of a large power without expanding its digits.',
 'mod_linear':'Enumerate all representative solutions to a linear congruence.',
 'mod_impossible':'Disprove an integer root of a quadratic using parity classes.',
 'mod_clock':'Determine a later clock hour after elapsed whole hours.',
 'count_routes':'Count disjoint two-stage routes by the sum and product rules.',
 'count_permutations':'Arrange distinct objects in a nonrepetitive ordered row.',
 'count_combinations':'Choose an unordered committee of distinct people.',
 'count_stars':'Count nonnegative integer triples with a specified total using separators.',
 'count_binomial':'Find a polynomial coefficient through the binomial theorem.',
 'ph_birthdays':'Determine the sharp guaranteed count of student birthdays in one month.',
 'ph_boxes':'Find the minimal number of objects forcing a target occupancy in boxes.',
 'ph_remainders':'Prove two selected integers share a residue and have divisible difference.',
 'ph_square':'Bound the distance of two points by a square grid diagonal.',
 'ph_repunit':'Construct a divisible all-ones decimal with a modulus coprime to ten.',
 'relation_missing':'Test whether an integer linear relation fails to supply an output for some input.',
 'relation_total':'Determine whether an integer linear relation gives a unique integer output everywhere.',
 'finite_range':'Compute the finite image of a square-based function on a small domain.',
 'equal_rational':'Compare equality of a factored rational rule and an affine rule with a removed domain point.',
 'square_real':'Classify a square map on all reals using collision and missing-target witnesses.',
 'square_nonnegative':'Prove a scaled square is a bijection on nonnegative inputs and outputs.',
 'reciprocal_not_onto':'Prove a shifted reciprocal is injective but misses a real codomain target.',
 'reciprocal_bijection':'Construct preimages for a shifted reciprocal when its missing output is excluded.',
 'integer_pair_bijection':'Prove an integer-pair map is bijective with an integer-valued inverse.',
 'logic_table':'Build the full truth table for a compound implication over Boolean variables.',
 'logic_equivalence':'Compare two logical statements for equivalence over every truth assignment.',
 'logic_quantifiers':'Evaluate universal and existential predicates on an explicit finite integer universe.',
 'logic_negation':'Find the negation of a universal quantified bound and determine its truth.',
 'rel_properties':'Classify reflexive symmetric antisymmetric and transitive properties of a listed finite relation.',
 'rel_classes':'Partition a finite integer universe into congruence equivalence classes.',
 'rel_between':'List pairs of a relation from one finite set to another using an inequality predicate.',
 'order_extrema':'Find least greatest minimal and maximal elements under divisibility ordering.',
 'order_bounds':'Find lower and upper bounds, infimum and supremum in a finite divisibility poset.',
 'order_subsets':'Find extremal elements of a family ordered by set inclusion.',
 'world_parity':'Decide polynomial evenness and oddness using symmetry of the real domain.',
 'world_monotonic':'Separate non-strict and strict monotonicity of an affine function, including a constant case.',
 'world_domain':'Find the largest real domain of a rational polynomial quotient.'}
BOOK_SUPPORT={
 'sets_ops':30,'sets_complement':32,'sets_product':20,'sets_power':27,
 'ind_odd':194,'ind_divisible':195,'mod_compare':143,
 'count_routes':79,'count_permutations':90,'count_combinations':97,'count_stars':109,'count_binomial':104,
 'ph_birthdays':116,'ph_boxes':116,
 'relation_missing':240,'relation_total':240,'finite_range':240,'square_real':241,
 'square_nonnegative':241,'reciprocal_not_onto':242,'reciprocal_bijection':242,'integer_pair_bijection':242}
NEW_TEXT={
 'logic_table':'Boolean connectives conjunction disjunction implication full truth table assignments',
 'logic_equivalence':'logical equivalence compare formulas same truth assignments',
 'logic_quantifiers':'universal existential quantifiers finite universe predicate square bound witnesses',
 'logic_negation':'negation universal quantified statement existential reversed inequality',
 'rel_properties':'reflexive symmetric antisymmetric transitive listed finite relation properties',
 'rel_classes':'congruence equivalence classes partition integer universe modulo',
 'rel_between':'relation between sets ordered pairs inequality predicate Cartesian product',
 'order_extrema':'least greatest minimal maximal divisibility partial order extrema',
 'order_bounds':'lower upper bounds infimum supremum divisibility finite poset',
 'order_subsets':'least greatest minimal maximal set inclusion family subsets',
 'world_parity':'polynomial even odd parity symmetric domain negative input coefficient identity',
 'world_monotonic':'affine monotonicity increasing decreasing strict non-strict constant function',
 'world_domain':'rational polynomial quotient largest real domain denominator roots'}
CONCEPTS={**P.CONCEPTS,
 'functions':P.CONCEPTS['functions']+['polynomials','parity_functions','monotonicity'],
 'logic':['Boolean_logic','finite_universe','quantifiers'],
 'relations':['finite_sets','ordered_pairs','relation_properties','congruence'],
 'orders':['finite_sets','partial_order','divisibility','inclusion']}
def make_bank():
    old={d['id']:d for d in P.bank()};docs=[]
    for t in E.templates():
        item=E.build(t,E.params(t,0))
        if t in old:
            d={k:old[t][k] for k in ['id','topic','domain','requires','text']}
        else:
            topic=E.NEW[t][0];d={'id':t,'topic':topic,'domain':{'logic':'finite_logic','relations':'finite_relations','orders':'finite_orders','functions':'real'}[topic],
              'requires':(['function_definition','real_arithmetic','polynomials'] if topic=='functions' else CONCEPTS[topic]),'text':NEW_TEXT[t]+' '+item['title']}
        source=item['source'];doc=source.get('document','notes');sources=[{'document':doc,'pdf_page':source['page'],'role':'template_method_support'}]
        if t in BOOK_SUPPORT:sources.append({'document':'book','pdf_page':BOOK_SUPPORT[t],'role':'supporting_definition_or_method_not_a_literal_copy'})
        if t=='rel_properties':sources.append({'document':'notes','pdf_page':45,'role':'antisymmetry_definition'})
        d.update(example=item,sources=sources,revision='two-pdf-bank-v1');docs.append(d)
    return docs
def profiles(docs):
    return [{'id':i,'goal':GOALS[d['id']],'topic':d['topic'],'domain':d['domain'],'available':CONCEPTS[d['topic']],
      'expected':[d['id']],'sources':d['sources'],'variants':2} for i,d in enumerate(docs,1)]
def retrieve(profile,docs):return P.retrieve(profile,docs,k=5)
def retrieve_normalized(profile,docs):
    """General lexical repair, not a lookup using expected evaluation labels."""
    original=P.tokens
    aliases={'equal':'same','equals':'same','modulo':'modular','modulus':'modular','congruent':'congruence'}
    def normalized(text):
        words=original(text);out=[]
        for w in words:
            if len(w)>3 and w.endswith('s') and not w.endswith(('ss','is')):w=w[:-1]
            out.append(aliases.get(w,w))
        return out
    try:
        P.tokens=normalized
        return P.retrieve(profile,docs,k=5)
    finally:P.tokens=original
def source_packets(docs):
    from pypdf import PdfReader
    targets={k:set() for k in PATHS}
    for d in docs:
        for src in d['sources']:targets[src['document']].add(src['pdf_page'])
    manifests=[];packets={}
    for doc,path in PATHS.items():
        pdf=PdfReader(path);pages=sorted(targets[doc])
        for n in pages:
            text=pdf.pages[n-1].extract_text() or ''
            packets[f'{doc}:{n}']={'document':doc,'pdf_page':n,'selected_excerpt':text[:1600],'page_text_sha256':hashlib.sha256(text.encode()).hexdigest()}
        reviewed=sorted(set(pages)|set(INITIAL_READ[doc]))
        manifests.append({'id':doc,'name':path.name,'pages_total':len(pdf.pages),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
          'targeted_pages':pages,'initial_inspection_pages':INITIAL_READ[doc],'unique_pages_accessed':reviewed,
          'full_document_text_extracted':False,'strategy':'TOC/outlines first; extract only selected topic pages. No full-PDF index or full-PDF model upload.'})
    return manifests,packets
def prepare():
    docs=make_bank();requests=profiles(docs);manifest,packets=source_packets(docs)
    return {'bank':docs,'requests':requests,'retrieval':[{'request':r,'retrieved':retrieve(r,docs)} for r in requests],'sources':manifest,'source_packets':packets}
def compile_variants(t,request_id):
    results=[];seen=set();draws=[]
    for v in [0,1]:
        for attempt in range(100):
            seed=E.SEED+attempt*1000;p=E.params(t,v,seed);item=E.build(t,p)
            key=json.dumps(item['question'],sort_keys=True)
            if key not in seen:break
        else:raise ValueError('Cannot make distinct variants')
        seen.add(key);E.verify(item);results.append(item);draws.append({'seed':seed,'variant':v})
    return results,draws
def controls(docs):
    probes=[{'topic':'calculus','domain':'real','goal':'differentiate a trigonometric function','available':['derivatives']},
      {'topic':'functions','domain':'complex','goal':'a bijective complex analytic function','available':CONCEPTS['functions']},
      {'topic':'orders','domain':'finite_orders','goal':'bounds in a partial order','available':['finite_sets']}]
    return [{'request':p,'status':retrieve(p,docs)['status']} for p in probes]
