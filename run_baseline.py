"""Five fresh baseline trials. Intermediate-state evaluator reasons before scoring."""
import sys,os,json,time,argparse,urllib.request,hashlib
from pathlib import Path
from datetime import datetime,timezone
root=Path(__file__).resolve().parent
sys.path.insert(0,str(root/'src'))
import tot.models as models
import tot.methods.bfs as bfs
from tot.tasks.game24 import Game24Task
parser=argparse.ArgumentParser()
parser.add_argument('--condition', choices=['baseline','label_only'], default='baseline')
condition=parser.parse_args().condition
os.environ['TOT_EVALUATION']='reasoning' if condition=='baseline' else 'label_only'
out=root/'results'/condition;out.mkdir(parents=True,exist_ok=True)
if (out/'manifest.json').exists(): raise SystemExit('Existing experiment found; refusing to overwrite or repeat paid calls.')
cfg=dict(l.split('=',1) for l in (root/'.env').read_text().splitlines() if '=' in l)
def balance():
 req=urllib.request.Request('https://api.deepseek.com/user/balance',headers={'Authorization':'Bearer '+cfg['DEEPSEEK_API_KEY'].strip()})
 with urllib.request.urlopen(req,timeout=20) as r: data=json.load(r)
 return next(float(x['total_balance']) for x in data['balance_infos'] if x['currency']=='CNY')
initial=balance(); args=argparse.Namespace(backend='deepseek-chat',temperature=0.7,method_generate='propose',method_evaluate='value',method_select='greedy',n_generate_sample=1,n_evaluate_sample=3,n_select_sample=5)
manifest=dict(started=datetime.now(timezone.utc).isoformat(),indices=list(range(901,906)),config=vars(args),initial_balance_cny=initial,batch_spend_limit_cny=10,condition=condition,description='Fresh trials; no replay; only intermediate-state reasoning differs between conditions; final-answer judge unchanged.')
manifest['files_sha256']={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [root/'src/tot/models.py',root/'src/tot/methods/bfs.py']}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2))
original_chat=models.chatgpt
last_checked=-1
class BudgetStop(RuntimeError): pass
def guarded(*a,**kw):
 global last_checked
 if models.calls//10!=last_checked:
  current=balance();last_checked=models.calls//10
  if initial-current>=9.5 or current<1: raise BudgetStop('Balance spending guard reached')
 result=original_chat(*a,**kw)
 if models.calls%10==0: print(f'  {models.calls} calls; {models.prompt_tokens+models.completion_tokens} tokens',flush=True)
 return result
models.chatgpt=guarded
summary=[]
for number,index in enumerate(manifest['indices'],1):
 models.calls=models.prompt_tokens=models.completion_tokens=0;last_checked=-1
 os.environ['TOT_CALL_LIMIT']='600';os.environ['TOT_LOG']=f'results/{condition}/api-{index}.jsonl'
 task=Game24Task();bfs.gpt=models.gpt
 start=time.time();print(f'START {number}/5 | index {index} | numbers {task.get_input(index)}',flush=True)
 record=dict(condition=condition,index=index,input=task.get_input(index),config=vars(args))
 stop_batch=False
 try:
  ys,info=bfs.solve(args,task,index,to_print=False)
  scores=[task.test_output(index,y)['r'] for y in ys]
  record.update(status='completed',outputs=ys,scores=scores,success=any(scores),info=info)
 except Exception as e:
  record.update(status='interrupted',error=f'{type(e).__name__}: {e}',success=None)
  stop_batch=isinstance(e,BudgetStop)
 record.update(seconds=time.time()-start,usage=models.gpt_usage())
 (out/f'result-{index}.json').write_text(json.dumps(record,indent=2))
 summary.append({k:v for k,v in record.items() if k not in ['info','outputs','config']})
 (out/'summary.json').write_text(json.dumps(summary,indent=2))
 print(f'END {number}/5 | {record["status"]} | success={record["success"]} | {record["seconds"]:.1f}s',flush=True)
 if stop_batch: break
manifest.update(finished=datetime.now(timezone.utc).isoformat(),final_balance_cny=balance())
(out/'manifest.json').write_text(json.dumps(manifest,indent=2))
print('BATCH FINISHED',flush=True)
