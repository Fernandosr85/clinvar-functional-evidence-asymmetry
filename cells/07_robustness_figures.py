# 07_robustness_figures.py
#
# Section 7 of the notebook one_paper_two_readings.ipynb, extracted verbatim.
#
# THIS FILE DOES NOT RUN ON ITS OWN. It is a notebook cell, and it expects
# nothing from the kernel - the measured values are constants at the top
# to already exist in the kernel. The cells run in order, in one kernel, and
# cell 01 bootstraps the classifier notebook that defines `subs` and `classify`.
# To reproduce, run the notebook; these files are here to be read and diffed.
#
# Extracted from the stored run of 26-29 September 2026. Byte-identical to the
# notebook cell: sha256 of the cell source is
# 91a14d0fb931613f6359e488865fdf8f4d9e64dd6cd7a93d45eaf40f9ece2faa

"""
Figures for section 7. Pure HTML and SVG, no charting library.

The two constants at the top of the <script> block hold the measured values:
  RUNS   - the five recomputation scenarios, with claims, denials and the ratio
  CAUSES - the four defects, with the change each makes to the ratio

Everything else is geometry. The values are transcribed from the section 6 output
above so the figures render without re-running the pipeline; the table view under
each figure carries the same numbers for checking.
"""

from IPython.display import HTML, display

