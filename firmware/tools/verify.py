from pathlib import Path
import subprocess,sys,os,json,time
F=Path(__file__).resolve().parents[1];B=F/'build';B.mkdir(exist_ok=True)
zig=Path(sys.argv[1]);env=os.environ.copy();env['ZIG_GLOBAL_CACHE_DIR']=str(B/'zig-global');env['ZIG_LOCAL_CACHE_DIR']=str(B/'zig-local');env['TEMP']=str(B);env['TMP']=str(B)
common=[str(zig),'cc','-std=c99','-Wall','-Wextra','-Werror','-pedantic','-I',str(F/'include')]
src=[F/'src/fd_cc1101.c',F/'src/fd_power.c'];records=[]
def run(cmd):
 r=subprocess.run([str(x) for x in cmd],cwd=F,env=env,text=True,capture_output=True,timeout=180)
 records.append({'command':[str(x) for x in cmd],'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
 if r.returncode:raise RuntimeError(r.stderr or r.stdout)
 print((r.stdout or 'PASS: '+Path(str(cmd[-1])).name).strip(),flush=True)
try:
 run(common+src+[F/'tests/test_core.c','-o',B/'test_core.exe'])
 run([B/'test_core.exe'])
 for p in src:run(common+['-target','thumb-freestanding-eabi','-mcpu=cortex_m4','-ffreestanding','-c',p,'-o',B/(p.stem+'.o')])
 status='PASS_HOST_TESTS_AND_ARM_OBJECT_COMPILATION'
except Exception as e:status='FAILED';print(str(e),flush=True)
result={'status':status,'records':records,'scope':'Host mock callbacks and pure power policy; Cortex-M4 freestanding objects. No firmware image, SDK integration, hardware test or measured timing.','hardware_tested':False}
(B/'verification.json').write_text(json.dumps(result,indent=2),encoding='utf8')
sys.exit(0 if status.startswith('PASS') else 1)
