import pathlib,subprocess,sys,tempfile,json,hashlib,shutil
PYTHON=pathlib.Path(sys.argv[1]).absolute()
SOURCE=pathlib.Path(__file__).absolute().parent
COMMAND=PYTHON.parent/"pgn-clock-ledger"
with tempfile.TemporaryDirectory() as td:
 work=pathlib.Path(td)
 def run(args,code=0):
  p=subprocess.run([str(COMMAND),*map(str,args)],cwd=work,text=True,capture_output=True,timeout=20)
  assert p.returncode==code,(args,p.returncode,p.stdout,p.stderr)
  if code==2:
   assert not p.stdout and p.stderr,(p.stdout,p.stderr)
   return None
  return json.loads(p.stdout)
 help_result=subprocess.run([str(COMMAND),"--help"],cwd=work,capture_output=True,text=True,timeout=10)
 assert help_result.returncode==0 and "usage:" in help_result.stdout
 installed=subprocess.run([str(PYTHON),"-I","-c","import pgn_clock_ledger,pathlib,hashlib;print(hashlib.sha256(pathlib.Path(pgn_clock_ledger.__file__).read_bytes()).hexdigest())"],cwd=work,capture_output=True,text=True,check=True).stdout.strip()
 assert installed==hashlib.sha256((SOURCE/"pgn_clock_ledger.py").read_bytes()).hexdigest()
 for p in SOURCE.glob("example.*"):shutil.copyfile(p,work/p.name)
 r=run(['example.pgn']);assert [p['elapsed_millis'] for p in r['plies']]==[3000,2000,3000,5000]
 assert r['known_elapsed_totals_millis']=={'white':6000,'black':7000}
 text=(work/'example.pgn').read_text();(work/'missing.pgn').write_text(text.replace('{[%clk 0:04:59]}',''))
 m=run(['missing.pgn'],1);assert m['plies'][0]['elapsed_millis'] is None and m['plies'][2]['status']=='prior_clock_missing'
 (work/'bad.pgn').write_text(text.replace('300+2','40/7200:3600'));run(['bad.pgn'],2)
 (work/'large.pgn').write_bytes(b' '*(128*1024+1));run(['large.pgn'],2)
print(json.dumps({"installed_command":"pgn-clock-ledger","outside_checkout":True,"source_identity_matched":True,"contract_checks":"passed"}))
