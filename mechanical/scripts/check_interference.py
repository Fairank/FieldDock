# SPDX-License-Identifier: LicenseRef-FieldDock-NC-1.0
from pathlib import Path
import sys,json,itertools
M=Path(__file__).resolve().parents[1]/'K';import gmsh
d=json.loads((M/'checks/assembly-K.json').read_text());gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.model.add('interference');o=gmsh.model.occ
parts={r['id']:o.importShapes(str(M/'parts'/(r['id']+'.step'))) for r in d['parts']};o.synchronize();bad=[];allowed=[];checked=0
for a,b in itertools.combinations(d['parts'],2):
 ba,bb=a['bbox_mm'],b['bbox_mm']
 if any(min(ba[i+3],bb[i+3])-max(ba[i],bb[i])<.0005 for i in range(3)):continue
 checked+=1;ca=o.copy(parts[a['id']]);cb=o.copy(parts[b['id']]);out,_=o.intersect(ca,cb);vol=sum(o.getMass(dim,tag) for dim,tag in out if dim==3)
 if out:o.remove(out,recursive=True)
 if vol>.0001:
  rec=dict(a=a['id'],b=b['id'],volume_mm3=round(vol,6))
  if (a['id']=='M01_base' and b['id'].startswith('S_M2_')):rec['reason']='Thread-forming screw nominal cylinder overlaps pilot hole material by design';allowed.append(rec)
  else:bad.append(rec)
report=dict(status='PASS_ENVELOPE_INTERFERENCE_ONLY' if not bad else 'FAIL',tested_pairs=checked,unintended_overlaps=bad,intended_overlaps=allowed,scope='CAD solids and conservative placed component envelopes; no tolerances, force, cable bend or antenna performance qualification',manufacturing_release=False)
(M/'checks/interference-K.json').write_text(json.dumps(report,indent=2),encoding='utf-8');gmsh.finalize();print(json.dumps(report,indent=2))
