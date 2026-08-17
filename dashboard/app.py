from pathlib import Path
import json
import pandas as pd
import streamlit as st

ROOT=Path(__file__).resolve().parents[1]
TOPOLOGY=ROOT/"configs/topology.json"
EVENTS=ROOT/"results/events.jsonl"
FLOWS=ROOT/"results/demo-2026-08-17/openflow-flows.txt"

st.set_page_config(page_title="SDN Sentinel",page_icon="🛡️",layout="wide",initial_sidebar_state="expanded")

st.markdown("""
<style>
:root{--bg:#11100e;--panel:#1b1916;--panel2:#24211c;--border:#41382c;--cream:#f4ead8;--muted:#b7aa95;--gold:#d8a24a;--green:#79c99a;--red:#d96b6b;--orange:#e28b4d;--purple:#a998d4}
.stApp{background:linear-gradient(145deg,#11100e 0%,#15130f 55%,#1b1712 100%);color:var(--cream)}
.block-container{max-width:1540px;padding:1.7rem 2.4rem 4rem}
[data-testid="stSidebar"]{background:#181612;border-right:1px solid var(--border)}
.hero{background:linear-gradient(135deg,#292119,#171511);border:1px solid #51422d;border-radius:20px;padding:28px 32px;box-shadow:0 18px 55px #0008;margin-bottom:24px}
.eyebrow{color:var(--gold);font-size:.7rem;font-weight:800;letter-spacing:.18em;text-transform:uppercase}.hero h1{font-size:2.6rem;letter-spacing:-.06em;margin:.35rem 0;color:var(--cream)}.hero p{color:var(--muted);font-size:1.03rem;margin:0}
.section{font-size:1.2rem;font-weight:750;color:var(--cream);margin:1.5rem 0 .7rem}.sub{color:var(--muted);font-size:.85rem;margin-bottom:.8rem}
.card{background:linear-gradient(145deg,#211e19,#171512);border:1px solid var(--border);border-radius:15px;padding:17px;min-height:108px}.label{color:var(--muted);font-size:.72rem;text-transform:uppercase;letter-spacing:.1em}.value{font-size:1.8rem;font-weight:800;margin-top:.3rem;color:var(--cream)}.hint{color:var(--muted);font-size:.76rem;margin-top:.2rem}
.status{border-radius:12px;padding:13px 16px;font-weight:750;letter-spacing:.04em}.active{background:#3b201c;color:#f39b78;border:1px solid #7b3d2c}.healthy{background:#1d3327;color:var(--green);border:1px solid #3d7754}
.topo{background:#171512;border:1px solid var(--border);border-radius:18px;padding:12px}.legend{display:flex;gap:18px;color:var(--muted);font-size:.78rem;margin:.7rem 0}.legend span{display:inline-flex;gap:5px;align-items:center}.dot{width:10px;height:10px;border-radius:50%;display:inline-block}.controller{background:var(--gold)}.switch{background:var(--purple)}.host{background:var(--green)}.attack{background:var(--red)}
.node{border:1px solid var(--border);border-radius:14px;background:#211e19;padding:13px;text-align:center;min-height:115px}.node-icon{font-size:2rem;line-height:1}.node-title{font-weight:800;margin-top:.4rem}.node-detail{color:var(--muted);font-size:.75rem;margin-top:.22rem}.node-state{display:inline-block;margin-top:.55rem;border-radius:999px;padding:3px 8px;font-size:.65rem;font-weight:800}.online{color:var(--green);background:#1e392a}.blocked{color:#ffaaa0;background:#4a211e}.control{color:var(--gold);background:#49381c}
.flow-card{background:#1b1916;border:1px solid var(--border);border-radius:14px;padding:13px 16px;margin:.45rem 0}.flow-path{font-family:monospace;color:var(--cream);font-size:.9rem}.flow-meta{color:var(--muted);font-size:.75rem;margin-top:4px}.flow-bar{height:7px;border-radius:5px;background:#302a22;margin-top:9px;overflow:hidden}.flow-fill{height:100%;border-radius:5px;background:var(--orange)}
[data-testid="stMetric"]{background:#1b1916;border:1px solid var(--border);border-radius:14px;padding:13px}
</style>
""",unsafe_allow_html=True)

def load(path,default):
    try:return json.loads(path.read_text()) if path.exists() else default
    except Exception:return default

def events():
    if not EVENTS.exists():return []
    out=[]
    for line in EVENTS.read_text().splitlines():
        try:out.append(json.loads(line))
        except:pass
    return out[-250:]

def drops():
    if not FLOWS.exists():return []
    return [x for x in FLOWS.read_text().splitlines() if "actions=drop" in x]

