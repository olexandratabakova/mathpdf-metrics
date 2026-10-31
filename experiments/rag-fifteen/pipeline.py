"""Real local BM25 retrieval, hard prerequisites/domains, then bounded generation.

The test profiles/expected families are hand-authored; this is not an automatic
PDF theory extractor or an independent unseen-source generalization benchmark.
"""
from collections import Counter
import hashlib,importlib.util,json,math,random,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('rag_math_engine',ROOT.parent/'v5-seventy/engine.py')
E=importlib.util.module_from_spec(spec);spec.loader.exec_module(E)
SEED=51515
CONCEPTS={
 'sets':['membership','finite_sets','set_operations','ordered_pairs','subsets'],
 'induction':['positive_integer_induction','integer_arithmetic','factorial','inequality'],
 'integers':['integer_arithmetic','division','divisibility','factorization','positional_notation'],
 'congruences':['integer_arithmetic','congruence','parity','finite_enumeration'],
 'counting':['finite_choices','binomial_choices','nonnegative_integers'],
 'pigeonhole':['pigeonhole','integer_arithmetic','square_diagonal','congruence','coprimality'],
 'functions':['function_definition','injectivity','surjectivity','real_arithmetic','integer_arithmetic','integer_pairs']}
DESCRIPTIONS={
 'sets_ops':'union intersection difference membership two finite sets',
 'sets_complement':'relative complement universal set excluded elements',
 'sets_product':'Cartesian product ordered pairs count finite sets',
 'sets_power':'all subsets power set enumeration',
 'sets_distribute':'distributive identity union intersection three sets',
 'ind_squares':'scaled sum of squares quadratic summands induction base transition',
 'ind_odd':'scaled odd integer sum induction identity',
 'ind_factorial':'weighted factorial sum induction base transition identity',
 'ind_divisible':'cubic divisibility induction consecutive integers parity',
 'ind_harmonic':'reciprocal squares sum upper bound inequality induction',
 'int_division':'division algorithm quotient nonnegative remainder negative dividend',
 'int_gcd':'Euclidean greatest common divisor gcd algorithm',
 'int_bezout':'gcd integer Bezout coefficients linear combination',
 'int_factor':'prime factorization positive integers',
 'int_base':'binary octal positional base conversion digits',
 'mod_compare':'test congruence same remainder',
 'mod_power':'power exponent remainder modular multiplication',
 'mod_linear':'all integer solutions linear congruence representative residue classes',
 'mod_impossible':'parity residue classes quadratic equation no integer roots',
 'mod_clock':'clock hour elapsed modular addition',
 'count_routes':'routes multiply choices add disjoint paths',
 'count_permutations':'permutations ordered arrangements distinct objects',
 'count_combinations':'unordered committee choose distinct people no repetition binomial choices',
 'count_stars':'nonnegative integer triples fixed sum combinations stars bars separators',
 'count_binomial':'polynomial coefficient binomial expansion',
 'ph_birthdays':'students birthdays months occupancy guaranteed maximum',
 'ph_boxes':'smallest objects boxes target occupancy sharp threshold minimum guarantee',
 'ph_remainders':'two integers equal remainders divisible difference',
 'ph_square':'points square grid cells distance diagonal bound',
 'ph_repunit':'decimal all ones repunit divisible modulus coprime ten'}
def tokens(text):
    # Deliberately simple lexical search, no embeddings or hidden external API.
    return re.findall(r'[a-z0-9]+',text.lower())
