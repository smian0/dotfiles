#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["fastmcp"]
# ///
"""MD"""
import subprocess,sys
from pathlib import Path
from fastmcp import FastMCP
try:
    from .core import PATTERNS,MarkdownParser,safe_findall,safe_finditer,safe_search
    from .obsidian_engine import ObsidianEngine
    from .lint_engine import LintEngine
    from .mq_engine import MQEngine
    from .performance_engine import PerformanceEngine,Config,HAS_PSUTIL
    from .spec_engine import SpecEngine
except:
    sys.path.insert(0,str(Path(__file__).parent))
    from core import PATTERNS,MarkdownParser,safe_findall,safe_finditer,safe_search
    from obsidian_engine import ObsidianEngine
    from lint_engine import LintEngine
    from mq_engine import MQEngine
    from performance_engine import PerformanceEngine,Config,HAS_PSUTIL
    from spec_engine import SpecEngine
mcp=FastMCP()
o=ObsidianEngine()
l=LintEngine()
m=MQEngine()
p=PerformanceEngine()
s=SpecEngine()
@mcp.tool
def get_document_outline(x):
    """h"""
    c=p.get_cached_result(x,"document_outline")
    if c:return c
    a=Path(x)
    if not a.exists():return{"error":"!"}
    try:
        t=MarkdownParser.read_file(x)
        h=[{"level":len(i.group(1)),"title":i.group(2).strip(),"line":MarkdownParser.get_line_number(t,i.start()),"anchor":MarkdownParser.normalize_anchor(i.group(2).strip())}for i in safe_finditer(PATTERNS.HEADERS,t,Config.REGEX_TIMEOUT_SECONDS)]
        r={"file":x,"outline":h,"count":len(h)}
        p.cache_result(x,"document_outline",r)
        return r
    except Exception as e:return{"error":str(e)}
@mcp.tool
def extract_frontmatter(x):
    """y"""
    c=p.get_cached_result(x,"frontmatter")
    if c:return c
    a=Path(x)
    if not a.exists():return{"error":"!"}
    try:
        t=MarkdownParser.read_file(x)
        i=safe_search(PATTERNS.FRONTMATTER,t,Config.REGEX_TIMEOUT_SECONDS)
        if not i:r={"file":x,"has_frontmatter":False,"frontmatter":{}}
        else:
            d={}
            for n in i.group(1).split('\n'):
                if':'in n and not n.strip().startswith('#'):k,v=n.split(':',1);d[k.strip()]=v.strip().strip('"\'[]')
            r={"file":x,"has_frontmatter":True,"frontmatter":d}
        p.cache_result(x,"frontmatter",r)
        return r
    except Exception as e:return{"error":str(e)}
@mcp.tool
def find_code_blocks(x,g=None):
    """c"""
    w={"language":g}if g else None
    c=p.get_cached_result(x,"code_blocks",w)
    if c:return c
    a=Path(x)
    if not a.exists():return{"error":"!"}
    try:
        t=MarkdownParser.read_file(x)
        b=[{"language":i.group(1)or"text","code":i.group(2),"line":MarkdownParser.get_line_number(t,i.start()),"length":len(i.group(2).split('\n'))}for i in safe_finditer(PATTERNS.CODE_BLOCKS,t,Config.REGEX_TIMEOUT_SECONDS)if not g or(i.group(1)or"").lower()==g.lower()]
        r={"file":x,"code_blocks":b,"count":len(b),"languages":list(set(z["language"]for z in b))}
        p.cache_result(x,"code_blocks",r,w)
        return r
    except Exception as e:return{"error":str(e)}
