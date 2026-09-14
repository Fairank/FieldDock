# SPDX-License-Identifier: LicenseRef-FieldDock-NC-1.0
"""Verify published evidence and file hashes without launching KiCad.

python tools/verify_artifacts.py           checks integrity and reported status
python tools/verify_artifacts.py --release additionally requires fabrication release
"""
from pathlib import Path
import argparse,collections,csv,hashlib,json,sys
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--release',action='store_true');args=p.parse_args()
errors=[]
def read(name):return json.loads((R/name).read_text(encoding='utf-8'))
def check(ok,message):
 if not ok:errors.append(message)
def safe_path(name):
 q=(R/name).resolve()
 if not q.is_relative_to(R):raise ValueError('Path leaves repository: '+name)
 return q
status=read('release-status.json');manifest=read('checks/artifact-manifest.json')
for name,digest in manifest['sha256'].items():
 q=safe_path(name);check(q.is_file(),'Missing: '+name)
 if q.is_file():check(hashlib.sha256(q.read_bytes()).hexdigest()==digest,'Hash mismatch: '+name)
drc=read('checks/drc.json');counts=dict(collections.Counter(v['type'] for v in drc['violations']))
check(status['drc']['unconnected']==len(drc['unconnected_items']),'DRC unconnected count does not match report')
check(status['drc']['violations']==counts,'DRC violation counts do not match report')
erc=read('checks/erc.json');erc_violations=[v for s in erc['sheets'] for v in s['violations']]
check(len(erc_violations)==status['erc']['violations'],'ERC count does not match report')
net=read('checks/netlist-consistency.json');check(net['status']=='PASS' and not net['mismatches'] and not net['unexpected_connected_pins'],'Netlist mapping failed')
with (R/'licensing/library-inventory.csv').open(encoding='utf-8-sig',newline='') as f:
 for item in csv.DictReader(f):
  q=safe_path(item['path']);check(q.is_file(),'Missing licensed library: '+item['path'])
  if q.is_file():check(hashlib.sha256(q.read_bytes()).hexdigest()==item['sha256'],'Library provenance hash mismatch: '+item['path'])
geometry=read('checks/manufacturing-export-K.json')
final_net=read('checks/final-pad-net-consistency-K.json')
board_hash=hashlib.sha256((R/'cad/FD-MAIN-01.kicad_pcb').read_bytes()).hexdigest()
check(status['pcb_sha256']==board_hash,'Status PCB hash mismatch')
check(geometry['native_board_sha256']==board_hash,'Manufacturing check belongs to another PCB')
check(final_net['native_board_sha256']==board_hash,'Final pad mapping belongs to another PCB')
check(geometry['status']=='PASS' and not geometry['errors'],'Manufacturing export geometry failed')
check(final_net['status']=='PASS' and not final_net['errors'],'Final PCB-to-schematic pad mapping failed')
check(status['release_scope']=='bare_pcb_engineering_prototype_files','Unsupported release scope')
released=status['manufacturing_release']
if released or args.release:
 check(released,'Fabrication release has not been granted')
 check(not drc['unconnected_items'] and not drc['violations'],'PCB DRC is not clean')
 check(not erc_violations,'Schematic ERC is not clean')
 files=status.get('manufacturing_files',[]);check(bool(files),'No checked manufacturing file set')
 for name in files:check(name in manifest['sha256'],'Manufacturing file not covered by checksum: '+name)
 check(status.get('manufacturing_file_geometry_checked') is True,'Manufacturing export geometry not checked')
for error in errors:print('FAIL:',error)
if errors:sys.exit(1)
print('PASS: published files, report counts, netlist mapping and library provenance agree.')
print('Bare-PCB engineering prototype file release:',released)
print('Assembled product release:',status['assembly_release'],'; hardware tested:',status['hardware_tested'])
print('This check does not run KiCad, simulate the circuit or test physical hardware.')
