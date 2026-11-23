import unittest
from prepare import record
class CurationTests(unittest.TestCase):
 def product(self):return {'code':'8901234567890','countries_tags':['en:india'],'categories_tags':['en:snacks'],'ingredients_text_en':'wheat flour sugar palm oil salt','brands':'Example','nutriscore':{'2023':{'grade':'c','estimated':0,'nutriscore_applicable':1,'nutriscore_computed':1,'preparation':'as_sold'}}}
 def test_only_valid_versioned_label(self):
  p=self.product();self.assertEqual(record(p)[0]['label'],'intermediate');p['nutriscore']['2023']['estimated']=1;self.assertIsNone(record(p)[0])
 def test_no_top_level_grade_fallback(self):
  p=self.product();p['nutriscore']={};p['nutriscore_grade']='a';self.assertEqual(record(p)[1],'missing_2023_label')
 def test_no_score_or_nutrients_in_features(self):
  p=self.product();p['nutriments']={'sugars_100g':25};r,_=record(p);self.assertNotIn('nutriments',r);self.assertEqual(r['ingredients'],'wheat flour sugar palm oil salt')
 def test_excludes_alcohol_and_other_markets(self):
  p=self.product();p['categories_tags']+=['en:alcoholic-beverages'];self.assertEqual(record(p)[1],'excluded_category');p=self.product();p['countries_tags']=['en:france'];self.assertEqual(record(p)[1],'not_india')
 def test_separate_beverage_category(self):
  p=self.product();p['categories_tags']=['en:beverages'];self.assertEqual(record(p)[0]['category'],'beverage')
if __name__=='__main__':unittest.main()
