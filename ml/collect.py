"""Collect public OFF snapshots; resume without re-requesting saved pages.
No health profiles, credentials or synthetic product labels are used.
"""
import argparse,datetime,hashlib,json,pathlib,subprocess,time,urllib.parse
ROOT=pathlib.Path(__file__).resolve().parent
FIELDS='code,product_name,brands,categories_tags,countries_tags,ingredients_text,ingredients_text_en,nutriscore'
def main():
 p=argparse.ArgumentParser();p.add_argument('--max-pages',type=int,default=50);a=p.parse_args()
 out=ROOT/'data/raw';out.mkdir(parents=True,exist_ok=True)
 manifest=[]
 for category in ['snacks','beverages']:
  for page in range(1,a.max_pages+1):
   path=out/f'{category}-{page:03d}.json'
   params={'countries_tags_en':'india','categories_tags_en':category,'page_size':100,'page':page,'fields':FIELDS}
   url='https://world.openfoodfacts.org/api/v2/search?'+urllib.parse.urlencode(params)
   if not path.exists():
    # API search quota: conservatively allow at most ~8 requests/minute.
    time.sleep(8)
    for attempt in range(3):
     r=subprocess.run(['curl','-fsSL','--max-time','50','-G','https://world.openfoodfacts.org/api/v2/search']+[part for key,value in params.items() for part in ['--data-urlencode',str(key)+'='+str(value)]],capture_output=True)
     try:
      data=json.loads(r.stdout)
      if r.returncode or not isinstance(data.get('products'),list):raise ValueError('Invalid response')
      path.write_bytes(r.stdout);break
     except (ValueError,KeyError):
      print(f'Request failed {category}/{page}: {r.stderr.decode()[:200]}',flush=True)
      if attempt==2:raise RuntimeError(f'Failed {category} page {page}; rerun to resume')
      time.sleep(60)
   data=json.loads(path.read_text());n=len(data['products']);total=int(data.get('count',0))
   manifest.append({'file':path.name,'url':url,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'records':n,'fetched_at':datetime.datetime.fromtimestamp(path.stat().st_mtime,datetime.timezone.utc).isoformat()})
   print(f'{category} page {page}: {n} records / {total} available',flush=True)
   (ROOT/'data/manifest.json').write_text(json.dumps({'source':'Open Food Facts','database_license':'ODbL 1.0','records_are_community_data':True,'pages':manifest},indent=2))
   if n<100 or page*100>=total:break
if __name__=='__main__':main()