def hashjson(obj):return hashlib.sha256(json.dumps(obj,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
def bank():
    examples=E.generate();first={}
    for x in examples:first.setdefault(x['template_id'],x)
    docs=[]
    for t,x in first.items():
        topic=x['topic'];domain='real' if topic=='functions' else {'sets':'finite_sets','induction':'positive_integers','integers':'integers','congruences':'integers','counting':'finite_choices','pigeonhole':'finite_occupancy'}[topic]
        required=list(CONCEPTS[topic])
        if topic=='functions':
            if t=='integer_pair_bijection':domain='integer_pairs';required=['function_definition','injectivity','surjectivity','integer_arithmetic','integer_pairs']
            elif t in ['relation_missing','relation_total','finite_range']:domain='integers';required=['function_definition','integer_arithmetic']
            else:required=['function_definition','injectivity','surjectivity','real_arithmetic']
        if t=='ph_square':domain='geometry_square';required=['pigeonhole','square_diagonal']
        if t.startswith('ph_') and t!='ph_square':required=['pigeonhole','integer_arithmetic']+(['congruence','coprimality'] if t=='ph_repunit' else [])
        text=DESCRIPTIONS.get(t,E.FUNCTIONS.CATALOG.get(t,{}).get('method',''))+' '+x['title']
        docs.append({'id':t,'topic':topic,'domain':domain,'requires':required,'text':text,'source':x['source'],'example':x,'revision':'curated-bank-v1'})
    assert len(docs)==40
    return docs
def retrieve(request,docs,k=3):
    query=tokens(request['goal']);counts=[Counter(tokens(d['text'])) for d in docs];avg=sum(sum(c.values()) for c in counts)/len(counts)
    available=set(request.get('available',CONCEPTS.get(request['topic'],[])))
    ranked=[];rejected=[]
    for d,c in zip(docs,counts):
        reasons=[]
        if d['topic']!=request['topic']:reasons.append('topic')
        if d['domain']!=request['domain']:reasons.append('domain')
        if not set(d['requires'])<=available:reasons.append('missing_prerequisites')
        if reasons:rejected.append({'id':d['id'],'reasons':reasons});continue
        score=0;length=sum(c.values())
        for word in set(query):
            df=sum(word in cc for cc in counts);idf=math.log(1+(len(docs)-df+.5)/(df+.5));tf=c[word]
            score+=idf*tf*2.2/(tf+1.2*(.25+.75*length/avg)) if tf else 0
        if score>0:ranked.append({'id':d['id'],'score':round(score,6),'doc':d})
    ranked.sort(key=lambda x:(-x['score'],x['id']))
    return {'matches':ranked[:k],'eligible':len(ranked),'rejected':rejected,'status':'retrieved' if ranked else 'no_coverage'}
def theory_chunks(requests):
    from pypdf import PdfReader
    pdf=PdfReader('C:/Users/kotya/Downloads/main (12).pdf');result={}
    for r in requests:
        text=pdf.pages[r['page']-1].extract_text();a=text.find(r['start'])
        if a<0:raise ValueError('Missing theory start marker '+str(r['id']))
        b=text.find(r['end'],a+len(r['start']))
        if b<0:raise ValueError('Missing theory end marker '+str(r['id']))
        chunk=text[a:b].strip()
        if re.search(r'\b(?:Example|Exercise)\s*\d',chunk):raise ValueError('Example leaked into theory-only context')
        result[str(r['id'])]={'page':r['page'],'text':chunk,'sha256':hashlib.sha256(chunk.encode()).hexdigest()}
    return result
def prepare():
    requests=json.loads((ROOT/'requests.json').read_text(encoding='utf-8'));docs=bank();chunks=theory_chunks(requests)
    return [{'request':r,'theory':chunks[str(r['id'])],'retrieval':retrieve(r,docs)} for r in requests]
def build_item(t,number,constraints=None):
    constraints=constraints or {}
    if set(constraints)-{'negative_dividend'}:raise ValueError('Unknown parameter constraint')
    if constraints and t!='int_division':raise ValueError('Constraint incompatible with family')
    if t in E.FUNCTIONS.CATALOG:
        old=E.FUNCTIONS.SEED;E.FUNCTIONS.SEED=SEED+number
        p=E.FUNCTIONS.params()[t];E.FUNCTIONS.SEED=old
        x=E.FUNCTIONS.build(t,p);x['topic']='functions';x['source']={'page':x['source']['page'],'reference':x['source']['reference']}
    else:
        p=E.parameters(t,random.Random(SEED+number),number%2)
        if constraints.get('negative_dividend'):p['a']=-abs(p['a'])
        x=E.build(t,p)
    x['id']=number;E.verify_artifact(x)
    return x
def controls():
    docs=bank();cases=[
      {'id':'unknown_topic','topic':'calculus','goal':'differentiate sine function','domain':'real','available':['derivatives']},
      {'id':'missing_prerequisites','topic':'functions','goal':'integer pair bijection','domain':'integer_pairs','available':['integer_arithmetic']},
      {'id':'wrong_domain','topic':'functions','goal':'reciprocal bijection','domain':'complex','available':CONCEPTS['functions']}]
    return [{'case':c,'status':retrieve(c,docs)['status']} for c in cases]
