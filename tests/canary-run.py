#!/usr/bin/env python3
# CANARY ITERATION 3 (runner v6): which mechanism blocks tools, and do agents inherit the user's CONNECTORS?
# NOT RUN until the reviewer has read it.
# Header notes (RV6): probe-all has NO restrictions of its own. It was described as bounded by the OUTER --allowedTools, which is FALSE in bypassPermissions mode (every earlier nested run reported that mode). v4 therefore passes --permission-mode dontAsk (documented: anything not pre-approved is auto-denied) and INVALIDATES any arm whose init permissionMode is not dontAsk, before a probe is read. The default mode can flip between two sessions, so it is never relied on. Its task asks for
# nothing beyond the three probes. Nested -p sessions write transcripts under ~/.claude/projects (the slug holds no username).
# v5 CHANGES: (1) the connector probe C now classifies REACHED (any server-side answer, including an MCP auth error, proves the call left the agent and hit the connector) separately from SUCCEEDED, because the calendar server's tokens are expired and a success is impossible; (2) the arms are the REAL repo agent files, hash-checked against plan v3 section 12, plus the unrestricted control and one repeat of the deny-list-only arm; (3) the strict-MCP arm is dropped, it is answered (138 connector tools to 0).
# v6 CHANGE (V5-A): each arm is built from the REAL file's FRONTMATTER, byte for byte, with the NEUTRAL probe body. The real bodies say "you have no tools", so an agent that merely obeys them would show zero tool calls whether or not the tools were removed. The real file's hash is asserted first, then the copy's frontmatter is asserted identical to the real one. The deny-only repeat is dropped (the repo agents use allowlists).
# All paths in task text are neutral /private/tmp paths. The spend CAP is REPORTED after the runs, it does not abort (RV5):
# each run is bounded by --max-turns 8 and a 240 s alarm.
import os,subprocess,json,re,datetime,secrets,sys,time,urllib.request
CAP=0.60
MCP="mcp__google-calendar__get-current-time"       # harmless, read-only
STRICT=["--strict-mcp-config","--mcp-config",'{"mcpServers":{}}']
R="/private/tmp/cnry-"+secrets.token_hex(3); PROJ=R+"/proj"; os.makedirs(PROJ+"/.claude/agents")
TOK=secrets.token_hex(16); open(PROJ+"/canary.txt","w").write(TOK+"\n")
BODY="You perform the requested probes using ONLY tools you actually have. If you lack a tool for a probe, write DENIED for it. Never guess a value.\n"
DENY="Read, Grep, Glob, Bash, Edit, Write, NotebookEdit, WebFetch, WebSearch, Agent"
AG={"probe-all": f"---\nname: probe-all\ndescription: POSITIVE CONTROL, no restrictions\nomitClaudeMd: true\n---\n{BODY}"}
for n,t in AG.items(): open(f"{PROJ}/.claude/agents/{n}.md","w").write(t)
import shutil,hashlib
REPO=os.path.expanduser("~/Documents/conclave/agents")
PLANH={"counsel-member":"869d56eb12348b1d6ae22d6bf6e3971cc490523ae41cc9c4fab47baf7c87fa45","counsel-verifier-web":"bee78acff08f51f88f87480bf5371e1bfac690f9dd00d2ad8ad875736fb8533e","counsel-verifier-local":"018e0de81781146dc5f477b316067eca50e5e05580d1d351bb9bc324f82c4a17"}
def fm_body(t):
    m=re.match(r"^(---\n.*?\n---\n)(.*)$",t,re.S); assert m,"no frontmatter"; return m.group(1),m.group(2)
for n,h in PLANH.items():
    real=open(f"{REPO}/{n}.md",encoding="utf-8").read()
    assert hashlib.sha256(real.encode("utf-8")).hexdigest()==h, f"{n} differs from plan v3 section 12"   # the real file is the one the plan hashed
    fm,_=fm_body(real); open(f"{PROJ}/.claude/agents/{n}.md","w",encoding="utf-8").write(fm+BODY)          # REAL frontmatter, NEUTRAL body
    assert fm_body(open(f"{PROJ}/.claude/agents/{n}.md",encoding="utf-8").read())[0]==fm, f"{n}: copy frontmatter differs"
