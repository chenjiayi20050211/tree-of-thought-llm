import os, json, time, urllib.request, re
from pathlib import Path
completion_tokens = prompt_tokens = calls = 0
ROOT = Path(os.getenv("TOT_ROOT", str(Path(__file__).resolve().parents[2])))
def gpt(prompt, model="deepseek-chat", temperature=0.7, max_tokens=1000, n=1, stop=None):
    if 'Possible next steps:' in prompt:
        rule = 'Continue the last example. Output ONLY lines of the form a + b = c (left: d e c), using + - * /. No headings, bullets, markdown, explanations or questions.'
    elif 'Judge:' in prompt:
        rule = 'Output exactly one lowercase word: sure or impossible. No other text.'
    elif prompt.startswith('Evaluate if'):
        rule = 'Evaluate the final input following the examples. Show your arithmetic reasoning first. End with a separate final line containing exactly one lowercase word: sure, likely, or impossible. No text after that line.'
        if os.getenv('TOT_EVALUATION', 'reasoning') == 'label_only':
            rule = 'Evaluate the final input. Output exactly one lowercase word: sure, likely, or impossible. No other text.'
    else:
        rule = 'Continue the last solution. Output only one line: Answer: <arithmetic expression using each original input once> = 24. No commentary.'
    return chatgpt([{"role":"system","content":rule},{"role":"user","content":prompt}], model, temperature, max_tokens, n, stop)
def chatgpt(messages, model="deepseek-chat", temperature=0.7, max_tokens=1000, n=1, stop=None):
    global completion_tokens, prompt_tokens, calls
    config_path = Path(os.getenv("TOT_CONFIG", str(ROOT / ".env")))
    cfg = dict(l.split("=", 1) for l in config_path.read_text().splitlines() if "=" in l and not l.lstrip().startswith("#")) if config_path.exists() else {}
    cfg["DEEPSEEK_API_KEY"] = os.getenv("DEEPSEEK_API_KEY", cfg.get("DEEPSEEK_API_KEY", ""))
    if not cfg["DEEPSEEK_API_KEY"].strip(): raise RuntimeError("Set DEEPSEEK_API_KEY or create .env")
    outputs=[]
    for _ in range(n):
        if (ROOT / "STOP").exists(): raise RuntimeError("Paused for format investigation")
        if calls >= int(os.getenv("TOT_CALL_LIMIT", "150")) or prompt_tokens + completion_tokens >= 500000:
            raise RuntimeError("Conservative experiment usage cap reached")
        payload=dict(model=model,messages=messages,temperature=temperature,max_tokens=max_tokens)
        if stop: payload["stop"]=stop
        req=urllib.request.Request("https://api.deepseek.com/chat/completions",data=json.dumps(payload).encode(),headers={"Authorization":"Bearer "+cfg["DEEPSEEK_API_KEY"].strip(),"Content-Type":"application/json"})
        t=time.time()
        with urllib.request.urlopen(req,timeout=120) as response: data=json.load(response)
        calls+=1
        usage=data["usage"]
        prompt_tokens+=usage["prompt_tokens"]; completion_tokens+=usage["completion_tokens"]
        output=data["choices"][0]["message"]["content"]
        outputs.append(output)
        with (ROOT / os.getenv("TOT_LOG", "adapted-api-log.jsonl")).open("a") as f:
            f.write(json.dumps(dict(call=calls,model=data.get("model"),seconds=time.time()-t,usage=usage,prompt=messages,output=output))+"\n")
    return outputs
def gpt_usage(backend="deepseek-chat"):
    return dict(completion_tokens=completion_tokens,prompt_tokens=prompt_tokens,calls=calls,cost=None)
