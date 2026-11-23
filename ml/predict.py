"""Local research inference; never replace measured label data with these estimates."""
import argparse,json
import joblib,numpy as np
from scipy.sparse import hstack,csr_matrix
from prepare import ROOT,normalise
from forward import probabilities

def predict(ingredients,category):
 artifact=ROOT/'artifacts/ingredient-mlp.joblib'
 if not artifact.exists():raise ValueError('No trained artifact. Run the documented collection and training steps first.')
 bundle=joblib.load(artifact) # Only load a trusted, locally trained artifact.
 text=normalise(ingredients)
 if category not in ['snack','beverage'] or len(text.split())<4:raise ValueError('Provide an in-scope category and a full English ingredient list.')
 vectorizer=bundle['vectorizer'];x=vectorizer.transform([text]);tokens=vectorizer.build_analyzer()(text);vocab=vectorizer.vocabulary_
 coverage=sum(t in vocab for t in tokens)/max(1,len(tokens))
 if x.nnz==0 or coverage<.3:return {'status':'abstained','reason':'Insufficient familiar ingredient vocabulary.','research_only':True}
 features=hstack([x,csr_matrix([[category=='snack',category=='beverage']])]).tocsr();model=bundle['model'];prob=probabilities(model,features)[0];winner=int(prob.argmax())
 # Token occlusion describes model sensitivity, not causal nutrient effects.
 changes=[]
 for token in list(dict.fromkeys(text.split()))[:60]:
  masked=' '.join(t for t in text.split() if t!=token)
  xx=hstack([vectorizer.transform([masked]),features[:,-2:]]).tocsr()
  changes.append({'term':token,'score_change_on_removal':float(prob[winner]-probabilities(model,xx)[0,winner])})
 return {'status':'experimental_prediction','research_only':True,'category':category,'predicted_source_band':bundle['classes'][winner],'uncalibrated_model_scores':dict(zip(bundle['classes'],map(float,prob))),'vocabulary_coverage':coverage,'sensitivity_terms':sorted(changes,key=lambda t:abs(t['score_change_on_removal']),reverse=True)[:5],'warning':'Not a verified nutrition grade, health percentage, safety assessment or medical recommendation. Do not use this research model to make consumer decisions.'}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--category',choices=['snack','beverage'],required=True);p.add_argument('--ingredients',required=True);a=p.parse_args()
 try:print(json.dumps(predict(a.ingredients,a.category),indent=2))
 except ValueError as e:p.exit(2,str(e)+'\n')