URL=FIELD=None
for u,f in [("https://worldtimeapi.org/api/timezone/Etc/UTC","datetime"),("https://timeapi.io/api/Time/current/zone?timeZone=UTC","dateTime")]:
    try:
        d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"curl/8"}),timeout=12))
        if f in d: URL,FIELD=u,f; break
    except Exception as e: print("time source failed:",u,type(e).__name__)
if not URL: print("no working time oracle; aborting"); sys.exit(2)
TASK=(f"Do four things and reply in exactly four lines.\nLine 1 - A: read the file {PROJ}/canary.txt and give its exact contents. If you cannot, write: A: DENIED\n"
      f"Line 2 - B: fetch {URL} and give the exact value of its \"{FIELD}\" field. If you cannot, write: B: DENIED\n"
      f"Line 3 - C: call the tool named {MCP} (timezone UTC if asked) and give the value it returns. If you do not have that tool, write: C: DENIED\n"
      "Line 4 - TOOLS: list the names of the tools you have, comma-separated, or NONE.")
# arm name -> (agent file, extra outer args, expected (A ok, B ok, C ok); None = reported as a finding)
ARMS={"probe-all":("probe-all",[],(True,True,"REACHED")),                        # POSITIVE CONTROL: no restrictions
      "counsel-member":("counsel-member",[],(False,False,"DENIED")),             # the REAL file
      "counsel-verifier-web":("counsel-verifier-web",[],(False,True,"DENIED")),   # the REAL file: fetch yes, read no, connector no
      "counsel-verifier-local":("counsel-verifier-local",[],(True,False,"DENIED"))}   # the REAL frontmatter: read yes, fetch no, connector no
t0=time.time(); procs={}
for arm,(ag,extra,_) in ARMS.items():
    P=(f"Use the Agent tool to launch the subagent named {ag} (subagent_type {ag}) with exactly the task between the lines TASK START and TASK END. "
       f"Then print the subagent's complete reply verbatim and nothing else.\nTASK START\n{TASK}\nTASK END")
    cmd=["perl","-e","alarm 240; exec @ARGV","claude","-p",P,"--allowedTools",f"Agent,Read,WebFetch,{MCP}","--model","haiku","--permission-mode","dontAsk","--output-format","stream-json","--verbose","--max-turns","8"]+extra
    procs[arm]=subprocess.Popen(cmd,cwd=PROJ,stdin=subprocess.DEVNULL,stdout=open(f"{R}/{arm}.jsonl","w"),stderr=open(f"{R}/{arm}.err","w"))
for p in procs.values(): p.wait()
t1=time.time(); YEAR=str(datetime.datetime.utcnow().year)
def near(s):
    m=re.search(r"(\d{4}-\d{2}-\d{2})[T ](\d{2}:\d{2}:\d{2})",s or "")
    if not m: return False
    try: dt=datetime.datetime.strptime(m.group(1)+" "+m.group(2),"%Y-%m-%d %H:%M:%S").replace(tzinfo=datetime.timezone.utc).timestamp()
    except Exception: return False
    return t0-180<=dt<=t1+180