FIGURES = r"""
<div class="viz-root" id="viz">
<style>
.viz-root{
  color-scheme: light;
  --surface-1:#fcfcfb; --text-primary:#0b0b0b; --text-secondary:#52514e;
  --text-muted:#898781; --grid:#e1e0d9; --axis:#c3c2b7;
  --claims:#2a78d6; --denials:#eb6834; --up:#2a78d6; --down:#e34948; --mid:#f0efec;
  background:var(--surface-1); color:var(--text-primary);
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
  padding:4px 0 10px; max-width:920px;
}
@media (prefers-color-scheme: dark){
  :root:where(:not([data-theme="light"])) .viz-root{
    color-scheme: dark;
    --surface-1:#1a1a19; --text-primary:#ffffff; --text-secondary:#c3c2b7;
    --text-muted:#898781; --grid:#2c2c2a; --axis:#383835;
    --claims:#3987e5; --denials:#d95926; --up:#3987e5; --down:#e66767; --mid:#383835;
  }
}
:root[data-theme="dark"] .viz-root{
  color-scheme: dark;
  --surface-1:#1a1a19; --text-primary:#ffffff; --text-secondary:#c3c2b7;
  --text-muted:#898781; --grid:#2c2c2a; --axis:#383835;
  --claims:#3987e5; --denials:#d95926; --up:#3987e5; --down:#e66767; --mid:#383835;
}
.viz-root h3{font-size:15px;margin:18px 0 2px;font-weight:600;color:var(--text-primary)}
.viz-root p.sub{font-size:12.5px;margin:0 0 10px;color:var(--text-secondary);max-width:760px;line-height:1.45}
.viz-root .lg{display:flex;gap:16px;align-items:center;font-size:12px;color:var(--text-secondary);margin:0 0 6px}
.viz-root .lg i{display:inline-block;width:11px;height:11px;border-radius:2px;margin-right:5px;vertical-align:-1px}
.viz-root details{margin-top:8px;font-size:12px;color:var(--text-secondary)}
.viz-root summary{cursor:pointer;color:var(--text-muted)}
.viz-root table{border-collapse:collapse;margin-top:8px;font-size:12px}
.viz-root th,.viz-root td{padding:3px 12px 3px 0;text-align:left;border-bottom:1px solid var(--grid);white-space:nowrap}
.viz-root th{color:var(--text-muted);font-weight:600}
.viz-tip{position:fixed;pointer-events:none;opacity:0;transition:opacity .08s;
  background:var(--text-primary);color:var(--surface-1);font-size:11.5px;line-height:1.5;
  padding:6px 9px;border-radius:5px;z-index:9999;white-space:nowrap}
</style>

<h3>Does any pipeline defect overturn the published result?</h3>
<p class="sub">Each row recomputes the panel counts changing <b>one</b> thing. The ratio stays below parity in
every scenario: denials outnumber claims throughout. Scenarios A and B are full recomputations; C is a
pattern-based upper bound that over-counts, and is shown as such.</p>
<div class="lg"><span><i style="background:var(--claims)"></i>claims</span><span><i style="background:var(--denials)"></i>denials</span></div>
<div id="f1"></div>
<details><summary>data table</summary><div id="t1"></div></details>

<h3>Where the change comes from</h3>
<p class="sub">Change in the claims/denials ratio attributable to each defect, measured separately against the
published value of 0.805. Two of the four move nothing at all.</p>
<div id="f2"></div>
<details><summary>data table</summary><div id="t2"></div></details>

<script>
// ---------------------------------------------------------------- data
const RUNS = [
  {id:"published", label:"published",            note:"as released",                       claims:1218, denials:1513, ratio:0.805, kind:"base"},
  {id:"A",         label:"A · gene filter",      note:"dropped rows restored",             claims:1329, denials:1536, ratio:0.865, kind:"recompute"},
  {id:"B",         label:"B · sentence splitter",note:"bullet-aware split",                claims:1218, denials:1513, ratio:0.805, kind:"recompute"},
  {id:"C",         label:"C · negated claims",   note:"tier-1 removed — upper bound",      claims:1201, denials:1513, ratio:0.794, kind:"estimate"},
  {id:"D",         label:"D · missed denials",   note:"none found",                        claims:1218, denials:1513, ratio:0.805, kind:"estimate"}
];

const CAUSES = [
  {id:"A", label:"Gene-field filter",   detail:"4,007 rows on panel variants dropped; 354 with prose. The dropped set is claim-rich (111 vs 23).", delta:+0.060, measured:true},
  {id:"B", label:"Sentence splitter",   detail:"Splitting at bullets as well changes 0 of 32,562 submissions.",                                    delta: 0.000, measured:true},
  {id:"C", label:"Negated claim text",  detail:"Tier-1 pattern flags 17; reading the printed examples, most are genuine claims with a caveat.",    delta:-0.011, measured:false},
  {id:"D", label:"Missed denial text",  detail:"'<functional> studies have not been performed' matches 0 unflagged submissions.",                  delta: 0.000, measured:true}
];

// ------------------------------------------------------------- helpers
const NS="http://www.w3.org/2000/svg";
const el=(n,a={})=>{const e=document.createElementNS(NS,n);for(const k in a)e.setAttribute(k,a[k]);return e;};
const txt=(x,y,s,o={})=>{const t=el("text",Object.assign({x,y},o));t.textContent=s;return t;};
const fmt=n=>n.toLocaleString("en-US");

// bar with a 4px rounded data-end, square at the baseline
function bar(x0,y,w,h,fill,r=4){
  if(w<=0.5) return el("g");
  const rr=Math.min(r,w);
  const d=`M${x0},${y} H${x0+w-rr} A${rr},${rr} 0 0 1 ${x0+w},${y+rr} V${y+h-rr} A${rr},${rr} 0 0 1 ${x0+w-rr},${y+h} H${x0} Z`;
  return el("path",{d,fill});
}
// mirrored for bars growing left from a zero baseline
function barL(x0,y,w,h,fill,r=4){
  if(w<=0.5) return el("g");
  const rr=Math.min(r,w);
  const d=`M${x0},${y} H${x0-w+rr} A${rr},${rr} 0 0 0 ${x0-w},${y+rr} V${y+h-rr} A${rr},${rr} 0 0 0 ${x0-w+rr},${y+h} H${x0} Z`;
  return el("path",{d,fill});
}

// one shared tooltip
const tip=document.createElement("div"); tip.className="viz-tip"; document.body.appendChild(tip);
function hover(node,html){
  node.style.cursor="default";
  node.addEventListener("mousemove",e=>{tip.innerHTML=html;tip.style.opacity=1;
    tip.style.left=Math.min(e.clientX+14,innerWidth-tip.offsetWidth-8)+"px";
    tip.style.top=(e.clientY-tip.offsetHeight-10)+"px";});
  node.addEventListener("mouseleave",()=>tip.style.opacity=0);
}

// ------------------------------------------------- figure 1 · scenarios
(function(){
  const W=900, ROW=56, TOP=42, LAB=178,
        CX0=LAB+10, CX1=560, RX0=642, RX1=868,
        H=TOP+RUNS.length*ROW+40;
  const cmax=1700, rmax=1.10;
  const cx=v=>CX0+(v/cmax)*(CX1-CX0);
  const rx=v=>RX0+(v/rmax)*(RX1-RX0);
  const svg=el("svg",{width:"100%",viewBox:`0 0 ${W} ${H}`,role:"img",
    "aria-label":"Claims and denials per scenario, and the claims-to-denials ratio against parity"});

  svg.appendChild(txt(CX0,20,"submissions",{fill:"var(--text-muted)","font-size":11}));
  svg.appendChild(txt(RX0,20,"claims / denials",{fill:"var(--text-muted)","font-size":11}));

  // count gridlines
  for(let v=0;v<=cmax;v+=500){
    svg.appendChild(el("line",{x1:cx(v),y1:TOP-8,x2:cx(v),y2:TOP+RUNS.length*ROW-6,
      stroke:"var(--grid)","stroke-width":1}));
    svg.appendChild(txt(cx(v),TOP+RUNS.length*ROW+14,fmt(v),
      {fill:"var(--text-muted)","font-size":10.5,"text-anchor":"middle"}));
  }
  // ratio axis + parity reference
  [0,0.5,1.0].forEach(v=>{
    svg.appendChild(el("line",{x1:rx(v),y1:TOP-8,x2:rx(v),y2:TOP+RUNS.length*ROW-6,
      stroke:v===1?"var(--axis)":"var(--grid)","stroke-width":1}));
    svg.appendChild(txt(rx(v),TOP+RUNS.length*ROW+14,v.toFixed(1),
      {fill:"var(--text-muted)","font-size":10.5,"text-anchor":"middle"}));
  });
  svg.appendChild(txt(rx(1.0),TOP-14,"parity",{fill:"var(--text-secondary)","font-size":10.5,"text-anchor":"middle"}));

  RUNS.forEach((r,i)=>{
    const y=TOP+i*ROW;
    svg.appendChild(txt(0,y+18,r.label,{fill:"var(--text-primary)","font-size":12.5,
      "font-weight":r.kind==="base"?600:400}));
    svg.appendChild(txt(0,y+33,r.note,{fill:"var(--text-muted)","font-size":10.5}));

    const bc=bar(CX0,y+4,cx(r.claims)-CX0,18,"var(--claims)");
    hover(bc,`<b>${r.label}</b><br>claims ${fmt(r.claims)}`); svg.appendChild(bc);
    const bd=bar(CX0,y+24,cx(r.denials)-CX0,18,"var(--denials)");   // 2px surface gap
    hover(bd,`<b>${r.label}</b><br>denials ${fmt(r.denials)}`); svg.appendChild(bd);

    svg.appendChild(txt(cx(r.claims)+6,y+17,fmt(r.claims),{fill:"var(--text-secondary)","font-size":10.5}));
    svg.appendChild(txt(cx(r.denials)+6,y+37,fmt(r.denials),{fill:"var(--text-secondary)","font-size":10.5}));

    const dot=el("circle",{cx:rx(r.ratio),cy:y+21,r:6,fill:"var(--claims)",
      stroke:"var(--surface-1)","stroke-width":2});
    hover(dot,`<b>${r.label}</b><br>ratio ${r.ratio.toFixed(3)} — ${r.note}`); svg.appendChild(dot);
    svg.appendChild(txt(rx(r.ratio),y+39,r.ratio.toFixed(3),
      {fill:"var(--text-secondary)","font-size":10.5,"text-anchor":"middle"}));
  });
  document.getElementById("f1").appendChild(svg);

  document.getElementById("t1").innerHTML=
    "<table><tr><th>scenario</th><th>claims</th><th>denials</th><th>ratio</th><th>basis</th></tr>"+
    RUNS.map(r=>`<tr><td>${r.label}</td><td>${fmt(r.claims)}</td><td>${fmt(r.denials)}</td>`+
      `<td>${r.ratio.toFixed(3)}</td><td>${r.kind==="estimate"?"pattern estimate":"recomputation"}</td></tr>`).join("")+
    "</table>";
})();

// ---------------------------------------------------- figure 2 · causes
(function(){
  const W=900, ROW=54, TOP=40, LAB=200, ZX=470, SPAN=330,
        H=TOP+CAUSES.length*ROW+38;
  const dmax=0.07;
  const dx=v=>ZX+(v/dmax)*SPAN*0.62;
  const svg=el("svg",{width:"100%",viewBox:`0 0 ${W} ${H}`,role:"img",
    "aria-label":"Change in the claims-to-denials ratio caused by each defect"});

  svg.appendChild(txt(ZX,20,"change in ratio",{fill:"var(--text-muted)","font-size":11,"text-anchor":"middle"}));
  [-0.02,0,0.02,0.04,0.06].forEach(v=>{
    svg.appendChild(el("line",{x1:dx(v),y1:TOP-8,x2:dx(v),y2:TOP+CAUSES.length*ROW-8,
      stroke:v===0?"var(--axis)":"var(--grid)","stroke-width":1}));
    svg.appendChild(txt(dx(v),TOP+CAUSES.length*ROW+12,(v>0?"+":"")+v.toFixed(2),
      {fill:"var(--text-muted)","font-size":10.5,"text-anchor":"middle"}));
  });

  CAUSES.forEach((c,i)=>{
    const y=TOP+i*ROW;
    svg.appendChild(txt(0,y+15,`${c.id} · ${c.label}`,{fill:"var(--text-primary)","font-size":12.5}));
    const words=c.detail.split(" "); let line="",ln=0;
    words.forEach(w=>{ if((line+w).length>62){ svg.appendChild(txt(0,y+29+ln*12,line,
        {fill:"var(--text-muted)","font-size":10})); line=w+" "; ln++; } else line+=w+" "; });
    svg.appendChild(txt(0,y+29+ln*12,line,{fill:"var(--text-muted)","font-size":10}));

    if(Math.abs(c.delta)<0.0005){
      svg.appendChild(el("line",{x1:ZX-4,y1:y+6,x2:ZX+4,y2:y+6,stroke:"var(--axis)","stroke-width":2}));
      svg.appendChild(txt(ZX+12,y+10,"no effect measured",{fill:"var(--text-muted)","font-size":10.5}));
    } else {
      const pos=c.delta>0, w=Math.abs(dx(c.delta)-ZX), col=pos?"var(--up)":"var(--down)";
      const b=pos?bar(ZX,y-2,w,17,col):barL(ZX,y-2,w,17,col);
      hover(b,`<b>${c.id} · ${c.label}</b><br>ratio ${(c.delta>0?"+":"")}${c.delta.toFixed(3)}`+
        `<br>${c.measured?"recomputation":"pattern estimate — over-counts"}`);
      svg.appendChild(b);
      svg.appendChild(txt(pos?dx(c.delta)+7:dx(c.delta)-7,y+11,
        (pos?"+":"")+c.delta.toFixed(3)+(c.measured?"":"  (upper bound)"),
        {fill:"var(--text-secondary)","font-size":10.5,"text-anchor":pos?"start":"end"}));
    }
  });
  document.getElementById("f2").appendChild(svg);

  document.getElementById("t2").innerHTML=
    "<table><tr><th>defect</th><th>change in ratio</th><th>basis</th></tr>"+
    CAUSES.map(c=>`<tr><td>${c.id} · ${c.label}</td><td>${(c.delta>0?"+":"")}${c.delta.toFixed(3)}</td>`+
      `<td>${c.measured?"recomputation":"pattern estimate (over-counts)"}</td></tr>`).join("")+
    "</table>";
})();
</script>
</div>
"""

display(HTML(FIGURES))
