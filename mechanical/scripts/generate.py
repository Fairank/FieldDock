# SPDX-License-Identifier: LicenseRef-FieldDock-NC-1.0
# -*- coding: utf-8 -*-
"""Compact FieldDock arrangement, mm. Geometry prototype, not manufacturing release.
Regenerate with Python + Gmsh/OpenCASCADE; never launches KiCad.
"""
from pathlib import Path
import sys,json,math,struct,collections,csv,itertools
import argparse
args=argparse.ArgumentParser()
args.add_argument('--placement',type=Path)
opt=args.parse_args()
O=Path(__file__).resolve().parents[2]
ROOT=O/'mechanical/K';ROOT.mkdir(parents=True,exist_ok=True)
import gmsh
P={"length":100.0,"width":46.0,"height":18.0,"radius":6.0,"wall":1.6,
   "lid_z":16.0,"pcb_width":40.0,"pcb_length":94.0,"pcb_z":5.7,"pcb_thickness":1.6,
   "coil_center_y":10.0,"port_spacing":25.0,"mount_positions":[[-17,-37],[17,-37],[-17,43],[17,43]],
   "status":"PLACEMENT_ENVELOPES_NOT_QUALIFIED_FOR_PRODUCTION"}
f=ROOT/'parameters.json'
if f.exists():P.update(json.loads(f.read_text(encoding='utf-8-sig')))
f.write_text(json.dumps(P,indent=2),encoding='utf-8')
for d in ['parts','preview','checks','layout']:(ROOT/d).mkdir(exist_ok=True)
gmsh.initialize();gmsh.option.setNumber('General.Terminal',0)
gmsh.option.setNumber('Geometry.OCCBoundsUseStl',0)
o=gmsh.model.occ;scene=[];reports=[]
def box(w,h,d,x=0,y=0,z=0):return o.addBox(x-w/2,y-h/2,z,w,h,d)
def cyl(r,h,x=0,y=0,z=0):return o.addCylinder(x,y,z,0,0,h,r)
def fuse(tags):
 if len(tags)==1:return tags[0]
 out,_=o.fuse([(3,tags[0])],[(3,t) for t in tags[1:]])
 assert len(out)==1, out
 return out[0][1]
def cut(a,bs):
 out,_=o.cut([(3,a)],[(3,b) for b in bs])
 assert len(out)==1,out
 return out[0][1]
def rr(w,h,d,r,x=0,y=0,z=0):
 return fuse([box(w-2*r,h,d,x,y,z),box(w,h-2*r,d,x,y,z)]+[cyl(r,d,x+sx*(w/2-r),y+sy*(h/2-r),z) for sx in [-1,1] for sy in [-1,1]])
def housing(w,h,d,r,wall):return cut(rr(w,h,d,r),[rr(w-2*wall,h-2*wall,d,r-wall,z=wall)])
def plate_holes(w,h,d,z=0):
 return cut(rr(w,h,d,3,z=z),[cyl(1.5,d+2,x,y,z-1) for x in [-w/2+4,w/2-4] for y in [-h/2+4,h/2-4]])