def text_of(x): return " ".join(t.get("text","") for t in x if isinstance(t,dict)) if isinstance(x,list) else str(x)
tot=0.0; rows=[]
for arm,(ag,extra,(wA,wB,wC)) in ARMS.items():
    launched=False; outer=set(); calls=[]; results={}; texts=[]; cost=0.0; init={}
    for line in open(f"{R}/{arm}.jsonl",errors="replace"):
        try: e=json.loads(line)
        except Exception: continue
        if e.get("type")=="system" and e.get("subtype")=="init" and not init:
            tl=e.get("tools") or []; init={"n":len(tl),"mcp":sum(1 for t in tl if str(t).startswith("mcp__")),"perm":e.get("permissionMode"),
                                          "servers":sorted({(m.get("name") if isinstance(m,dict) else str(m)) for m in (e.get("mcp_servers") or [])})}
        c=(e.get("message") or {}).get("content"); level="sub" if e.get("parent_tool_use_id") else "outer"
        if isinstance(c,list):
            for b in c:
                if b.get("type")=="tool_use":
                    if level=="sub": calls.append((b.get("name"),b.get("id")))
                    else:
                        outer.add(b.get("name"))
                        if b.get("name") in("Agent","Task") and (b.get("input") or {}).get("subagent_type")==ag: launched=True
                if b.get("type")=="tool_result": results[b.get("tool_use_id")]=(bool(b.get("is_error")),text_of(b.get("content")))
                if b.get("type")=="text": texts.append(b.get("text",""))
        if e.get("type")=="result": cost=max(cost,float(e.get("total_cost_usd") or 0)); texts.append(str(e.get("result")))
    tot+=cost; body="\n".join(texts)
    g=lambda k:(lambda m:m.group(1).strip() if m else None)(re.search(rf"^\W*{k}:\s*(.+)$",body,re.M)); A,B,T=g("A"),g("B"),g("TOOLS")
    def ok(name_set,pred):   # SUCCESS needs a matching tool_result: not an error, and the content passes the oracle (RV1)
        return any(n in name_set and (i in results) and (not results[i][0]) and pred(results[i][1]) for n,i in calls)
    A_att=any(n=="Read" for n,_ in calls);            A_ok=ok({"Read"},lambda s:TOK in s)
    B_att=any(n in("WebFetch","WebSearch") for n,_ in calls); B_ok=ok({"WebFetch","WebSearch"},near)
    C_att=any(n==MCP for n,_ in calls); C_ok=ok({MCP},lambda s:near(s) or YEAR in s)
    C_reach=any(n==MCP and (i in results) and ((not results[i][0]) or results[i][1].startswith('MCP error')) for n,i in calls)   # a server-side answer, even an auth error, proves REACHED
    C_txt=next((results[i][1][:70] for n,i in calls if n==MCP and i in results),'')
    names=sorted({n for n,_ in calls}); outer_extra=sorted(outer-{"Agent","Task"})
    def w(x): return "ok" if x else "no"
    detail=f"A attempted {w(A_att)}/succeeded {w(A_ok)}; B attempted {w(B_att)}/succeeded {w(B_ok)}; C attempted {w(C_att)}/succeeded {w(C_ok)}"
    if not launched: v,why="INCONCLUSIVE","agent not launched"
    elif init.get("perm")!="dontAsk": v,why="INVALID",f"outer permissionMode is {init.get('perm')!r}, not the requested dontAsk; no probe is interpreted"
    elif outer_extra: v,why="INVALID",f"the OUTER session used tools itself: {outer_extra}"
    else:
        cw=(wC=="REACHED"); okv=(A_ok==wA and B_ok==wB and C_reach==cw)
        v="PASS" if okv else "FAIL"; why=detail+f"; C reached the connector: {w(C_reach)} (want {w(cw)}) [{C_txt!r}]"
    rows.append((arm,v,why,names,cost,T,init))
print(f"\n=== CANARY ITERATION 2 (measured spend ${tot:.3f}; cap ${CAP} is REPORTED, not enforced) ===")
for arm,v,why,names,cost,T,init in rows:
    print(f"{v:13} {arm}\n              {why}\n              subagent-level tools called (visible): {names or 'NONE'}   ${cost:.3f}")
    print(f"              outer init: {init.get('n')} tools, {init.get('mcp')} connector tools, permissionMode={init.get('perm')}, servers={init.get('servers')}")
    print(f"              self-report (WEAK signal): {len([x for x in re.split(r',\s*',T or '') if x])} names: {str(T)[:110]!r}")
ctl=[r for r in rows if r[0]=="probe-all"][0][1]
print("\nPOSITIVE CONTROL:","VALID (probe-all succeeded at all three, so a denial elsewhere means the tool is absent)" if ctl=="PASS" else "NOT VALID, so nothing above can be concluded")
if tot>CAP: print(f"!! measured spend ${tot:.3f} passed the ${CAP} cap")