@mcp.tool
def find_task_lists(x,z=None):
    """t"""
    w={"status":z}if z else None
    c=p.get_cached_result(x,"task_lists",w)
    if c:return c
    a=Path(x)
    if not a.exists():return{"error":"!"}
    try:
        t=MarkdownParser.read_file(x)
        k=[]
        for i in safe_finditer(PATTERNS.TASKS,t,Config.REGEX_TIMEOUT_SECONDS):
            d=i.group(1)=='x'
            if not z or(z=='completed'and d)or(z=='incomplete'and not d):k.append({"completed":d,"text":i.group(2),"line":MarkdownParser.get_line_number(t,i.start())})
        n=sum(1 for j in k if j["completed"])
        r={"file":x,"tasks":k,"summary":{"total":len(k),"completed":n,"incomplete":len(k)-n,"completion_rate":n/len(k)if k else 0}}
        p.cache_result(x,"task_lists",r,w)
        return r
    except Exception as e:return{"error":str(e)}
def _a(x):
    c=p.get_cached_result(x,"document_structure")
    if c:return c
    a=Path(x)
    if not a.exists():return{"error":"!"}
    try:
        t=MarkdownParser.read_file(x)
        u=Config.REGEX_TIMEOUT_SECONDS
        d={"headers":len(safe_findall(PATTERNS.HEADERS,t,u)),"wiki_links":len(safe_findall(PATTERNS.WIKI_LINKS,t,u)),"external_links":len(safe_findall(PATTERNS.EXTERNAL_LINKS,t,u)),"code_blocks":len(safe_findall(PATTERNS.CODE_BLOCKS,t,u)),"tasks":len(safe_findall(PATTERNS.TASKS,t,u)),"completed_tasks":len([i for i in safe_finditer(PATTERNS.TASKS,t,u)if i and i.group(1)=='x']),"tables":len(safe_findall(PATTERNS.TABLES,t,u)),"tags":len(set(safe_findall(PATTERNS.TAGS,t,u))),"embedded_content":len(safe_findall(PATTERNS.EMBEDDED,t,u)),"block_references":len(safe_findall(PATTERNS.BLOCK_REF,t,u)),"block_links":len(safe_findall(PATTERNS.BLOCK_LINK,t,u)),"header_links":len([i for i in safe_finditer(PATTERNS.HEADER_LINK,t,u)if i and'#^'not in i.group(0)]),"callouts":len(safe_findall(PATTERNS.CALLOUTS,t,u)),"dataview_fields":len(safe_findall(PATTERNS.DATAVIEW_FIELDS,t,u)),"wiki_aliases":len([i for i in safe_finditer(PATTERNS.WIKI_LINKS,t,u)if i and i.group(2)])}
        e=d["embedded_content"]+d["block_references"]+d["callouts"]+d["dataview_fields"]
        f=d["headers"]+d["wiki_links"]+d["code_blocks"]+d["tasks"]+d["tables"]
        r={"file":x,"structure":d,"content":{"lines":t.count('\n')+1,"words":len(t.split()),"characters":len(t)},"complexity_score":f+e,"obsidian_features":{"has_embedded":d["embedded_content"]>0,"has_block_refs":d["block_references"]>0,"has_callouts":d["callouts"]>0,"has_dataview":d["dataview_fields"]>0,"obsidian_score":e}}
        p.cache_result(x,"document_structure",r)
        return r
    except Exception as e:return{"error":str(e)}
@mcp.tool
def analyze_document_structure(x):
    """a"""
    return _a(x)
@mcp.tool
def find_obsidian_elements(x,y,f=None):
    """o"""
    if y=="wiki_links":return o.find_wiki_links(x,f)
    elif y=="embedded":return o.find_embedded_content(x,f)
    elif y=="blocks":return o.find_block_references(x)
    elif y=="callouts":return o.find_callouts(x,f)
    elif y=="dataview":return o.extract_dataview_fields(x,f)
    return{"error":"?"}
@mcp.tool
def parse_obsidian_links(x):
    """l"""
    return o.parse_obsidian_links(x)
@mcp.tool
def build_vault_graph(x):
    """v"""
    return o.build_vault_graph(x)
@mcp.tool
def find_cross_references(x,y):
    """x"""
    return o.find_cross_references(x,y)
