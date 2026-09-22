#!/usr/bin/env python3
# T2 (no-rules baseline, haiku, C4-C7, n=2) + T3 (rules, sonnet, all 8 cases, n=3). Same flags/validity as run.py.
# Measured first batch = 4 T3 sonnet runs; project; stop if the projected WHOLE-PROGRAM total would pass HARD_STOP.
import os,sys,json,subprocess,re,random,time
B=os.path.dirname(os.path.abspath(__file__)); SPENT_BEFORE=2.829; HARD_STOP=9.00
AG=json.load(open(f"{B}/agents2.json")); SC=json.load(open(f"{B}/scenarios.json")); os.makedirs(f"{B}/raw2",exist_ok=True)
T3=[("T3",c,r,"sonnet",SC[c][0]) for c in SC for r in (1,2,3)]; T2=[("T2",c,r,"haiku","baseline") for c in ("C4","C5","C6","C7") for r in (1,2)]
rng=random.SystemRandom(); rng.shuffle(T3); rest=T3[4:]+T2; rng.shuffle(rest); jobs=T3[:4]+rest
def launch(j):
    arm,c,r,model,ag=j; text=SC[c][1]
    P=(f"Use the Agent tool to launch the subagent named {ag} (subagent_type {ag}) in the FOREGROUND (do not run it in the background) and wait for its result. "
       f"Give it exactly the task between TASK START and TASK END. Then print its complete reply verbatim and nothing else.\nTASK START\n{text}\nTASK END")
    cmd=["perl","-e","alarm 300; exec @ARGV","claude","-p",P,"--agents",json.dumps({ag:AG[ag]}),"--allowedTools","Agent","--model",model,
         "--permission-mode","dontAsk","--strict-mcp-config","--mcp-config",'{"mcpServers":{}}',"--no-chrome","--output-format","stream-json","--verbose","--max-turns","6"]
    n=f"{arm}-{c}-r{r}"; return subprocess.Popen(cmd,cwd="/private/tmp",stdin=subprocess.DEVNULL,stdout=open(f"{B}/raw2/{n}.jsonl","w"),stderr=open(f"{B}/raw2/{n}.err","w"))
def cost(j):
    arm,c,r,_,_=j; m=0.0
    for line in open(f"{B}/raw2/{arm}-{c}-r{r}.jsonl",errors="replace"):
        try: e=json.loads(line)
        except Exception: continue
        if e.get("type")=="result": m=max(m,float(e.get("total_cost_usd") or 0))
    return m
spent=0.0; done=[]
def batch(js):
    global spent
    ps=[launch(j) for j in js]
    for p in ps: p.wait()
    for j in js: c=cost(j); spent+=c; done.append((j,c))
batch(jobs[:4]); avg_s=sum(c for j,c in done)/4
proj=SPENT_BEFORE+spent+avg_s*len([j for j in jobs[4:] if j[3]=="sonnet"])+0.045*len([j for j in jobs[4:] if j[3]=="haiku"])
print(f"measured batch: 4 sonnet runs, ${spent:.3f} (avg ${avg_s:.3f}); projected whole-program total ${proj:.2f} (hard stop ${HARD_STOP})")
if proj>HARD_STOP: print("PROJECTION BREAKS HARD STOP: stopping after the measured batch"); 
else:
    for i in range(4,len(jobs),4):
        if SPENT_BEFORE+spent>=HARD_STOP: print("hard stop reached"); break
        batch(jobs[i:i+4])
json.dump([[list(j),c] for j,c in done],open(f"{B}/run2-done.json","w"))
print(f"runs done: {len(done)} | spent this run ${spent:.3f} | whole program ${SPENT_BEFORE+spent:.3f}")