def part(name,title,make,color,category='fabricated',offset=(0,0,0),explode=0,notes=''):
 gmsh.model.add(name)
 gmsh.option.setNumber('Mesh.MeshSizeFromCurvature',36)
 gmsh.option.setNumber('Mesh.MinimumCirclePoints',36)
 gmsh.option.setNumber('Mesh.MeshSizeMin',0.15)
 gmsh.option.setNumber('Mesh.MeshSizeMax',4)
 tags=make(); tags=[tags] if isinstance(tags,int) else tags
 if any(offset):o.translate([(3,t) for t in tags],*offset)
 o.synchronize()
 for t in tags:gmsh.model.setEntityName(3,t,name)
 gmsh.write(str(ROOT/'parts'/f'{name}.step'))
 gmsh.model.mesh.generate(2)
 node_tags,xyz,_=gmsh.model.mesh.getNodes()
 nodes={int(n):[float(v) for v in xyz[i*3:i*3+3]] for i,n in enumerate(node_tags)}
 # Gmsh already orients these surface mesh elements for the volume. Do not apply boundary signs twice.
 tris=[]
 for t in tags:
  for dim,signed in gmsh.model.getBoundary([(3,t)],combined=False,oriented=True):
   if dim!=2:continue
   ty,el,conn=gmsh.model.mesh.getElements(2,abs(signed))
   for typ,ns in zip(ty,conn):
    assert int(typ)==2,('Expected linear triangle',typ)
    for i in range(0,len(ns),3):
     tri=[nodes[int(n)] for n in ns[i:i+3]]
     tris.append(tri)
 edges=collections.Counter()
 for tri in tris:
  pts=[tuple(round(v,6) for v in p) for p in tri]
  for i in range(3):edges[tuple(sorted((pts[i],pts[(i+1)%3])))]+=1
 bad=sum(n!=2 for n in edges.values())
 # Binary STL in assembly coordinates, with explicit mm declaration in README.
 with (ROOT/'parts'/f'{name}.stl').open('wb') as f:
  f.write(('FieldDock mm '+name).encode().ljust(80,b'\0'));f.write(struct.pack('<I',len(tris)))
  for a,b,c in tris:
   u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)]
   n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
   l=math.sqrt(sum(k*k for k in n)) or 1
   f.write(struct.pack('<12fH',*[k/l for k in n],*a,*b,*c,0))
 bounds=[gmsh.model.getBoundingBox(3,t) for t in tags]
 bb=[min(b[i] for b in bounds) for i in range(3)]+[max(b[i] for b in bounds) for i in range(3,6)]
 volumes=[o.getMass(3,t) for t in tags]
 mesh_volume=sum((a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6 for a,b,c in tris)
 mesh_volume_error=abs(mesh_volume-sum(volumes))/sum(volumes)
 assert mesh_volume>0 and mesh_volume_error<0.025,(name,'mesh orientation/volume',mesh_volume,sum(volumes))
 assert all(v>0 for v in volumes) and bad==0,(name,volumes,bad)
 rec=dict(id=name,title=title,color=color,category=category,offset=offset,explode=explode,notes=notes,
          bbox_mm=[round(v,4) for v in bb],volume_mm3=sum(volumes),solids=len(tags),triangles=len(tris),nonmanifold_edges=bad,mesh_signed_volume_mm3=mesh_volume,mesh_volume_relative_error=mesh_volume_error)
 reports.append(rec)
 # A coarser tessellation is used only by the lightweight preview, never the STL.
 gmsh.model.mesh.clear()
 gmsh.option.setNumber('Mesh.MeshSizeFromCurvature',12)
 gmsh.option.setNumber('Mesh.MinimumCirclePoints',12)
 gmsh.option.setNumber('Mesh.MeshSizeMin',0.8)
 gmsh.option.setNumber('Mesh.MeshSizeMax',7)
 gmsh.model.mesh.generate(2)
 ni,nx,_=gmsh.model.mesh.getNodes()
 nd={int(n):[float(v) for v in nx[i*3:i*3+3]] for i,n in enumerate(ni)}
 display=[]
 for t in tags:
  for dim,face in gmsh.model.getBoundary([(3,t)],combined=False,oriented=True):
   if dim!=2:continue
   ty,ee,con=gmsh.model.mesh.getElements(2,abs(face))
   for typ,ns in zip(ty,con):
    assert int(typ)==2
    for i in range(0,len(ns),3):display.append([nd[int(n)] for n in ns[i:i+3]])
 rec=dict(rec,display_triangles=len(display),mesh=[[[round(v,3) for v in p] for p in t] for t in display])
 scene.append(rec)
 print(name,len(tris),'triangles',flush=True)
 return rec



S={s['ref']:s for s in json.loads((O/'cad/design.json').read_text()) if s['footprint']};PADS=json.loads((O/'cad/footprint-geometry.json').read_text());PLACE=json.loads((opt.placement or O/'placement-full.json').read_text());H=json.loads((O/'cad/mounting-hole-locations.json').read_text())
mounts=[(x-100,100-y) for x,y in H['holes']];zpcb=5.7;thick=1.6;ztop=zpcb+thick
P.update(pcb_z=zpcb,pcb_thickness=thick,mount_positions=mounts,coil_center_y=24.5,coil_width=30,coil_length=34,body_dimensions=[46,100,18],manufacturing_release=False)
(ROOT/'parameters.json').write_text(json.dumps(P,indent=2),encoding='utf-8')
def body_height(r,s):
 if r=='U1':return 1.382
 if r=='L201':return 4
 if r in ['J101','J102']:return 3.3
 if r=='J301':return 1.83
 if r=='J700':return 8.5
 if r=='J730':return 3.0
 if r in ['SW1','SW2','SW3','SW5']:return 3.5
 if r=='SW4':return 4.0
 if r=='U712':return 3.5
 if r=='BZ740':return 1.9
 if r.startswith(('J','TP')):return .1
 if r in ['D710','D711','D712']:return 1.6
 if '1206' in s['footprint']:return 2
 if '0805' in s['footprint']:return 1.25
 if '0603' in s['footprint']:return .9
 if '0402' in s['footprint']:return .65
 if '0201' in s['footprint']:return .4
 if 'SOT-23' in s['footprint']:return 1.45
 return 1.25
body=[]
for r,p in PLACE.items():
 s=S[r]
 if r.startswith('TP') or r in ['J500','J600','J710','J740'] or s.get('dnp'):continue
 a,b,c,d=p['bounds'];height=body_height(r,s)
 rec=dict(ref=r,side=p['side'],x=(a+c)/2-100,y=100-(b+d)/2,w=c-a,h=d-b,height=height,z=ztop if p['side']=='F' else zpcb-height,source='PCB courtyard XY + conservative height; exact manufacturer body/actuator model pending',bbox=[a-100,100-d,ztop if p['side']=='F' else zpcb-height,c-100,100-b,ztop+height if p['side']=='F' else zpcb])
 body.append(rec)
(ROOT/'component-envelopes.json').write_text(json.dumps(body,indent=2),encoding='utf-8')
# Shell is a fit-study geometry. Actuator openings provide tool access; final buttons/latches are not qualified.
def base():
 a=housing(46,100,16,6,1.6);a=fuse([a]+[cyl(1.7,zpcb-1.6,x,y,1.6) for x,y in mounts])
 holes=[cyl(.8,zpcb,x,y,.7) for x,y in mounts]
 holes += [box(11.2,8,4.5,x,-49,ztop-.4) for x in [-12.5,12.5]]
 holes += [box(8,16.5,2.6,-21,100-115.9,ztop-.2)]
 holes += [box(8,15.8,4,21,100-122.7,zpcb-3.5)]
 holes += [cyl(2.1,3,PLACE[r]['x']-100,100-PLACE[r]['y'],-.2) for r in ['SW1','SW5']]
 # Coax test-antenna passage, and IR side window. Optical receiver orientation still needs exact supplier model.
 holes += [box(6,5,3,22,22,9),box(8,9,4,22,13,ztop-.1)]
 holes += [box(18,6,4,0,49,ztop-.1)]
 return cut(a,holes)
part('M01_base','100 x 46 lower shell / fit prototype',base,'#5e7285',notes='1.6 mm walls; M2 thread-forming screw pilot 1.6 mm. Port cutouts track current PCB; shrink and tolerances not qualified.')
def lid():
 a=rr(46,100,2,6,z=16);a=fuse([a]+[cyl(1.7,16-ztop,x,y,ztop) for x,y in mounts])
 holes=[cyl(1.2,12,x,y,ztop-.1) for x,y in mounts]+[o.addCone(x,y,16.7,0,0,1.4,1.2,2.2) for x,y in mounts]
 holes += [box(12.5,22.2,3,13.4,100-104.6,15.5)]
 holes += [cyl(2.15,14,PLACE[r]['x']-100,100-PLACE[r]['y'],4) for r in ['SW2','SW3']]
 holes += [box(5,9,14,2.8,100-119.5,4)]
 return cut(a,holes)
part('M02_lid','Outward non-metal lid / fit prototype',lid,'#dbe2e8',explode=35,notes='GPIO access, confirmation/stop plunger apertures and hardware slide-switch access. No ingress/impact rating.')
part('E01_pcb','Actual 94 x 40 x 1.6 PCB datum and mounting holes',lambda:cut(rr(40,94,1.6,2,z=zpcb),[cyl(1.2,3,x,y,zpcb-.5) for x,y in mounts]),'#237b66','pcb_geometry',explode=8,notes='Actual board outline and current four 2.4 mm holes; copper not included in mechanical STEP.')
for side in ['F','B']:
 def blocks(side=side):return [box(v['w'],v['h'],v['height'],v['x'],v['y'],v['z']) for v in body if v['side']==side]
 part('E_SMT_'+side,'Current '+side+'-side component envelopes',blocks,'#384b5b' if side=='F' else '#7f99a6','component_envelope',explode=8,notes='Every populated reference tied to placement; XY uses conservative courtyard. Not exact supplier geometry.')
# Coil area shrunk to avoid mounting pillar H1 and GPIO access. Antenna performance is still a measured gate.
def carrier():
 a=box(32.5,36.5,.6,1,24.5,13.7)
 holes=[cyl(2.2,2,x,y,13) for x,y in mounts]+[cyl(2.6,2,.6,14.5,13)]
 return cut(a,holes)
part('M03_coil_carrier','Dual-coil fit carrier',carrier,'#abb9c2',explode=21,notes='30 x 34 NFC and 23 x 21 LF winding envelopes; nominal inductances not guaranteed.')
part('E_FERRITE','Ferrite material reservation',lambda:cut(box(32,36,.5,1,24.5,13.2),[cyl(2.3,2,x,y,13) for x,y in mounts]+[cyl(2.6,2,.6,14.5,13)]),'#4e5963','material_reserved',explode=21,notes='Material permeability/loss must suit 125 kHz and 13.56 MHz; composition and adhesive not selected.')
part('E_NFC_COIL','NFC winding envelope',lambda:cut(rr(30,34,.4,3,1,24.5,14.4),[rr(25,29,1,1.5,1,24.5,14.1)]),'#ca9b58','antenna_reserved',explode=23,notes='Winding envelope only. Start with removable winding; tune installed coil and matching using VNA/LCR.')
part('E_LF_COIL','LF winding envelope',lambda:cut(rr(23,21,1.1,3,1,27.5,14.4),[rr(18,16,2,1.5,1,27.5,14)]),'#b77641','antenna_reserved',explode=23,notes='500 uH is circuit target; turns and Q require winding measurement.')
for i,(x,y) in enumerate(mounts,1):
 part('S_M2_'+str(i),'M2 x 16 screw nominal envelope',lambda x=x,y=y:fuse([cyl(1,14.8,x,y,2),o.addCone(x,y,16.8,0,0,1.2,1,2)]),'#9caab4','fastener_envelope',explode=42,notes='Thread geometry omitted; verify pilot, screw length and pull-out in chosen printing process.')
for r in ['SW2','SW3']:
 x=PLACE[r]['x']-100;y=100-PLACE[r]['y'];bottom=ztop+3.5+.2
 part('M_'+r+'_plunger',r+' button plunger fit',lambda x=x,y=y,bottom=bottom:cyl(1.9,17.8-bottom,x,y,bottom),'#94aba7',explode=35,notes='0.2 mm initial actuator gap; retained button cap and stroke require switch drawing and fit test.')
# Small detachable mounting plate is additional thickness, with replaceable case adhesive (no built-in magnets).
part('M04_mount_plate','Phone-case mounting plate fit',lambda:rr(42,65,1.2,3,y=-6,z=-1.6),'#8799a8','mount_prototype',explode=-8,notes='Mount geometry prototype; latch/adhesive/camera clearance and iPhone case dimensions not frozen.')
# Assembly CAD contains each distinct solid; reference envelope status is preserved in manifest.
gmsh.model.add('FieldDock_assembly_K')
for rec in reports:o.importShapes(str(ROOT/'parts'/(rec['id']+'.step')))
o.synchronize();gmsh.write(str(ROOT/'FieldDock-assembly-K.step'))
report=dict(board_mm=[94,40,1.6],case_mm=[100,46,18],pcb_bottom_z=zpcb,pcb_top_z=ztop,body_reference_count=len(body),min_bottom_component_floor_clearance=min(v['z']-1.6 for v in body if v['side']=='B'),max_front_component_top=max(v['z']+v['height'] for v in body if v['side']=='F'),parts=reports,manufacturing_release=False,limits=['Component heights are envelopes, exact supplier STEP and mounting force not checked.','Coils are winding spaces, not electrically complete antennas.','No final Sub-GHz internal antenna; coax test passage provided.','Phone retention, optics and plunger retention remain unfinished.'])
(ROOT/'checks/assembly-K.json').write_text(json.dumps(report,indent=2),encoding='utf-8');(ROOT/'preview/scene.json').write_text(json.dumps(scene),encoding='utf-8');gmsh.finalize();print('Mechanical CAD generated:',len(reports),'parts;',len(body),'placed component envelopes')