def icon(kind):
    return {"controller":"◉", "switch":"▣", "router":"◇", "host":"▰"}.get(kind,"●")

def color(kind):return {"controller":"controller","switch":"switch","router":"switch","host":"host"}.get(kind,"host")

def metric(label,value,hint):return f'<div class="card"><div class="label">{label}</div><div class="value">{value}</div><div class="hint">{hint}</div></div>'

def save_topology(data):
    TOPOLOGY.parent.mkdir(parents=True, exist_ok=True)
    TOPOLOGY.write_text(json.dumps(data, indent=2))

def node_card(n,attacks):
    is_attack=n["id"] in attacks
    state="ATTACK" if is_attack else ("CONTROL" if n.get("kind")=="controller" else "ONLINE")
    cls="blocked" if is_attack else ("control" if n.get("kind")=="controller" else "online")
    return f'<div class="node"><div class="node-icon">{icon(n.get("kind"))}</div><div class="node-title">{n.get("label",n["id"])}</div><div class="node-detail">{n.get("detail","")}</div><span class="node-state {cls}">{state}</span></div>'

def topology(data,attacks):
    """Render graph nodes with the exact same SVG-style glyph vocabulary as node cards."""
    try:
        import networkx as nx
        import plotly.graph_objects as go
        g=nx.Graph()
        for n in data["nodes"]: g.add_node(n["id"], **n)
        for e in data["links"]: g.add_edge(e["source"],e["target"],**e)
        pos=nx.spring_layout(g,seed=8,k=1.5)
        ex=[]; ey=[]
        for a,b in g.edges():
            ex += [pos[a][0],pos[b][0],None]
            ey += [pos[a][1],pos[b][1],None]
        edge=go.Scatter(x=ex,y=ey,mode="lines",line=dict(width=2,color="#8b7656"),hoverinfo="none")

        # Plotly marker symbols are selected by node kind, not by a generic circle.
        # This keeps the graph vocabulary aligned with the cards and legend.
        marker_symbol={
            "controller":"circle",
            "switch":"square",
            "router":"diamond",
            "host":"square",
        }
        palette={
            "controller":"#d8a24a",
            "switch":"#a998d4",
            "router":"#e28b4d",
            "host":"#79c99a",
        }
        traces=[edge]
        for kind in ["controller","switch","router","host"]:
            members=[(n,d) for n,d in g.nodes(data=True) if d.get("kind","host")==kind]
            if not members: continue
            x=[pos[n][0] for n,d in members]
            y=[pos[n][1] for n,d in members]
            labels=[f"{icon(kind)}  {d.get('label',n)}" for n,d in members]
            hover=[d.get("detail","") for n,d in members]
            colors=["#d96b6b" if n in attacks else palette[kind] for n,d in members]
            sizes=[39 if n in attacks else 31 for n,d in members]
            traces.append(go.Scatter(
                x=x,y=y,mode="markers+text",text=labels,textposition="bottom center",
                hovertext=hover,hoverinfo="text",name=kind.title(),
                marker=dict(symbol=marker_symbol[kind],size=sizes,color=colors,line=dict(color="#f4ead8",width=2))
            ))
        fig=go.Figure(traces)
        fig.update_layout(
            height=480,plot_bgcolor="#171512",paper_bgcolor="#171512",
            margin=dict(l=25,r=25,t=15,b=35),xaxis=dict(visible=False),yaxis=dict(visible=False),
            showlegend=True,legend=dict(orientation="h",y=-0.02,font=dict(color="#f4ead8")),
            hoverlabel=dict(bgcolor="#211e19",font_color="#f4ead8")
        )
        st.plotly_chart(fig,width="stretch",config={"displayModeBar":False})
    except Exception as e:
        st.warning(f"Topology visualization unavailable: {e}")

data=load(TOPOLOGY,{"nodes":[],"links":[]});rows=events();rules=drops();attack_events=[x for x in rows if x.get("event")=="ddos_detected"];attacks=set()
for e in attack_events:
    if e.get("source_node"):attacks.add(e["source_node"])
if rules and not attacks:attacks.add("h2")

with st.sidebar:
    st.markdown("## 🛡️ Sentinel")
    st.caption("Security operations console")
    page=st.radio("Navigation",["Overview","Local Lab Builder","Topology & Flow","Detections","OpenFlow Evidence","Runbook"],label_visibility="collapsed")
    st.divider();st.markdown("**Environment**")
    st.caption("Local authorized SDN laboratory")
    st.success("Controller online")
    st.success("Switch connected")
    if st.button("Refresh telemetry",width="stretch"):st.rerun()

