# SPDX-License-Identifier: LicenseRef-FieldDock-NC-1.0
# -*- coding: utf-8 -*-
from pathlib import Path
import json,math,html
R=Path(__file__).resolve().parents[1]/'K'
S=json.loads((R/'preview/scene.json').read_text(encoding='utf-8'))
T=r'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>FieldDock 结构审查</title><style>
*{box-sizing:border-box}body{margin:0;background:#eef1f5;color:#192434;font:14px -apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei",sans-serif}header{height:84px;padding:20px 28px;background:#fff;border-bottom:1px solid #dce1e7;display:flex;justify-content:space-between;align-items:center}h1{font-size:23px;margin:0 0 6px}small{color:#68788c}.badge{background:#fff0cd;color:#73521a;padding:9px 14px;border-radius:18px}main{display:grid;grid-template-columns:1fr 310px;height:calc(100vh - 84px)}section{position:relative;min-width:0}canvas{width:100%;height:100%;display:block;touch-action:none}.toolbar{position:absolute;top:18px;left:18px;display:flex;gap:7px}button{border:1px solid #d4dce5;border-radius:8px;background:white;padding:8px 12px;color:#29384c;cursor:pointer}button:hover{background:#e6edf5}aside{overflow:auto;background:#fff;border-left:1px solid #dce1e7;padding:22px}h2{font-size:16px;margin:22px 0 12px}label{display:block;margin:12px 0;cursor:pointer}input[type=range]{width:100%}.help{position:absolute;bottom:18px;left:20px;color:#64758b;background:#ffffffdc;padding:8px 12px;border-radius:8px}.legend{font-size:12px;line-height:1.8;color:#586b82}.list{max-height:39vh;overflow:auto}.item{font-size:12px;display:flex;gap:8px;margin:8px 0;align-items:center}.swatch{width:9px;height:9px;border-radius:2px;flex-shrink:0}.notice{background:#fff6e6;padding:12px;line-height:1.65;font-size:12px;border-radius:8px}@media(max-width:800px){main{grid-template-columns:1fr;grid-template-rows:65vh auto;height:auto}aside{border:0}.badge{font-size:11px}header{padding:16px}h1{font-size:19px}}
</style><header><div><h1>FieldDock · 紧凑装配 K</h1><small>实际板框 + 元件包络 · 单位 mm · iPhone 17 Pro Max</small></div><span class="badge">工程审查稿 / 未发布制造</span></header><main><section><canvas id="cv"></canvas><div class="toolbar"><button id="iso">立体</button><button id="top">俯视</button><button id="side">侧视</button><button id="reset">复位</button></div><div class="help">拖拽旋转 · 滚轮缩放 · 右侧可隐藏外壳、展开装配</div></section><aside><b>装配层次</b><label>展开程度 <span id="ev">55%</span></label><input id="explode" type="range" min="0" max="100" value="55"><label><input id="shell" type="checkbox" checked> 显示上下壳与窗口</label><label><input id="phone" type="checkbox" checked> 显示参考几何</label><label><input id="res" type="checkbox" checked> 显示预留板和装配包络</label><label><input id="probes" type="checkbox"> 显示探头预留（本模型无）</label><label><input id="keep" type="checkbox"> 显示简化避让提示区域</label><div class="notice">板框、孔位和元件 XY 已与当前 PCB 对齐。元件高度为保守包络；线圈为绕线空间。外壳公差、光学窗口、按键保持与手机固定仍须验证。</div><h2>可见零件</h2><div id="list" class="list"></div><h2>审查范围</h2><div class="legend">可检查装配层次、体积和接口方向。尺寸请以 STEP 和二维图为准。预览不构成天线、载荷、散热、线缆弯折或 Apple 兼容性验证。</div></aside></main><script>
const scene=__SCENE__;
const cv=document.querySelector('#cv'),ctx=cv.getContext('2d');let az=-.5,el=.75,zoom=1,drag=null,scheduled=false;
const ids=['explode','shell','phone','res','probes','keep'];const controls=Object.fromEntries(ids.map(x=>[x,document.getElementById(x)]));
function visible(p){if(p.category==='probe_reserved')return controls.probes.checked;if(p.category==='keepout')return controls.keep.checked;if(p.category==='reference')return controls.phone.checked;if(['M01_base','M02_lid','M03_ir_window'].includes(p.id)&&!controls.shell.checked)return false;if(['pcb_reserved','component_envelope','connector_envelope'].includes(p.category)&&!controls.res.checked)return false;return true}
function rot(p){let u=p[0]*Math.cos(az)-p[1]*Math.sin(az),v=p[0]*Math.sin(az)+p[1]*Math.cos(az);return [u,v*Math.cos(el)+p[2]*Math.sin(el),-v*Math.sin(el)+p[2]*Math.cos(el)]}
function request(){if(!scheduled){scheduled=true;requestAnimationFrame(draw)}}
function draw(){scheduled=false;const W=cv.clientWidth,H=cv.clientHeight,dpr=Math.min(devicePixelRatio||1,2);cv.width=W*dpr;cv.height=H*dpr;ctx.setTransform(dpr,0,0,dpr,0,0);ctx.fillStyle='#eef1f5';ctx.fillRect(0,0,W,H);let parts=scene.filter(visible),e=+controls.explode.value/100;let tr=[];let bounds=[Infinity,Infinity,-Infinity,-Infinity];for(let p of parts){for(let t of p.mesh){let r=t.map(a=>rot([a[0],a[1],a[2]+p.explode*e]));for(let a of r){bounds[0]=Math.min(bounds[0],a[0]);bounds[1]=Math.min(bounds[1],a[1]);bounds[2]=Math.max(bounds[2],a[0]);bounds[3]=Math.max(bounds[3],a[1])}let normal=(r[1][0]-r[0][0])*(r[2][1]-r[0][1])-(r[1][1]-r[0][1])*(r[2][0]-r[0][0]);if(normal<0)continue;tr.push({r,p,z:(r[0][2]+r[1][2]+r[2][2])/3})}}
let scale=Math.min((W-90)/(bounds[2]-bounds[0]),(H-90)/(bounds[3]-bounds[1]))*zoom,cx=(bounds[0]+bounds[2])/2,cy=(bounds[1]+bounds[3])/2;tr.sort((a,b)=>a.z-b.z);
for(let {r,p} of tr){let a=r[0],b=r[1],c=r[2],u=b.map((x,i)=>x-a[i]),v=c.map((x,i)=>x-a[i]),n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]],mag=Math.hypot(...n)||1,light=.6+.4*Math.abs((n[0]*.2+n[1]*.5+n[2]*.84)/mag),hex=p.color.slice(1),rgb=[0,2,4].map(i=>Math.min(255,Math.round(parseInt(hex.slice(i,i+2),16)*light)));ctx.fillStyle=`rgb(${rgb})`;ctx.globalAlpha=p.category==='keepout'?.23:1;ctx.beginPath();r.forEach((a,i)=>ctx[i?'lineTo':'moveTo'](W/2+(a[0]-cx)*scale,H/2-(a[1]-cy)*scale));ctx.closePath();ctx.fill();ctx.strokeStyle=ctx.fillStyle;ctx.lineWidth=.8;ctx.stroke()}ctx.globalAlpha=1;document.querySelector('#ev').textContent=Math.round(e*100)+'%';document.querySelector('#list').innerHTML=parts.filter(p=>!p.id.startsWith('R_PWR')).map(p=>`<div class="item"><i class="swatch" style="background:${p.color}"></i>${p.title}</div>`).join('')}
for(let c of Object.values(controls))c.oninput=request;
cv.onpointerdown=e=>{drag=[e.clientX,e.clientY];cv.setPointerCapture(e.pointerId)};cv.onpointerup=()=>drag=null;cv.onpointermove=e=>{if(!drag)return;az+=(e.clientX-drag[0])*.008;el=Math.max(-1.5,Math.min(1.5,el+(e.clientY-drag[1])*.008));drag=[e.clientX,e.clientY];request()};cv.onwheel=e=>{e.preventDefault();zoom=Math.max(.5,Math.min(3,zoom*Math.exp(-e.deltaY*.001)));request()};document.querySelector('#iso').onclick=()=>{az=-.5;el=.75;request()};document.querySelector('#top').onclick=()=>{az=0;el=Math.PI/2;request()};document.querySelector('#side').onclick=()=>{az=0;el=0;request()};document.querySelector('#reset').onclick=()=>{az=-.5;el=.75;zoom=1;controls.explode.value=55;controls.probes.checked=false;controls.keep.checked=false;request()};new ResizeObserver(request).observe(cv);request();
</script></html>'''
(R/'preview/assembly-viewer.html').write_text(T.replace('__SCENE__',json.dumps(S,ensure_ascii=False,separators=(',',':'))),encoding='utf-8')
# Standalone shaded SVG uses the same CAD tessellation as the interactive preview.
az=-.5;el=.75;faces=[]
def rot(p):
 x,y,z=p;u=x*math.cos(az)-y*math.sin(az);v=x*math.sin(az)+y*math.cos(az)
 return [u,v*math.cos(el)+z*math.sin(el),-v*math.sin(el)+z*math.cos(el)]
for p in S:
 if p['category'] in ['probe_reserved','keepout']:continue
 for t in p['mesh']:
  r=[rot([a[0],a[1],a[2]+p['explode']*.55]) for a in t]
  a,b,c=r
  n=(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
  if n<0:continue
  u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)];nn=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
  mag=math.sqrt(sum(n*n for n in nn)) or 1;light=.6+.4*abs(sum(x*y for x,y in zip(nn,[.2,.5,.84]))/mag)
  col='#'+''.join(f'{min(255,round(int(p["color"][i:i+2],16)*light)):02x}' for i in [1,3,5])
  faces.append((sum(a[2] for a in r)/3,r,col))
xs=[v[0] for _,r,_ in faces for v in r];ys=[v[1] for _,r,_ in faces for v in r]
cx=(min(xs)+max(xs))/2;cy=(min(ys)+max(ys))/2;sc=min(950/(max(xs)-min(xs)),640/(max(ys)-min(ys)))
v=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="850" viewBox="0 0 1200 850">','<rect width="1200" height="850" fill="#eef1f5"/>','<g font-family="Microsoft YaHei,Segoe UI,sans-serif"><text x="50" y="50" font-size="28" fill="#233349">FieldDock / 100 × 46 × 18 mm 装配研究</text><text x="50" y="80" font-size="15" fill="#68788c">可拆工程扩展坞 · iPhone 17 Pro Max · 无电池 / 双 USB-C</text></g>']
for _,r,col in sorted(faces,key=lambda a:a[0]):
 v.append('<polygon points="'+' '.join(f'{600+(a[0]-cx)*sc:.2f},{440-(a[1]-cy)*sc:.2f}' for a in r)+'" fill="'+col+'" stroke="'+col+'" stroke-width="0.8"/>')
v.append('<g font-family="Microsoft YaHei,Segoe UI,sans-serif" fill="#4b5d75"><text x="50" y="795" font-size="15">94 × 40 × 1.6 mm 主板 · 395 个贴装元件包络 · 无电池 / 双 USB-C</text><text x="50" y="823" font-size="13">工程审查稿；模块包络、夹持结构与制造细节尚未冻结。装配展开图不表示使用姿态。</text></g></svg>')
(R/'preview/assembly-exploded.svg').write_text(''.join(v),encoding='utf-8')