@mcp.tool
def lint_document(x,f=False,y=None):
    """L"""
    return l.auto_fix_document(x,y)if f else l.lint_document(x)
@mcp.tool
def mq_query(x,q,f='json'):
    """q"""
    from pathlib import Path
    # Check if path is a directory and provide helpful error
    if Path(x).is_dir():
        return {"error": f"Path is a directory. Use 'mq_bulk_query' for querying multiple files in '{x}'"}
    return m.query(x,q,f)
@mcp.tool
def mq_bulk_query(x,q):
    """b"""
    return p.bulk_operation_optimized(x,lambda z:m.query(z,q,'json'),f"mq_{q}",batch_size=Config.MAX_BATCH_SIZE)
@mcp.tool
def analyze_docs(x):
    """d"""
    return m.analyze_docs(x)
@mcp.tool
def generate_toc(x,d=3):
    """T"""
    return m.generate_toc(x,d)
@mcp.tool
def task_stats(x):
    """s"""
    return m.task_stats(x)
@mcp.tool
def validate_spec(x,y="comprehensive"):
    """S"""
    k=f"spec_{y}"
    c=p.get_cached_result(x,k)
    if c:return c
    if y=="semantics":r=s.analyze_spec_semantics(x)
    elif y=="requirements":r=s.extract_spec_requirements(x)
    elif y=="constraints":r=s.extract_spec_constraints(x)
    elif y=="dependencies":r=s.extract_spec_dependencies(x)
    elif y=="completeness":r=s.validate_spec_completeness(x)
    else:r=s.validate_spec_document(x)
    p.cache_result(x,k,r)
    return r
@mcp.tool
def get_performance_stats():
    """p"""
    return p.get_performance_stats()
@mcp.tool
def clear_cache(y="all"):
    """C"""
    p.clear_cache(y)
    return{"status":"ok","message":f"cleared {y}"}
@mcp.tool
def bulk_analyze(x,n=100):
    """B"""
    # Convert n to int if it's a string (from MCP call)
    if isinstance(n, str):
        n = int(n)
    f=p.intelligent_file_discovery(x,"*.md",max_size_mb=50)
    if len(f)>n:f=f[:n]
    p.optimize_for_dataset(len(f),10)
    return p.bulk_operation_optimized(f,_a,"bulk_analyze",batch_size=Config.MAX_BATCH_SIZE)
@mcp.tool
def health_check():
    """H"""
    h="healthy"
    w=[]
    e=[]
    v="n/a"
    try:
        if HAS_PSUTIL:
            try:
                import psutil
                r=psutil.Process()
                v=r.memory_info().rss/(1024*1024)
                u=Config.MAX_MEMORY_MB
                if v>u*0.9:h="warning";w.append(f"mem:{v:.1f}/{u}")
                elif v>u:h="critical";e.append(f"mem>{u}")
            except:w.append("mem off")
        else:w.append("mem off")
        try:
            if not isinstance({"test":"ok"},dict):raise Exception("!")
        except Exception as x:h="critical";e.append(f"corrupt:{x}")
        try:
            z=p.get_performance_stats()
            if not isinstance(z,dict):raise Exception("!")
        except Exception as x:h="warning";w.append(f"perf:{x}")
        try:k=subprocess.run(["marksman","--version"],capture_output=True,timeout=3).returncode==0
        except:k=False
    except Exception as x:h="critical";e.append(f"fail:{x}");k=False
    return{"status":h,"marksman_available":k,"memory_info":{"current_mb":v if isinstance(v,(int,float))else"n/a","limit_mb":Config.MAX_MEMORY_MB,"usage_percent":(v/Config.MAX_MEMORY_MB*100)if isinstance(v,(int,float))else"n/a","monitoring":"on"if isinstance(v,(int,float))else"off"},"warnings":w,"errors":e,"capabilities":["h","y","c","t","a","o","l","v","x","L","q","b","d","T","s","S","p","C","B","H"],"version":"3.0-x"}
if __name__=="__main__":mcp.run(show_banner=False)