st.markdown('<div class="hero"><div class="eyebrow">SDN security operations</div><h1>SDN Sentinel</h1><p>Explainable closed-loop DDoS detection and OpenFlow mitigation for authorized SDN laboratories.</p></div>',unsafe_allow_html=True)

if page=="Overview":
    st.markdown('<div class="section">Mission overview</div>',unsafe_allow_html=True)
    c=st.columns(4)
    for col,label,val,hint in zip(c,["Nodes online","Live events","Detected attacks","Drop rules"],[len(data["nodes"]),len(rows),len(attack_events),len(rules)],["Configured network","Controller telemetry","Confirmed detections","Active enforcement"]):
        with col:st.markdown(metric(label,val,hint),unsafe_allow_html=True)
    st.markdown('<br>',unsafe_allow_html=True)
    st.markdown(f'<div class="status {"active" if rules else "healthy"}">● {"MITIGATION ACTIVE · OpenFlow drop actions confirmed" if rules else "HEALTHY · No active mitigation evidence"}</div>',unsafe_allow_html=True)
    st.markdown('<div class="section">Security activity</div>',unsafe_allow_html=True)
    overview_data=pd.DataFrame({"metric":["Nodes","Events","Attacks","Drop rules"],"count":[len(data["nodes"]),len(rows),len(attack_events),len(rules)]})
    st.bar_chart(overview_data.set_index("metric")["count"],width="stretch",height=280,color="#d8a24a")
    st.markdown('<div class="section">Live network snapshot</div>',unsafe_allow_html=True)
    st.markdown('<div class="sub">Real topology symbols and current attack association.</div>',unsafe_allow_html=True)
    topology(data,attacks)
    cards=st.columns(min(6,max(1,len(data["nodes"]))))
    for col,n in zip(cards,data["nodes"]):
        with col:st.markdown(node_card(n,attacks),unsafe_allow_html=True)

elif page=="Local Lab Builder":
    st.markdown('<div class="section">Local lab builder</div>',unsafe_allow_html=True)
    st.markdown('<div class="sub">Create a safe topology definition for an authorized Mininet lab. This page edits the topology model only; it does not execute commands or change production networks.</div>',unsafe_allow_html=True)
    st.info("Design first, validate second, run the approved Mininet topology separately.")
    left,right=st.columns([1,1.6])
    with left:
        st.markdown("#### Add network node")
        kind=st.selectbox("Type",["host","switch","router","controller"],key="builder_kind")
        node_id=st.text_input("Name",value=f"{kind}{len(data['nodes'])+1}",key="builder_id")
        default_detail={"host":"10.0.0.10","switch":"OpenFlow 1.3","router":"Gateway","controller":"127.0.0.1:6633"}[kind]
        detail=st.text_input("Address or detail",value=default_detail,key="builder_detail")
        label=st.text_input("Display label",value=node_id,key="builder_label")
        if st.button("Add node",width="stretch",type="primary"):
            ids={n["id"] for n in data["nodes"]}
            if not node_id.strip(): st.error("Enter a node name.")
            elif node_id in ids: st.error("That node name already exists.")
            else:
                data["nodes"].append({"id":node_id.strip(),"kind":kind,"label":label.strip() or node_id.strip(),"detail":detail.strip()})
                save_topology(data); st.success(f"Added {kind} {node_id}."); st.rerun()
        st.markdown("#### Add network link")
        ids=[n["id"] for n in data["nodes"]]
        if len(ids)>=2:
            source=st.selectbox("From",ids,key="builder_source")
            target=st.selectbox("To",ids,index=1,key="builder_target")
            state=st.selectbox("Initial state",["healthy","control","attack"],key="builder_state")
            pps=st.number_input("Packets per second",min_value=0.0,value=0.0,step=1.0,key="builder_pps")
            if st.button("Add link",width="stretch"):
                if source==target: st.error("Source and target must differ.")
                elif any((e["source"]==source and e["target"]==target) or (e["source"]==target and e["target"]==source) for e in data["links"]): st.error("That link already exists.")
                else:
                    data["links"].append({"source":source,"target":target,"state":state,"pps":pps})
                    save_topology(data); st.success(f"Added link {source} → {target}."); st.rerun()
        else: st.warning("Add at least two nodes before creating a link.")
        st.markdown("#### Lab controls")
        if st.button("Reset topology model",width="stretch"):
            save_topology({"nodes":[],"links":[]}); st.rerun()
    with right:
        st.markdown("#### Current lab topology")
        st.caption(f"{len(data['nodes'])} nodes · {len(data['links'])} links")
        topology(data,attacks)
        cards=st.columns(min(4,max(1,len(data["nodes"]))))
        for col,n in zip(cards,data["nodes"]):
            with col: st.markdown(node_card(n,attacks),unsafe_allow_html=True)
        if data["nodes"]:
            st.markdown("#### Node inventory")
            inventory=pd.DataFrame([{"name":n["id"],"type":n.get("kind"),"label":n.get("label"),"detail":n.get("detail")} for n in data["nodes"]])
            st.dataframe(inventory,width="stretch",hide_index=True)

