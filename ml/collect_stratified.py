"""Supplement the pilot by category/grade strata; NOT a prevalence sample."""
import datetime,hashlib,json,pathlib,subprocess,time,urllib.parse
from collect import ROOT,FIELDS
out=ROOT/'data/raw';out.mkdir(parents=True,exist_ok=True);manifest=[];failures=[]
for category in ['snacks','beverages']:
 for grade in ['a|b','c','d|e']:
  params={'countries_tags_en':'india','categories_tags_en':category,'nutrition_grades_tags':grade,'page_size':100,'page':1,'fields':FIELDS}
  path=out/f'{category}-stratum-{grade.replace("|","")}.json'
  if not path.exists():
   time.sleep(8)
   args=['curl','-fsSL','--max-time','45','-G','https://world.openfoodfacts.org/api/v2/search']+[v for k,val in params.items() for v in ['--data-urlencode',str(k)+'='+str(val)]]
   r=subprocess.run(args,capture_output=True)
   try:
    data=json.loads(r.stdout)
    if r.returncode or not isinstance(data.get('products'),list):raise ValueError()
    path.write_bytes(r.stdout)
   except ValueError:
    failures.append({'category':category,'grade':grade,'error':r.stderr.decode()[:200]});print('Failed',category,grade,flush=True);continue
  data=json.loads(path.read_text());print(category,grade,len(data['products']),'of',data.get('count'),flush=True)
  manifest.append({'file':path.name,'url':'https://world.openfoodfacts.org/api/v2/search?'+urllib.parse.urlencode(params),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'fetched_at':datetime.datetime.fromtimestamp(path.stat().st_mtime,datetime.timezone.utc).isoformat(),'available_in_stratum':data.get('count')})
(ROOT/'data/stratified-manifest.json').write_text(json.dumps({'source':'Open Food Facts','sampling':'Up to 100 per category/grade stratum; not a prevalence estimate','database_license':'ODbL 1.0','pages':manifest,'failures':failures},indent=2))
