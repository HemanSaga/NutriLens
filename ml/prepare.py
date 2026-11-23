"""Curate India-only, non-estimated 2023 labels; connect brand/recipe duplicates."""
import collections,hashlib,json,pathlib,re
ROOT=pathlib.Path(__file__).resolve().parent
LABELS={'a':'more_favourable','b':'more_favourable','c':'intermediate','d':'less_favourable','e':'less_favourable'}
EXCLUDED={'en:alcoholic-beverages','en:baby-foods','en:baby-milks','en:dietary-supplements','en:meal-replacements','en:powdered-drinks','en:dehydrated-beverages'}
def normalise(text):return ' '.join(re.findall(r'[a-z0-9]+',str(text).lower()))
def record(p):
 tags=set(p.get('categories_tags',[]))
 if 'en:india' not in p.get('countries_tags',[]):return None,'not_india'
 if tags & EXCLUDED:return None,'excluded_category'
 category='beverage' if 'en:beverages' in tags else 'snack' if 'en:snacks' in tags else None
 if not category:return None,'out_of_scope'
 ingredients=p.get('ingredients_text_en') or p.get('ingredients_text') or ''
 text=normalise(ingredients)
 if len(text.split())<4:return None,'missing_or_short_ingredients'
 # This first model supports English ingredient text only.
 if not re.search(r'\b(sugar|water|salt|oil|flour|milk|wheat|cocoa|juice|acid|rice|oats|corn|nuts|almonds)\b',text):return None,'english_not_confirmed'
 score=p.get('nutriscore',{}).get('2023',{})
 if not score or score.get('grade') not in LABELS:return None,'missing_2023_label'
 if score.get('estimated')!=0 or score.get('nutriscore_applicable')!=1 or score.get('nutriscore_computed')!=1:return None,'estimated_or_inapplicable_label'
 if score.get('preparation')!='as_sold':return None,'not_as_sold'
 # Brand families and identical recipes are joined before splitting.
 brands=[normalise(b) for b in str(p.get('brands','')).split(',') if normalise(b)]
 return {'code':str(p.get('code','')),'name':p.get('product_name',''),'category':category,'ingredients':text,'brands':brands,'label':LABELS[score['grade']],'source_grade':score['grade'],'recipe_hash':hashlib.sha256(text.encode()).hexdigest()},None

def prepare():
 rows={};rejected=collections.Counter();raw=0
 for path in sorted((ROOT/'data/raw').glob('*.json')):
  for p in json.loads(path.read_text()).get('products',[]):
   raw+=1;r,reason=record(p)
   if r and r['code']:rows[r['code']]=r
   else:rejected[reason or 'missing_code']+=1
 rows=list(rows.values());parent=list(range(len(rows)))
 def find(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 seen={}
 for i,r in enumerate(rows):
  for key in ['recipe:'+r['recipe_hash']]+['brand:'+b for b in r['brands']]:
   if key in seen:parent[find(i)]=find(seen[key])
   else:seen[key]=i
 for i,r in enumerate(rows):r['group']=str(find(i))
 audit={'raw_rows_with_page_overlap':raw,'eligible_unique_barcodes':len(rows),'rejections':dict(rejected),'classes':dict(collections.Counter(r['label'] for r in rows)),'categories':dict(collections.Counter(r['category'] for r in rows)),'category_classes':dict(collections.Counter(r['category']+':'+r['label'] for r in rows)),'independent_groups':len(set(r['group'] for r in rows))}
 (ROOT/'data/curated.json').write_text(json.dumps(rows,indent=2))
 (ROOT.parent/'research/data-audit.json').write_text(json.dumps(audit,indent=2));print(json.dumps(audit,indent=2))
 return rows
if __name__=='__main__':prepare()