elif page=="Topology & Flow":
    st.markdown('<div class="section">Topology & network flow</div>',unsafe_allow_html=True)
    st.markdown('<div class="sub">Normal network notation with controller, switch, router, and endpoint symbols. Arrows describe observed paths.</div>',unsafe_allow_html=True)
    st.markdown('<div class="legend"><span><i class="dot controller"></i>Controller</span><span><i class="dot switch"></i>Switch</span><span><i class="dot host"></i>Host</span><span><i class="dot attack"></i>Attack source</span></div>',unsafe_allow_html=True)
    topology(data,attacks)
    st.markdown('<div class="section">Directional traffic</div>',unsafe_allow_html=True)
    maxpps=max([float(x.get("pps",0)) for x in data.get("links",[])]+[1])
    for link in data.get("links",[]):
        pps=float(link.get("pps",0));width=max(2,min(100,pps/maxpps*100))
        state=link.get("state","healthy");label=f'{link["source"]}  →  {link["target"]}'
        st.markdown(f'<div class="flow-card"><div class="flow-path">{label}</div><div class="flow-meta">{state.upper()} · {pps:,.2f} packets/s · {"control plane" if state=="control" else "data plane"}</div><div class="flow-bar"><div class="flow-fill" style="width:{width}%"></div></div></div>',unsafe_allow_html=True)

elif page=="Detections":
    st.markdown('<div class="section">Detection timeline</div>',unsafe_allow_html=True)
    st.markdown('<div class="sub">Explainable events received from the controller and runtime detector.</div>',unsafe_allow_html=True)
    if attack_events:
        df=pd.DataFrame(attack_events);cols=[x for x in ["event","source_node","source_mac","pps","bps","model_probability","detection_latency_ms","mitigation_latency_ms"] if x in df.columns];st.dataframe(df[cols],width="stretch",hide_index=True)
        charts=[x for x in ["pps","bps","detection_latency_ms","mitigation_latency_ms"] if x in df.columns]
        if charts:st.line_chart(df[charts],width="stretch",height=320)
    else:st.info("No structured detections recorded yet.")

elif page=="Runbook":
    st.markdown('<div class="section">Authorized lab runbook</div>',unsafe_allow_html=True)
    st.markdown('<div class="sub">A reproducible, evidence-first workflow for the local SDN experiment.</div>',unsafe_allow_html=True)
    steps=[
        ("01","Start controller","ryu-manager src/controller/monitor.py","Ryu must be listening before the switch connects."),
        ("02","Start topology","sudo python3 scripts/custom_topology.py","Use only the approved local Mininet topology."),
        ("03","Verify baseline","pingall","Confirm normal connectivity before generating traffic."),
        ("04","Run controlled traffic","h2 ping -f h1","Use only authorized lab traffic."),
        ("05","Verify mitigation","ovs-ofctl -O OpenFlow13 dump-flows s1","Confirm priority, counters, timeout, and drop action."),
        ("06","Measure recovery","ping -c 10 h1","Record recovery after traffic stops and rules expire.")]
    for num,title,command,detail in steps:
        st.markdown(f'<div class="flow-card"><div class="label">Step {num}</div><div class="flow-path">{title}</div><div class="flow-meta">{detail}</div></div>',unsafe_allow_html=True)
        st.code(command,language="bash")
    st.warning("This runbook is documentation only. The dashboard does not execute these commands.")

else:
    st.markdown('<div class="section">Confirmed OpenFlow evidence</div>',unsafe_allow_html=True)
    st.markdown('<div class="sub">Rules are read-only evidence captured from the authorized laboratory switch.</div>',unsafe_allow_html=True)
    if rules:
        for i,r in enumerate(rules,1):
            st.markdown(f'<div class="flow-card"><div class="label">Drop rule {i}</div><div class="flow-meta">Priority 500 · timed enforcement · action: drop</div></div>',unsafe_allow_html=True)
            st.code(r,language="text")
    else:st.info("No OpenFlow drop rules captured.")

st.markdown('<div style="color:#8f8575;margin-top:36px;font-size:.78rem">SDN Sentinel is a local research prototype. It is not a production DDoS protection service.</div>',unsafe_allow_html=True)
