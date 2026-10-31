"""Small overview metadata derived from immutable evidence; no API calls.

Keep unlike measurement types separate. Every chart has its own scope caption.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(folder):return json.loads((ROOT/'experiments'/folder/'result.json').read_text(encoding='utf-8'))
def series(label,value,total,tone='sage',unit='ratio'):
    return {'label':label,'value':value,'total':total,'tone':tone,'unit':unit}
def build():
    out=[]
    def add(folder,title,method,description,finding,chart_title,chart_note,bars,data,_legacy_renderer,run_id=None):
        raw=read(folder)
        out.append({'id':folder,'number':len(out)+1,'title':title,'method':method,'description':description,'finding':finding,
          'date':raw['date'],'cost_usd':raw['cost_usd'],'chart_title':chart_title,'chart_note':chart_note,'series':bars,
          'data_script':data,
          'run_id':run_id,'evidence':'experiments/'+folder+'/result.json','readme':'experiments/'+folder+'/README.md'})
    a=read('review-four');n=len(a['problems'])
    add('review-four','Does GPT-4.1 catch the errors?','llm','Mini generates four tasks; GPT-4.1 reviews the statements and solutions.','All four were approved, including an incorrect algebraic simplification.',
      'Approval and local refutation','These bars overlap: an approved task can still be wrong. They are not a correct/incorrect partition.',
      [series('Model approved',sum(x['decision']=='accept' for x in a['audit']['items']),n,'muted'),series('Locally refuted',1,n,'clay')],
      'reviews-data.js','reviews.js',a['id'])
    a=read('review-mini-four');n=len(a['problems'])
    add('review-mini-four','The same mini model as reviewer','llm','Separate mini calls generate, solve blindly and audit four new tasks.','It caught a false bijection claim but missed a conflicting domain.',
      'Reviewer decisions on four tasks','These are model decisions, not an independent measure of mathematical correctness.',
      [series('Accept',sum(x['decision']=='accept' for x in a['audit']['items']),n,'muted'),series('Revise',sum(x['decision']=='revise' for x in a['audit']['items']),n,'clay')],
      'reviews-data.js','reviews.js',a['id'])
    a=read('compare-ten')
    add('compare-ten','Two reviewers, the same ten tasks','llm','Five valid and five flawed solutions, with known reference labels.','GPT-4.1 made better decisions, but its explanation still contained an error.',
      'Decisions matching reference labels','Both models saw the same cases. Ten matching decisions do not mean ten error-free explanations.',
      [series('GPT-4.1 mini',a['scores']['mini']['correct_decisions'],10),series('GPT-4.1',a['scores']['full']['correct_decisions'],10,'ink')],
      'comparison-data.js','comparison.js')
    a=read('cycle-fifteen');m=a['metrics']
    add('cycle-fifteen','Generate → review → repair','llm','One complete repair cycle on fifteen tasks, followed by a fresh review.','Model approval increased; the local count of mathematically correct tasks did not.',
      'Before and after one repair','Model approval and local mathematical assessment are different measures. Compare each measure only with itself.',
      [series('Model · before',m['before_accepts'],15,'muted'),series('Model · after',m['after_accepts'],15,'muted'),series('Local · before',m['local_before_correct'],15),series('Local · after',m['local_after_correct'],15)],
      'cycle-data.js','cycle.js')
    a=read('v5-parameterized')
    add('v5-parameterized','V5: controlled numbers and mathematics','templates','The model chooses a family; code supplies numbers, formulas and answers.','Ten supported families passed their dedicated checks.',
      'Checks within supported families','10/10 applies to curated families. It is not the accuracy of unrestricted LLM generation.',
      [series('Program checks',a['verified'],len(a['items']))],
      'parameterized-data.js','parameterized.js')
    a=read('v5-seventy')
    add('v5-seventy','V5: seventy variants, seven topics','templates','Controlled templates extended to induction, sets and other topics.','Seventy variants across forty families passed their checks.',
      'Task distribution by topic','Each bar is a share of the seventy-task set. This measures topic distribution, not correctness.',
      [series(name,10,70,unit='count') for name in ['Sets', 'Induction', 'Numbers', 'Congruences', 'Combinatorics', 'Pigeonhole', 'Functions']],
      'seventy-data.js','seventy.js')
    a=read('sympy-55');m=a['counts']
    add('sympy-55','SymPy meets actual LLM generation','symbolic','Forty close analogues and fifteen requested condition changes, with formal records.','Checking an encoded calculation does not guarantee that it matches the written task.',
      'What the SymPy adapter could check','Formal-record coverage, not task accuracy. Partial and unsupported results are not approval.',
      [series('Formally confirmed',m['confirmed'],55),series('Partial',m['partial'],55,'sand'),series('Encoding refuted',m['refuted'],55,'clay'),series('Unsupported',m['unsupported'],55,'muted')],
      'symbolic-data.js','symbolic.js')
    a=read('rag-fifteen');m=a['metrics']
    add('rag-fifteen','RAG: tasks from theory without examples','rag','Retrieve a family, let the model choose, then compile fifteen numeric analogues.','The required family was not always the first search result.',
      'Retrieval and selection on fifteen goals','Goals were manually labelled. The bank and theory share their origin; this is a small controlled test.',
      [series('Expected top-1',m['top1_hits'],15,'muted'),series('Present in top-3',m['top3_hits'],15),series('Goal-matching choice',m['model_goal_matches'],15,'ink')],
      'rag-data.js','rag.js')
    a=read('rag-hundred');m=a['metrics']
    add('rag-hundred','RAG: one hundred analogues from two PDFs','rag','Selected topics from course notes and Book of Proof; fifty supported families.','Ninety-eight variants were admitted initially; two more after a retrieval fix.',
      'Context admission and family checks','The first two bars measure context admission, not mathematics. One hundred variants are not one hundred distinct families.',
      [series('Context · initial',m['first_pass_task_accepts'],100,'muted'),series('Context · after retry',m['final_generated'],100,'ink'),series('Family checks',m['program_verified'],100)],
      'hundred-data.js','hundred.js')
    if (ROOT/'experiments/wildflower/result.json').exists():
        a=read('wildflower');c=a['metrics']['cards'];p=a['metrics']['problem_decisions']
        add('wildflower','Wildflower · ordinary generation','baseline',
          'Sixty flashcards and forty problems from unchanged MathPDF prompts, evaluated with the original card metrics and a task audit.',
          'Card self-containedness is 80%. The judge accepts 36/40 problems, but separate checks expose missed errors and false rejections.',
          'Card quality signals and task reviewer decisions',
          'Card scores are weighted judge metrics on 60 cards. Task acceptance is a separate model judgement on 40 problems, not mathematical proof. This is not a paired historical comparison.',
          [series('Cards · self-contained',round(c['pct_self_contained']*60,6),60),
           series('Cards · atomic',round(c['pct_atomic']*60,6),60),
           series('Problems · reviewer accepted',p.get('accept',0),40,'muted')],
          'wildflower-data.js','research.js')
    return {'schema_version':1,'experiments':out}
def main():
    catalog=build()
    (ROOT/'data/experiments.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (ROOT/'experiments-catalog.js').write_text('window.MATHPDF_EXPERIMENTS = '+json.dumps(catalog,ensure_ascii=False).replace('<','\\u003c')+';\n',encoding='utf-8')
    print('Published catalog:',len(catalog['experiments']),'task experiments; historical versions are read from browser data.')
if __name__=='__main__':main()
